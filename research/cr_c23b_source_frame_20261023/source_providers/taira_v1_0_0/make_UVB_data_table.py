"""
Reformats cloudy data to match : Faucher-Giguere 2009,
Faucher-Giguere 2020, Haardt and Madau 2012, and Puchwein et al. 2019 for
redshifts ~0-10. All intensities the same units of erg/s/cm**2.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps
import pandas as pd
import unyt as u
import argparse
import os

def read_cloudy_in(file):
    """
    Reads in CLOUDY input files as pandas Data Frames

    args:

        file (str) - path to CLOUDY input file
    
    returns:

        df (Data Frame): the read in / formatted data file
    """
    df = pd.read_csv(file,
                     header = None,
                    skiprows = 5,
                    skipfooter = 3,
                    delim_whitespace = True)
    
    df = df.drop(columns = 0)
    
    for i in range(len(df[1])):
        df[1][i] = float(df[1][i].replace(")","").replace("(",""))
        df[2][i] = float(df[2][i].replace(")","").replace("(",""))
    
    return df

# reading in arguments
parser = argparse.ArgumentParser(description = "Generate SALSA data from trident rays")

parser.add_argument('-out_path', action='store', 
                    required=False, dest='out_path', 
                    help='Path to UVB file',
                    default="./data_table_example/")

parser.add_argument('-uvb_names', action='store', 
                    required=False, dest='uvb_name', 
                    help='Label to assigned to uvb.',
                    default="FG09 FG20 HM12 PW19")

parser.add_argument('-uvb_paths', action='store', 
                    required=False, dest='uvb_paths', 
                    help='Paths to UVB data',
                    default="./cloudy_formatted_data/fg09 ./cloudy_formatted_data/fg20 ./cloudy_formatted_data/hm12 ./cloudy_formatted_data/pw19")

args = parser.parse_args()

uvb_names = args.uvb_name.split(" ")
uvb_paths = args.uvb_paths.split(" ")
out_dir = args.out_path

# checking for output table
# out_dir = "/mnt/scratch/tairaeli/UVB_data_table/"
if os.path.exists(out_dir) == False:
    os.mkdir(out_dir)

# making uvb dirs
for name in uvb_names:
    if os.path.exists(out_dir+name) == False:
        os.mkdir(out_dir+name)

# processing fg09 data
fg09_dir = uvb_paths[0]


for filename in os.listdir(fg09_dir):
    rs = 999
    if filename.endswith(".dat"):
        try:
            rs = float(filename[-8:-4])
        except(ValueError):
            rs = float(filename[-7:-4])
        
        fg09_temp = pd.read_csv(fg09_dir+"/"+filename,
                     skiprows=2,delimiter="   ",
                     header=None)
        fg09_ev = fg09_temp[0]*13.605703976
        fg09_int = ((fg09_ev.to_list()*u.eV).to("J")/(u.h)).to_value()
        fg09_int = (fg09_temp[1]*10**(-21))*4*np.pi*fg09_int
        fg09 = pd.DataFrame({"E (eV)":fg09_ev,
                             "I (erg/s/cm**2)":fg09_int})

        assert rs != 999, "filename processing failed"
        
        n1 = rs//1
        n2= rs%1
        n2 = f"{n2:.6f}"[2:]
        
        fg09.to_csv(out_dir+f"{uvb_names[0]}/z_{int(n1):02}"+"."+f"{n2}.csv")
        print("OUT:",f"{uvb_names[0]}/z_{int(n1):02}"+"."+f"{n2}.csv")

n=0
if not os.listdir(fg09_dir)[0].endswith(".dat"):
    n=1

dir_list = uvb_paths[(1-n):]
for i,dir_loc in enumerate(dir_list):
    for filename in os.listdir(dir_loc):
        rs = 999
        if filename.endswith(".out"):
            rs = float(filename[-14:-4])

            uvb = read_cloudy_in(dir_loc+"/"+filename)
            uvb[1] = uvb[1]*13.605703976
            uvb[3] = ((uvb[1].to_list()*u.eV).to("J")/(u.h)).to_value()
            uvb[4] = (10**uvb[2])*4*np.pi*uvb[3]
            
            out_df = pd.DataFrame({"E (eV)":uvb[1],
                                "I (erg/s/cm**2)":uvb[4]})

            assert rs != 999, "filename processing failed"
            
            n1 = rs//1
            n2= rs%1
            n2 = f"{n2:.6f}"[2:]
            
            out_df.to_csv(out_dir+f"{uvb_names[i+1-n]}/z_{int(n1):02}"+"."+f"{n2}.csv")
            print("OUT:",f"{uvb_names[i+1-n]}/z_{int(n1):02}"+"."+f"{n2}.csv")
