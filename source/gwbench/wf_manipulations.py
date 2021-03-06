# Copyright (C) 2020  Ssohrab Borhanian
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import numpy as np

#-----get amp/pha for pl and cr polarizations (since they are complex)-----
def transform_hfpc_to_amp_pha(hfpc, f, params_list):
    hfp, hfc = hfpc(f, *params_list)
    return wfm.pl_cr_to_amp_pha(hfp, hfc)

def pl_cr_to_amp_pha(hfp, hfc):
    hfp_amp, hfp_pha = amp_pha_from_z(hfp)
    hfc_amp, hfc_pha = amp_pha_from_z(hfc)
    return hfp_amp, hfp_pha, hfc_amp, hfc_pha

#-----convert amp/phase derivatives to re/im ones-----
def z_deriv_from_amp_pha(amp,pha,del_amp,del_pha):
    del_z = np.zeros(del_amp.shape,dtype=np.complex_)
    if len(del_amp.shape) == 2:
        for i in range(del_amp.shape[1]):
            del_z[:,i] = del_amp[:,i] * np.exp(1j*pha) + amp * np.exp(1j*pha) * 1j * del_pha[:,i]
        return del_z
    else:
        return del_amp * np.exp(1j*pha) + amp * np.exp(1j*pha) * 1j * del_pha

#-----re/im vs. amp/phase transformations-----
def re_im_from_amp_pha(amp,pha):
    return re_im_from_z(z_from_amp_pha(amp,pha))

def amp_pha_from_re_im(re,im):
    return amp_pha_from_z(z_from_re_im(re,im))

#-----re/im or amp/phase vs. complex number transformations-----
def re_im_from_z(z):
    return np.real(z), np.imag(z)

def z_from_re_im(re,im):
    return re + 1j * im

def amp_pha_from_z(z):
    return np.abs(z), np.unwrap(np.angle(z))

def z_from_amp_pha(amp,pha):
    return amp * np.exp(1j*pha)
