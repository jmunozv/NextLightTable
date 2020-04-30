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
from invisible_cities.io.mcinfo_io        import load_mcsensor_response_df
from invisible_cities.io.mcinfo_io        import get_sensor_types

# Light Table stuff
from sim_functions       import make_init_file
from sim_functions       import make_config_file
from sim_functions       import run_sim
from sim_functions       import get_num_photons

from table_functions     import get_table_positions
from table_functions     import get_working_paths
from table_functions     import build_table
from table_functions     import get_fnames
from table_functions     import get_table_fname



RUN_SIMULATIONS = False
GENERATE_TABLE  = True

########## SETTINGS ##########

### Generalities
# Vervosity
VERBOSITY = True

# Maximum number of photons per event
MAX_PHOTONS_PER_EVT = 1000000


### Current options: "NEXT_NEW", "NEXT100", "NEXT_FLEX"
det_name = "NEXT_NEW"


### Type of Light Table: energy or tracking
table_type = "tracking"


### Signal Type: S1 or S2
signal_type = "S2"


### Sensor name.
# Typically PmtR11410 for energy tables and SiPM for tracking ones
#sensor_name = "PmtR11410"
sensor_name = "SiPM"


### Table pitch
#pitch = (200.0 * units.mm, 200.0 * units.mm, 200.0 * units.mm)
#pitch = (20.0 * units.mm, 20.0 * units.mm, 40.0 * units.mm)
pitch = (30.0 * units.mm, 30.0 * units.mm, 1.0 * units.mm)
#pitch = (1.0 * units.mm, 1.0 * units.mm, 1.0 * units.mm)


### Table num photons / point
photons_per_point = 1000000


### Getting (photons / point) & (events / point) & (photons / event)
events_per_point  = 1
photons_per_event = photons_per_point

if photons_per_event > MAX_PHOTONS_PER_EVT:
    events_per_point  = ceil(photons_per_point / MAX_PHOTONS_PER_EVT)
    photons_per_event = MAX_PHOTONS_PER_EVT
    photons_per_point = events_per_point * photons_per_event

    
### Getting Table positions
table_positions = get_table_positions(det_name, table_type, signal_type, pitch)


### Getting PATHS
config_path, log_path, dst_path, table_path = get_working_paths(det_name)


### Verbosity
if VERBOSITY:
    print(f"\n***** Generating {det_name} Light Table  *****\n")
    print(f"*** Type: {table_type}  -  Signal: {signal_type}  -  Sensor: {sensor_name}")
    print(f"*** Pitch: {pitch} mm")
    print(f"*** Photons/Point = {photons_per_point:.1e} splitted into ...")
    print(f"*** {events_per_point} Events/Point * {photons_per_event:.1e} Photons/Event")
    print(f"*** Total number of points:{len(table_positions)}")
    print(f"*** Config PATH: {config_path}")
    print(f"*** Log    PATH: {log_path}")
    print(f"*** Dst    PATH: {dst_path}")
    print(f"*** Table  PATH: {table_path}")
    


########## RUNNING SIMULATIONS ##########

if RUN_SIMULATIONS:

    print("\n*** Running Light Simulations ...")

    for pos in table_positions:
        
        # file names
        init_fname, config_fname, log_fname, dst_fname = get_fnames(det_name ,pos)

        # make configuration files
        make_init_file(det_name, init_fname, config_fname)

        make_config_file(det_name, config_fname, dst_fname,
                         pos[0], pos[1], pos[2],
                         photons_per_event)
        
        # Runing the simulation
        if VERBOSITY:
            print(f"* Runing {det_name} sim of {photons_per_point:.1e} photons from {pos} ...")
        
        # Check if the sim is already run with the correct num_photons
        if os.path.isfile(dst_fname + '.h5'):
            run_photons = get_num_photons(dst_fname + '.h5')
            if (get_num_photons(dst_fname + '.h5') < photons_per_point):
                print("  Simulation already run previously with less events, so re-running ...")
                run_sim(init_fname, log_fname, events_per_point)
            else:
                print("  Simulation already run previously, so skipping ...")
    
        else:
            run_sim(init_fname, log_fname, events_per_point)



########## GENERATING LIGHT TABLE ##########

if GENERATE_TABLE:

    light_table_fname = table_path + get_table_fname(det_name, table_type,
                                                     signal_type, sensor_name)
    
    # Light Table
    light_table = build_table(det_name, table_type, signal_type, sensor_name, pitch)
    
    light_table.to_hdf(light_table_fname, '/LightTable', mode   = 'w',
                       format = 'table', data_columns = True)

    # Config Table
    config_columns =  ['parameter', 'value']

    config_data    = [['detector' ,         det_name],
                      ['table_type',        table_type],
                      ['signal_type',       signal_type],
                      ['sensor',            sensor_name],
                      ['pitch_x',           str(pitch[0])],
                      ['pitch_y',           str(pitch[1])],
                      ['pitch_z',           str(pitch[2])],
                      ['photons_per_point', str(photons_per_point)],
                      ['photons_per_event', str(photons_per_event)],
                      ['events_per_point',  str(events_per_point)],
                      ['total_points',      str(len(table_positions))],
                      ['table_path',        table_path],
                      ['dst_path',          dst_path],
                      ['config_path',       config_path],
                      ['log_path',          log_path]]

    config_table = pd.DataFrame(config_data, columns = config_columns)
    config_table.set_index("parameter", inplace = True)
    
    config_table.to_hdf(light_table_fname, '/Config', mode   = 'a',
                        format = 'table', data_columns = True)

    # Verbosing
    print(f"\n*** Storing Light Table in {light_table_fname} ...\n")
