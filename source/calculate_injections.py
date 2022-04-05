"""James Gardner, April 2022
generates and saves injections results as .npy"""
from basic_benchmarking import * # also loads numpy and gwbench's injection module
from useful_functions import without_rows_w_nan, parallel_map, logarithmically_uniform_sample
from network_subclass import NetworkExtended
from results_class import InjectionResults

from gwbench.basic_relations import f_isco_Msolar

def save_benchmark_from_generated_injections(net, redshift_bins, mass_dict, spin_dict, redshifted, base_params, deriv_symbs_string, coeff_fisco, conv_cos, conv_log, use_rot, only_net, numerical_over_symbolic_derivs, numerical_deriv_settings, data_path=None, file_name=None, parallel=True, log_uniformly_sampled_redshift=True):
    """given an extended network (with attributes: science_case, tecs, num_injs, file_tag) and variables, generate injections, benchmark, and save results (snr, errors in logM logDL eta iota, sky area) as .npy.
    to-do: tidy up number of arguments, e.g. into kwargs for network, kwargs for benchmarking"""
    # injection and benchmarking
    # concatenate injection data from different bins
    inj_data = np.empty((len(redshift_bins)*net.num_injs, 14))
    for i, (zmin, zmax, seed) in enumerate(redshift_bins):
        cosmo_dict = dict(sampler='uniform', zmin=zmin, zmax=zmax)
        # transposed array to get [[Mc0, eta0, ..., z0], [Mc1, eta1, ..., z1], ...] from [Mc, eta, chi1x, chi1y, chi1z, chi2x, chi2y, chi2z, DL, iota, ra, dec, psi, z]    
        injection_params = np.array(injections.injections_CBC_params_redshift(cosmo_dict, mass_dict, spin_dict, redshifted, num_injs=net.num_injs, seed=seed))
        # changing z to logarithmically uniformly sampled, DL and the redshifted Mc change accordingly
        if log_uniformly_sampled_redshift:
            # produces numerical transverse artefacts in population 
#             from scipy.stats import loguniform; z_vec = loguniform.rvs(zmin, zmax, size=net.num_injs)
            # to-do: see if numpy method does not produce artefacts
            z_vec = logarithmically_uniform_sample(zmin, zmax, net.num_injs, seed=seed)
            DL_vec = Planck18.luminosity_distance(z_vec).value
            if redshifted:
                # undo existing shift from z's, then apply new shift to Mc
                injection_params[0] = injection_params[0]*(1. + z_vec)/(1. + injection_params[13])
            injection_params[8] = DL_vec
            injection_params[13] = z_vec
        inj_data[i*net.num_injs:(i + 1)*net.num_injs] = injection_params.transpose()

    def calculate_benchmark_from_injection(inj):
        """given a 14-array of [Mc, eta, chi1x, chi1y, chi1z, chi2x, chi2y, chi2z, DL, iota, ra, dec, psi, z],
        returns a 7-tuple of the
        * redshift z,
        * integrated snr,
        * fractional Mc and DL and absolute eta and iota errors,
        * 90% sky area.
        sigma_log(Mc) = sigma_Mc/Mc is fractional error in Mc and similarly for DL, sigma_eta is absolute,
        while |sigma_cos(iota)| = |sigma_iota*sin(iota)| --> error in iota requires rescaling from output.
        if something goes wrong with the injection, then (z, *np.full(6, np.nan)) will be returned
        to-do: rewrite this without requiring an inner function"""
        varied_keys = ['Mc', 'eta', 'chi1x', 'chi1y', 'chi1z', 'chi2x', 'chi2y', 'chi2z', 'DL', 'iota', 'ra', 'dec', 'psi', 'z']
        varied_params = dict(zip(varied_keys, inj))
        z = varied_params.pop('z')
        Mc, eta, iota = varied_params['Mc'], varied_params['eta'], varied_params['iota']
        output_if_injection_fails = (z, *np.full(6, np.nan))
        
        Mtot = Mc/eta**0.6
        # fisco_obs = (6**1.5*PI*(1+z)*Mtot)**-1 # with the mass redshifted by (1+z) in the observer frame (not clear in B&S2022), missing some number of Msun, c=1, G=1 factors
        fisco_obs = f_isco_Msolar((1 + z)*Mtot) #4.4/Mtot*1e3 # Hz # from https://arxiv.org/pdf/2011.05145.pdf
        # chosing fmax in 11 <= coeff_fisco*fisco <= 1024, truncating to boundary values, NB: B&S2022 doesn't include the lower bound which must be included to avoid an IndexError with the automatically truncated fmin from the V+ and aLIGO curves stored in gwbench that start at 10 Hz, this can occur for Mtot > 3520 Msun with massive BBH mergers although those masses are at least an order of magnitude beyond any observed so far
        fmin, fmax = 5., coeff_fisco*fisco_obs
        # lower bound on fmax can be anything greater than f_lowest_allowed_by_PSD + 1/16     
        # from hardcoded PSDs, if aLIGO or V+ (everything else), then threshold fmax >= 11 (6) Hz; fmax is $f_U$ in B&S2022
        are_aLIGO_or_Vplus_used_bool = ('aLIGO' in net.tecs) or ('V+' in net.tecs)
        if are_aLIGO_or_Vplus_used_bool:
            fmax_bounds = (11, 1024)
        else:
            fmax_bounds = (6, 1024)
        fmax = float(max(min(fmax, fmax_bounds[1]), fmax_bounds[0]))            
        # if BBH, then discard the injection by returning NaNs if fmax < 12 Hz (7 Hz) for aLIGO or V+ (everything else)
        if net.science_case == 'BBH':
            if are_aLIGO_or_Vplus_used_bool and (fmax < 12):
                return output_if_injection_fails
            elif (not are_aLIGO_or_Vplus_used_bool) and (fmax < 7):
                return output_if_injection_fails
        # df linearly transitions from 1/16 (fine from B&S2022) to 10 (coarse to save computation time) Hz
        df = (fmax - fmax_bounds[0])/(fmax_bounds[1] - fmax_bounds[0])*10 + (fmax_bounds[1] - fmax)/(fmax_bounds[1] - fmax_bounds[0])*1/16
        f = np.arange(fmin, fmax, df)
        
        # net_copy is automatically deleted once out of scope (is copying necessary with Pool()?)
        net_copy = deepcopy(net)
        inj_params = dict(**base_params, **varied_params)
        net_copy.set_net_vars(f=f, inj_params=inj_params, deriv_symbs_string=deriv_symbs_string, conv_cos=conv_cos, conv_log=conv_log, use_rot=use_rot)

        basic_network_benchmarking(net_copy, numerical_over_symbolic_derivs=numerical_over_symbolic_derivs, only_net=only_net, numerical_deriv_settings=numerical_deriv_settings, hide_prints=True)

        if net_copy.wc_fisher:
            # convert sigma_cos(iota) into sigma_iota
            abs_err_iota = abs(net_copy.errs['cos_iota']/np.sin(iota))
            return (z, net_copy.snr, net_copy.errs['log_Mc'], net_copy.errs['log_DL'], net_copy.errs['eta'],
                    abs_err_iota, net_copy.errs['sky_area_90'])
        else:
            return output_if_injection_fails

    # calculate results: z, snr, errs (logMc, logDL, eta, iota), sky area
    # p_umap is unordered in redshift for greater speed (check)
    results = np.array(parallel_map(calculate_benchmark_from_injection, inj_data, num_cpus=os.cpu_count() - 1, unordered=True, parallel=parallel))
    # filter out NaNs
    results = without_rows_w_nan(results)
    if len(results) == 0:
        raise ValueError('All calculated values are NaN, FIM is ill-conditioned.')
    if data_path is None:
        data_path = net.data_path
    if file_name is None:
        file_name = net.file_name
    np.save(data_path + file_name, results)   
    
def detection_rate_for_network_and_waveform(network_spec, science_case, wf_model_name, wf_other_var_dic, num_injs, generate_fig=True, show_fig=True, print_progress=True, print_reach=True, data_path='/fred/oz209/jgardner/CEonlyPony/source/data_redshift_snr_errs_sky-area/', file_name=None, parallel=True, use_BS2022_seeds=False):
    """initialises network, benchmarks against injections, calculates efficiency and detection rate, plots.
    use case: Replicating Borhanian and Sathya 2022 (B&S2022) injections and detection rates"""
    # initialisation
    locs = [x.split('_')[-1] for x in network_spec]
    net = NetworkExtended(network_spec, science_case, wf_model_name, wf_other_var_dic, num_injs, data_path=data_path)
    net.set_wf_vars(wf_model_name=net.wf_model_name, wf_other_var_dic=net.wf_other_var_dic)
    
    if net.science_case == 'BNS':
        # injection settings - source
        mass_dict = dict(dist='gaussian', mean=1.35, sigma=0.15, mmin=1, mmax=2)
        spin_dict = dict(geom='cartesian', dim=1, chi_lo=-0.05, chi_hi=0.05)
        # redshift_bins = ((zmin, zmax, seed), ...) (use same seeds from B&S2022 to replicate results)
        # typo in AppA that starts at 0 rather than 0.02 (in main text)?
        redshift_bins = ((0.02, 0.5, 7669), (0.5, 1, 3103), (1, 2, 4431), (2, 4, 5526), (4, 10, 7035), (10, 50, 2785))
        coeff_fisco = 4 # fmax = 4*fisco for BNS, 8*fisco for BBH
    elif net.science_case == 'BBH':
        # following injection.py and GWTC-2 (AppB.2. Power Law + Peak mass model), to-do: update for GWTC-3?
        # m1 follows power peak, m2 follow uniform in (5 Msun, m1) --> change mmin to 5?
        mass_dict = dict(
            dist='power_peak_uniform',
            mmin       = 5, # 4.59 in GWTC-2, but changing to 5 here to get m2 in correct range
            mmax       = 86.22,
            m1_alpha   = 2.63,
            q_beta     = 1.26,
            peak_frac  = 0.1,
            peak_mean  = 33.07, # assuming that peak_mu is peak_mean?
            peak_sigma = 5.69,
            delta_m    = 4.82,
        )
        spin_dict = dict(geom='cartesian', dim=1, chi_lo=-0.75, chi_hi=0.75)
        redshift_bins = ((0.02, 0.5, 5485), (0.5, 1, 1054), (1, 2, 46), (2, 4, 5553), (4, 10, 5998), (10, 50, 4743))
        coeff_fisco = 8
    else:
        raise ValueError('Science case not recognised.')
    # when embarrassingly parallelising, each task (e.g. out of 30) should not have the same seeds when they generate their (e.g. 1000) injections
    if not use_BS2022_seeds:
        redshift_bins = tuple((zbin[0], zbin[1], None) for zbin in redshift_bins)
        
    base_params = {
        'tc':    0,
        'phic':  0,
        'gmst0': 0, # assume zero given B2021
        # B&S2022 uses tidal waveforms but turns tides off
        # these can be calculated if m1, m2, Love number, and EoS (i.e. radii) known
        'lam_t': 0, # combined dimensionless tidal deformability
        'delta_lam_t': 0,
    }

    # derivative settings
    # assign with respect to which parameters to take derivatives for the FIM
    deriv_symbs_string = 'Mc eta DL tc phic iota ra dec psi'
    # assign which parameters to convert to log or cos versions for differentiation
    conv_cos = ('dec', 'iota')
    conv_log = ('Mc', 'DL', 'lam_t')

    # network settings: whether to include Earth's rotation and individual detector calculations
    use_rot = 1
    only_net = 1

    # injection settings - other: number of injections per redshift bin (over 6 bins)
    # to-do: refactor file_tag generation
    redshifted = 1 # whether sample masses already redshifted wrt z
     
    if print_progress: print('Network initialised.')
    # use symbolic derivatives if able
    if (wf_model_name == 'tf2') | (wf_model_name == 'tf2_tidal'):
        numerical_over_symbolic_derivs = False    
        generate_symbolic_derivatives(wf_model_name, wf_other_var_dic, deriv_symbs_string, locs, use_rot, print_progress=print_progress)
        numerical_deriv_settings = None
    else:
        numerical_over_symbolic_derivs = True
        numerical_deriv_settings = dict(step=1e-9, method='central', order=2, n=1) # default
       
    # ------------------------------------------------
    # generate results or skip if previously generated successfully (i.e. not ill-conditioned)   
    if not net.results_file_exists:
        save_benchmark_from_generated_injections(net, redshift_bins, mass_dict, spin_dict, redshifted, base_params, deriv_symbs_string, coeff_fisco, conv_cos, conv_log, use_rot, only_net, numerical_over_symbolic_derivs, numerical_deriv_settings, data_path=net.data_path, file_name=net.file_name, parallel=parallel)
    else:
        if (not generate_fig) & print_progress:
            print('Results already exist; figure not (re)generated.')
            # to-do: increase efficiency by making this check sooner? this case seems unlikely.
            return

    if generate_fig:
        results = InjectionResults(net.file_name_with_path)
        if print_progress: print('Results found and loaded.')

        # ------------------------------------------------
        # calculting efficiency and detection rate for plotting
        results.calculate_and_set_detection_rate(print_reach=print_reach)
        if print_progress: print('Detection rate defined, now calculating...')
        
        # ------------------------------------------------
        # plotting
        results.plot_detection_rate(show_fig=show_fig, print_progress=print_progress, parallel=parallel)
