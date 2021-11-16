import matplotlib.pyplot as plt
import numpy as np
import healpy as hp
import os
import bilby as bby
from astropy.io import fits
from ligo.skymap.tool import ArgumentParser, FileType, register_to_xmldoc
from argparse import SUPPRESS
import lal
from ligo.skymap.io.fits import read_sky_map
import argparse
import json

def get_loc_area(ra_input,dec_input):
    #give a ra in (-180, 180), and dec in (-90,90) 
    ra_0=float('{:.2f}'.format(ra_input))
    dec_0=float('{:.2f}'.format(dec_input))

    ra_dg=np.rad2deg(float('{:.2f}'.format(ra_0)))
    dec_dg=np.rad2deg(float('{:.2f}'.format(dec_0)))

    print(ra_0,dec_0,"  ",ra_dg,dec_dg)
    
    os.system("lalapps_inspinj \
`# Write output to inj.xml.` \
-o inj_{}_{}_100mpc.xml \
`# Mass injection.` \
`# In this example, the masses are pinned to 1.5 and 1.8 Msun.` \
--m-distr fixMasses --fixed-mass1 1.50046 --fixed-mass2 1.80128 \
`# sky location injection.` \
--l-distr fixed --longitude {} --latitude {} \
`# Distance distribution: uniform in Euclidean volume.` \
`# WARNING: distances are in kpc.` \
--d-distr volume \
--min-distance 100000 --max-distance 100000 \
`# Coalescence time distribution: adjust time step, start, and stop` \
`# polarization` \
--polarization  0 \
`# Inclination angle` \
--i-distr  fixed --fixed-inc 40 \
`# phase` \
--fixed-coa-phase 57.295 \
`# time to control the number of injections.` \
--time-step 7200 \
--gps-start-time 1264079176 \
--gps-end-time 1264069576 \
`# Distance distribution: uniform in Euclidean volume.` \
`# Write a table of CBC injections to inj.xml.` \
--f-lower 20 --disable-spin \
--waveform TaylorF2threePointFivePN".format(ra_0,dec_0,ra_dg,dec_dg))

    print("#1")

    os.system("bayestar-realize-coincs \
`# Write output to coinc.xml.` \
-o coinc_{}_{}_100mpc.xml \
`# Use the injections and noise PSDs that we generated.` \
inj_{}_{}_100mpc.xml --reference-psd correct_psd.xml \
`# Specify which detectors are in science mode.` \
--detector H1 L1 V1 \
`# Optionally, add Gaussian noise (rather than zero noise).` \
--measurement-error gaussian-noise \
`# Optionally, adjust the detection threshold: single-detector` \
`# SNR, network SNR, and minimum number of detectors above` \
`# threshold to form a coincidence.` \
--snr-threshold 4.0 \
--net-snr-threshold 12.0 \
--min-triggers 2 \
`# Optionally, save triggers that were below the single-detector` \
`# threshold.` \
--keep-subthreshold".format(ra_0,dec_0,ra_0,dec_0))

    print("#2")

    os.system("bayestar-localize-coincs coinc_{}_{}_100mpc.xml".format(ra_0, dec_0))

    print("#3")

    os.system("mv 0.fits skymap_{}_{}_100mpc.fits".format(ra_0,dec_0))

    print("#4")

    os.system("ligo-skymap-plot skymap_{}_{}_100mpc.fits -o skymap_{}_{}_100mpc.png --annotate --contour 50 90".format(ra_0,dec_0,ra_0,dec_0))

    print("#5")
    
    
    
    
    hpdata, header = read_sky_map("skymap_{}_{}_100mpc.fits".format(ra_0,dec_0))
    interval=np.arange(0,1,0.00000001)
    
    
    res=0.5
    res_indexs=np.where(hpdata>res)[0]
    percent=sum(hpdata[res_indexs])

    bounds=[0,len(interval)-1]
    location=np.floor(len(interval)/2)

    while np.abs(percent-0.9)>0.0000001:
        if (percent-0.9)<0:
            bounds[1]=location
            location=int(np.floor(sum(bounds)/2))        
            res=interval[location]
        else:
            bounds[0]=location
            location=int(np.ceil(sum(bounds)/2)) 
            res=interval[location]

        res_indexs=np.where(hpdata>res)[0]
        percent=sum(hpdata[res_indexs])
        print(res,bounds,percent, location)
    
        if (bounds[1]-bounds[0]==1):
            break

    print(res,percent)
    
    
    npix=len(hpdata)
    nside=hp.npix2nside(npix)

    N=len(res_indexs)
    A=hp.nside2pixarea(nside, degrees = True)

    return N*A

    
if __name__=="__main__":
     
    parser = argparse.ArgumentParser()
    parser.add_argument('--ra', type=float)
    parser.add_argument('--dec', type=float)
    parser.add_argument('--N', type=float)
    args = parser.parse_args()

    os.chdir("bayestar_runs")
    os.mkdir("bayestar_{}_{}".format(args.ra,args.dec))
    os.chdir("bayestar_{}_{}".format(args.ra,args.dec))
    os.system("cp ../../correct_psd.xml .")
    
    print("measuring {}_{}...".format(args.ra,args.dec)) 
    area=get_loc_area(2*np.pi*args.ra/args.N-np.pi, np.pi*args.dec/args.N-np.pi/2)
    
    print("dumping {}_{}...".format(args.ra,args.dec))
    key_ra_dec=str(args.ra)+"_"+str(args.dec)
    area_dic={key_ra_dec : area}
    with open("../../json_dump/{}_{}.json".format(args.ra,args.dec), "w") as f:
        json.dump(area_dic, f, indent=2, sort_keys=True)
    
    os.chdir("../")
    print("done!")
