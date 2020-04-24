import os

from typing import List
from typing import Tuple
from typing import Dict

from math   import sqrt

# Specific IC stuff
import invisible_cities.core.system_of_units  as units



###
# Ideally to be read from the DataBase if this info is stored there.
def get_detector_dimensions(det_name : str
                           )        -> Dict :
    dimensions = {
        'NEXT_NEW': {
            'ACTIVE_radius' : 208.0 * units.mm,
            'ACTIVE_length' : 532.0 * units.mm
        },

        'NEXT100': {
            'ACTIVE_radius' :  492.0 * units.mm,
            'ACTIVE_length' : 1160.0 * units.mm
        },

        'NEXT_FLEX': {
            'ACTIVE_radius' :  496.0 * units.mm,
            'ACTIVE_length' : 1160.0 * units.mm
        }
    }
    
    return dimensions[det_name]



###
def get_table_positions(det_name   : str,
                        table_type : str,
                        pitch      : Tuple[float, float, float]
                       )          -> List[Tuple[float, float, float]] :
    
    # Getting detector dimensions
    det_dim = get_detector_dimensions(det_name)
    det_rad = int(det_dim["ACTIVE_radius"])
    det_len = int(det_dim["ACTIVE_length"])
    
    # Getting table pitch
    pitch_x = int(pitch[0])
    pitch_y = int(pitch[1])
    pitch_z = int(pitch[2])
    
    # Generating positions
    positions = []
    for i in range(-det_rad, det_rad, pitch_x):
        for j in range(-det_rad, det_rad, pitch_y):
            # Checking if corrent point fits into ACTIVE
            pos_rad = sqrt(i**2 + j**2)
            if (pos_rad < det_rad):
                # Generating S2 table
                if table_type == "S2":
                    positions.append((i, j, 0))
                
                # Generating S1 table
                else:
                    for k in range(0, det_len, pitch_z):
                        positions.append((i, j, k))
            
    return positions



###
def get_host_name() -> str :

    local_host = os.uname()[1]

    my_host = "local"
    if    "majorana"  in local_host: my_host = "majorana"
    elif  "neutrinos" in local_host: my_host = "neutrinos"
    elif  "harvard"   in local_host: my_host = "harvard"

    return my_host



###
def get_working_paths(det_name : str
                     )        -> Tuple[str, str, str, str] :

    # Getting local host
    host = get_host_name()

    # Setting base PATH
    if host == "local":
        base_path = f"/Users/Javi/Development/NextLightTable/data/{det_name}/"

    elif host == "majorana":
        base_path = f"/home/jmunoz/Development/NextLightTable/data/{det_name}/"

    elif host == "neutrinos":
        base_path = f"./NextLightTable/data/{det_name}/"

    elif host == "harvard":
        base_path = f"/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/NextLightTable/data/{det_name}/"

    else:
        print("get_working_paths::Not valid host name.")
        exit(0)

    if not os.path.isdir(base_path): os.makedirs(base_path)

    # Making working PATHs
    config_path = base_path + 'config/'
    if not os.path.isdir(config_path): os.makedirs(config_path)

    log_path = base_path    + 'log/'
    if not os.path.isdir(log_path): os.makedirs(log_path)

    dst_path = base_path    + 'dst/'
    if not os.path.isdir(dst_path): os.makedirs(dst_path)

    table_path = base_path  + 'table/'
    if not os.path.isdir(table_path): os.makedirs(table_path)

    return config_path, log_path, dst_path, table_path

