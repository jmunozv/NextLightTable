import os

import numpy      as np
import pandas     as pd
from   typing import Tuple

# Specific IC stuff
from invisible_cities.io.mcinfo_io import load_mcsensor_response_df
from invisible_cities.io.mcinfo_io import get_sensor_types

# Specific LightTable stuff
from sim_functions     import get_num_photons
from general_functions import get_host_name
from pos_functions     import get_energy_table_positions
from pos_functions     import get_tracking_table_positions

from detectors         import get_detector_dimensions



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



###
def get_table_fname(det_name    : str,
                    table_type  : str,
                    signal_type : str,
                    sensor_name : str
                   )           -> str :
    return f"{det_name}.{table_type}.{signal_type}.{sensor_name}.LightTable.h5"



###
def get_fnames(det_name : str,
               pos      : Tuple[float, float, float]
              )        -> Tuple[str, str, str, str] :
    
    config_path, log_path, dst_path, table_path = get_working_paths(det_name)
    
    base_fname =  f"{det_name}.x_{pos[0]}.y_{pos[1]}.z_{pos[2]}"
    
    init_fname   = config_path + base_fname + ".init"
    config_fname = config_path + base_fname + ".config"
    log_fname    = log_path    + base_fname + ".log"
    dst_fname    = dst_path    + base_fname + ".next"
  
    return init_fname, config_fname, log_fname, dst_fname






###
def build_energy_table(det_name, signal_type, sensor_name, pitch):
    
    table_positions = get_energy_table_positions(det_name, signal_type, pitch)
    
    # Initial list to be filled with data.
    _, _, _, dst_fname = get_fnames(det_name, table_positions[0])
    sensor_types = get_sensor_types(dst_fname + ".h5")

    sensor_ids = sensor_types[sensor_types.sensor_name == sensor_name].sensor_id.tolist()
    sensor_ids.sort()

    light_table_columns = np.append(['x', 'y', 'z'], np.append(sensor_ids, 'total'))
    light_table_data    = []
    
    # Getting the table data from sims
    for pos in table_positions:
    
        print(f"\n* Getting data from {det_name} - {pos} ...")

        # Getting the right DST file name
        _, _, _, dst_fname = get_fnames(det_name ,pos)
        dst_fname += ".h5"

        if os.path.isfile(dst_fname):
    
            # Getting the number of photons from the file, as it could be different
            # from the one included in the setup.
            num_photons = get_num_photons(dst_fname)
            print(f"  Simulation run with {num_photons:9} initial photons.")

            # Getting the sensor response of the sns_type requested
            sns_response = load_mcsensor_response_df(dst_fname)
            sns_response = sns_response.loc[pd.IndexSlice[:,sensor_ids], :]
            sns_charge   = sns_response.groupby('sensor_id').charge.sum().tolist()
            sns_charge   = np.divide(sns_charge, num_photons)
            sns_charge   = np.append(sns_charge, sum(sns_charge))
        
            # Composing & storing this position data
            pos_data = np.append([pos[0], pos[1], pos[2]], sns_charge)
            light_table_data.append(pos_data)
            
            # Verbosity
            #print(f"  {sns_type} behaviour: {sns_response.charge.describe()}")
    
        # If the DST file does NOT EXIST
        else:
            print(f"  WARNING: {dst_fname} NOT exist.")
    
    
    # Building the LightTable DataFrame
    light_table = pd.DataFrame(light_table_data, columns = light_table_columns)

    # Setting indices
    if(signal_type == 'S1'):
        light_table.set_index(['x', 'y', 'z'], inplace = True)
    else:
        light_table.drop(columns='z', inplace = True)
        light_table.set_index(['x', 'y'], inplace = True)

    light_table.sort_index() # Not sure if needed to speed access

    light_table = light_table.rename(columns = lambda name: sensor_name + '_' + name)

    return light_table



###
def build_tracking_table(det_name, signal_type, sensor_name, pitch, tracking_maxDist):

    table_positions = get_tracking_table_positions(det_name, pitch, tracking_maxDist)

    # Getting needed data
    det_dim         = get_detector_dimensions(det_name)
    sns_id, sns_pos = det_dim["ref_sensor"]

    sns_pos_x = sns_pos[0]
    pitch_z   = pitch[2]    
    
    # Initial list to be filled with data.
    dist_xys = list(set((pos[0] - sns_pos_x)  for pos in table_positions))
    zs       = list(set((pos[2] - pitch_z/2.) for pos in table_positions))
    dist_xys.sort()
    zs      .sort(reverse=True)

    light_table_columns = ['dist_xy'] + ['z_m' + str(int(-z)) for z in zs]
    light_table_probs   = np.zeros((len(dist_xys), len(zs)))

    # Getting the table data from sims
    for pos in table_positions:

        dist = pos[0] - sns_pos_x
        z    = pos[2] - pitch_z/2.
        print(f"\n* Getting data from {det_name} - Distance {dist} mm - Z = {z} mm ...")
    
        # Getting the right DST file name
        _, _, _, dst_fname = get_fnames(det_name ,pos)
        dst_fname += ".h5"
        print(f"  {dst_fname}")

        if os.path.isfile(dst_fname):
            
            # Getting the number of photons from the file, as it could be different
            # from the one included in the setup.
            num_photons = get_num_photons(dst_fname)
            print(f"  Simulation run with {num_photons:9} initial photons.")

            # Getting the sensor response of the sns_type requested
            sns_response = load_mcsensor_response_df(dst_fname)
            try:
                sns_charge   = sns_response.loc[pd.IndexSlice[:, sns_id], 'charge'].sum()
            except KeyError:
                sns_charge = 0
            sns_prob = sns_charge / num_photons
            print(f"  Charge: {sns_charge:6} -> Sensor prob: {sns_prob:2.3e}")
            
            light_table_probs[dist_xys.index(dist), zs.index(z)] = sns_prob        
        
        # If the DST file does NOT EXIST
        else:
            print(f"  WARNING: {dst_fname} NOT exist.")

    # Building the LightTable DataFrame
    dist_xys = [round(dist,1) for dist in dist_xys] # Taking just one decimal for the index
    light_table_data = np.c_[dist_xys, light_table_probs]
    light_table = pd.DataFrame(light_table_data, columns = light_table_columns)
    light_table.set_index("dist_xy", inplace = True)
    light_table.sort_index() # Not sure if needed to speed access
    
    return light_table



###
def build_table(det_name         : str,
                table_type       : str,
                signal_type      : str,
                sensor_name      : str,
                pitch            : Tuple[float, float, float],
                tracking_maxDist : float
               )                -> pd.DataFrame :
    
    if table_type == "energy":
        return build_energy_table(det_name, signal_type, sensor_name, pitch)
    
    elif table_type == "tracking":
        return build_tracking_table(det_name, signal_type, sensor_name, pitch, tracking_maxDist)
