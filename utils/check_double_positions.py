import sys
import pandas   as pd
from   glob import glob

try:
    path = sys.argv[1]
    print(f"\nAnalyzing {path} \n")    
except IndexError:
    print("\nUsage:   check_double_positions.py <path_name>\n")
    sys.exit()


for iFileName in glob(path + '/*.h5'):

    sns_positions = pd.read_hdf(iFileName, "/MC/sns_positions")

    if len(sns_positions) == len(sns_positions.sensor_id.unique()):
        #print(f"{iFileName} ... OK")
        pass
    else:
        print(f"{iFileName} ... ERROR: Sensor duplicated positions")

print()