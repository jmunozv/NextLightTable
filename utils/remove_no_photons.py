# General Importings
import os
import sys
import pandas   as pd
from   glob import glob

try:
    path = sys.argv[1]
    print(f"\nAnalyzing {path} \n")    
except IndexError:
    print("\nUsage:   remove_no_photons.py <path_name>\n")
    sys.exit()


for file in glob(path + '*'):
    mcConfig = pd.read_hdf(file, 'MC/configuration')
    mcConfig.set_index("param_key", inplace = True)
    try :
        num_photons_event = int(mcConfig.at["/Generator/ScintGenerator/nphotons" , "param_value"])
        print(file)
    except KeyError:
        print(f"{file} has no photons info. Removing ...")
        os.remove(path + file)

print()