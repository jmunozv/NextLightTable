"""
This SCRIPT generates Light Tables for a given geometry.
"""

# General Importings
import os

import numpy  as np
import pandas as pd

from math import ceil

# Specific IC stuff
import invisible_cities.core.system_of_units  as units

from invisible_cities.io.mcinfo_io import load_mcsensor_response_df
from invisible_cities.io.mcinfo_io import get_sensor_types


# Light Table stuff
from sim_functions   import make_init_file
from sim_functions   import make_config_file
from sim_functions   import get_num_photons
from sim_functions   import run_sim

from table_functions import get_table_positions
from table_functions import get_working_paths


RUN_SIMULATIONS = False
GENERATE_TABLE  = False


########## SETTINGS ##########

# Vervosity
VERBOSITY = True

# Maximum number of photons per event (to allow running with less memory)
MAX_PHOTONS_PER_EVT = 1000000

# Current options: "NEXT_NEW", "NEXT100", "NEXT_FLEX"
det_name = "NEXT_NEW"

# Type of Light Table: S1 or S2
table_type = "S1"

# Detector Type (it will be PmtR11) for most of the geometries
# but it could be "FIBER_SENSOR" for the flexible geometry
sns_type = "PmtR11410"

# Table pitch
#pitch = (100.0 * units.mm, 100.0 * units.mm, 100.0 * units.mm)
pitch = (20.0 * units.mm, 20.0 * units.mm, 20.0 * units.mm)

# Table num photons / point
photons_per_point = 20000000

# Verbosity
if VERBOSITY:
    print(f"*****  {det_name} - {table_type} - {sns_type}  Light Table  *****")
    print(f"* pitch: {pitch} mm")



### Getting num_evts  &  (num_evts / file)
photons_per_event = photons_per_point
num_evts = ceil(photons_per_point / MAX_PHOTONS_PER_EVT)

if num_evts > 1:
    photons_per_event = MAX_PHOTONS_PER_EVT

# Verbosity
if VERBOSITY:
    print(f"* Photons/point: {photons_per_point:.1e}  ->  ")
    print(f"  Num Events: {num_evts} of {photons_per_event:.0e} photons/event")



### Getting PATHS
config_path, log_path, dst_path, table_path = get_working_paths(det_name)

# Verbosity
if VERBOSITY:
    print(f"* Config PATH: {config_path}")
    print(f"* Log    PATH: {log_path}")
    print(f"* Dst    PATH: {dst_path}")
    print(f"* Table  PATH: {table_path}")



### Getting Table positions
table_positions = get_table_positions(det_name, table_type, pitch)

# Vervosity
if VERBOSITY:
    print(f"* {det_name} - {table_type} table : {len(table_positions)} points.")
    #print(table_positions)



########## RUNNING SIMULATIONS ##########

if RUN_SIMULATIONS:

    print("\n*** Running Light Simulations ...")

    for pos in table_positions:
        
        # file names
        base_fname = f"{det_name}.x_{pos[0]}.y_{pos[1]}.z_{pos[2]}"
    
        init_fname   = config_path + base_fname + ".init"
        config_fname = config_path + base_fname + ".config"
        log_fname    = log_path    + base_fname + ".log"
        dst_fname    = dst_path    + base_fname + ".next"
        
        # make configuration files
        make_init_file(det_name, init_fname, config_fname)

        make_config_file(det_name, config_fname, dst_fname,
                         pos[0], pos[1], pos[2], photons_per_event)
        
        # Runing the simulation
        if VERBOSITY:
            print(f"* Runing {det_name} sim of {photons_per_point:.1e} photons from {pos} ...")
            
        # Check if the sim is already run with the correct num_photons
        if os.path.isfile(dst_fname + '.h5'):
            run_photons = get_num_photons(dst_fname + '.h5')
            if (get_num_photons(dst_fname + '.h5') < photons_per_point):
                print("  Simulation already run previously with less events, so re-running ...")
                run_sim(init_fname, log_fname, num_evts)
            else:
                print("  Simulation already run previously, so skipping ...")
        
        else:
            run_sim(init_fname, log_fname, num_evts)



########## GENERATING LIGHT TABLE ##########

if GENERATE_TABLE:

    print("\n*** Generating the Light Table ...")

    # Getting the list of sensors from the first dst file
    pos        = table_positions[0]
    
    base_fname   = f"{det_name}.x_{pos[0]}.y_{pos[1]}.z_{pos[2]}"
    dst_fname    = dst_path + base_fname + ".next.h5"
    sensor_types = get_sensor_types(dst_fname)
    sensor_ids   = sensor_types[sensor_types.sensor_name == sns_type].sensor_id.tolist()
    sensor_ids.sort()
    
    # Preparing the data
    light_table_columns = np.append(['x', 'y', 'z'], np.append(sensor_ids, 'total'))
    light_table_data    = []
    
    # Getting the table data from sims
    for pos in table_positions:
        
        # Verbosity
        if VERBOSITY:
            print(f"* Getting data from {det_name} - {pos} ...")
    
        # Getting the right DST file name
        base_fname = f"{det_name}.x_{pos[0]}.y_{pos[1]}.z_{pos[2]}"
        dst_fname  = dst_path + base_fname + ".next.h5"
    
        # Add a check that the position is the expected one ??
        # Add check that the number of sensors is the expected one
        if os.path.isfile(dst_fname):
        
            # Getting the number of photons from the file, as it could be different
            # from the one included in the setup.
            num_photons = get_num_photons(dst_fname)
            
            # Getting the sensor response of the sns_type requested
            sns_response = load_mcsensor_response_df(dst_fname, sns_name = sns_type)
            sns_charge = sns_response.groupby('sensor_id').charge.sum().tolist()
            sns_charge   = np.divide(sns_charge, num_photons)
            sns_charge   = np.append(sns_charge, sum(sns_charge))
        
            # Composing & storing this position data
            pos_data = np.append([pos[0], pos[1], pos[2]], sns_charge)
            light_table_data.append(pos_data)
            
            # Verbosity
            if VERBOSITY:
                print(f"  Simulation run with {num_photons:9} initial photons.")
                #print(f"  {sns_type} behaviour: {sns_response.charge.describe()}")

        # If the DST file does NOT EXIST
        else:
            print(f"  WARNING: {dst_fname} NOT exist.")

    
    ### Building the LightTable DataFrame
    light_table = pd.DataFrame(light_table_data,
                              columns = light_table_columns)
    
    # Formatting indices & columns
    light_table.set_index(['x', 'y', 'z'], inplace = True)
    light_table.sort_index() # Not sure if needed to speed access
    light_table = light_table.rename(columns = lambda name: sns_type + '_' + name)
    
    # Storing the DataFrame
    light_table_fname = table_path + f"{det_name}.{table_type}.{sns_type}.LightTable.h5"
    
    if VERBOSITY:
        print(f"\n*** Storing Light Table in {light_table_fname} ...")
    
    light_table.to_hdf(light_table_fname, '/LightTable',
                       mode   = 'w',
                       format = 'table',
                       data_columns = True)

print()
