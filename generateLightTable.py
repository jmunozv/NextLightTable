"""
This SCRIPT generates Light Tables for a given geometry.
"""

# General Importings
import os
import sys
import json
import pandas as pd

from math import ceil

# Specific IC stuff
import invisible_cities.core.system_of_units  as units

# Light Table stuff
from sim_functions    import make_init_file
from sim_functions    import make_config_file
from sim_functions    import run_sims
from sim_functions    import get_num_photons

from pos_functions    import get_table_positions

from table_functions  import get_working_paths
from table_functions  import build_table
from table_functions  import get_fnames
from table_functions  import get_table_fname

from detectors        import get_detector_dimensions



#################### GENERALITIES ####################

# Vervosity
VERBOSITY = True

# Maximum number of photons per event
MAX_PHOTONS_PER_EVT = 1000000

# Valid options
VALID_DETECTORS    = ["NEXT_NEW", "NEXT100", "FLEX100", "FLEX100_7_3",
                      "FLEX100_M10", "FLEX100_M6_O6", "FLEX100_M12",
                      "FLEX_NEW", "TEST"]
VALID_TABLE_TYPES  = ["energy", "tracking"]
VALID_SIGNAL_TYPES = ["S1", "S2"]



#################### SETTINGS ####################
try:
    config_fname = sys.argv[1]
except IndexError:
    print("\nUsage: python generateLightTable.py config_file.json\n")
    sys.exit()

with open(config_fname) as config_file:
    config_data = json.load(config_file)

# Step Selection
RUN_SIMULATIONS = config_data["RUN_SIMULATIONS"]
GENERATE_TABLE  = config_data["GENERATE_TABLE"]

# Table Setting
det_name = config_data["det_name"]
assert det_name in VALID_DETECTORS, "Wrong Detector"

table_type = config_data["table_type"]
assert table_type in VALID_TABLE_TYPES, "Wrong Table Type"

signal_type = config_data["signal_type"]
assert signal_type in VALID_SIGNAL_TYPES, "Wrong Signal Type"

sensor_name = config_data["sensor_name"]

pitch = tuple(config_data['pitch'])
if((table_type == "tracking") and (pitch[2] > 2.0 * units.mm)):
    print("\n#### WARNING #### - Pitch Z unusually big.")

tracking_maxDist  = config_data["tracking_maxDist"]

photons_per_point = config_data["photons_per_point"]

# 
points_per_job = config_data["points_per_job"]



#################### PRELIMINARY JOB ####################

### Getting (photons / point) & (events / point) & (photons / event)
events_per_point  = 1
photons_per_event = photons_per_point

if photons_per_event > MAX_PHOTONS_PER_EVT:
    events_per_point  = ceil(photons_per_point / MAX_PHOTONS_PER_EVT)
    photons_per_event = MAX_PHOTONS_PER_EVT
    photons_per_point = events_per_point * photons_per_event

    
### Getting Table positions
table_positions = get_table_positions(det_name, table_type, signal_type, pitch, tracking_maxDist)
num_points = len(table_positions)


### Getting Num of jobs
num_jobs = ceil(num_points / points_per_job)
photons_per_job = points_per_job * photons_per_point


### Getting PATHS
config_path, log_path, dst_path, table_path = get_working_paths(det_name)


### Verbosity
if VERBOSITY:
    print(f"\n***** Generating {det_name} Light Table  *****\n")
    print(f"*** Type: {table_type}  -  Signal: {signal_type}  -  Sensor: {sensor_name}")
    print(f"*** Pitch: {pitch} mm")
    print(f"*** MaxDist of tracking tables: {tracking_maxDist} mm")    
    print(f"*** Photons/Point = {photons_per_point:.1e} splitted into ...")
    print(f"***    {events_per_point} Events/Point * {photons_per_event:.1e} Photons/Event")
    print(f"*** Total number of points: {num_points:6}")
    #print(table_positions)
    print(f"*** Max. number of jobs:    {num_jobs:6}")
    print(f"*** Photons/Job: {photons_per_job}  ->  {photons_per_job/60.e4:.3} minutes/job (@ Harvard)")
    print(f"*** Config PATH: {config_path}")
    print(f"*** Log    PATH: {log_path}")
    print(f"*** Dst    PATH: {dst_path}")
    print(f"*** Table  PATH: {table_path}")


### Checks
#assert num_jobs < 10000, "Number of jobs too high"
if (num_jobs > 10000):
    print("\n*** WARNING: Number of jobs too high.\n")

#assert (photons_per_job/1.e4) < 24*60*60, "Jobs larger than 24 hours"
if ((photons_per_job/1.e4) > 24*60*60):
    print("\n*** WARNING: Jobs larger than 24 hours.\n")


#################### RUNNING SIMULATIONS ####################

if RUN_SIMULATIONS:

    print(f"\n*** Running {num_points} Light Simulations ...\n")

    init_fnames    = []
    dst_fnames     = []
    log_fnames     = []
    job_id         = 0

    # For every position ...
    for pos in table_positions:
        print(f"* Position {pos} - {photons_per_point} photons")

        # file names
        init_fname, config_fname, log_fname, dst_fname = get_fnames(det_name ,pos)

        # Check if the sim is already run with the correct num_photons
        if os.path.isfile(dst_fname + '.h5'):
            prev_photons = get_num_photons(dst_fname + '.h5')
            if prev_photons >= photons_per_point:
                print("  Simulation run previously, so skipping ...")
                continue
            elif prev_photons > 0:
                print("  Simulation run previously with less events, so re-running ...")

        # Preparing this position to be simulated
        make_init_file(det_name, init_fname, config_fname)
        
        make_config_file(det_name, config_fname, dst_fname,
                         pos[0], pos[1], pos[2],
                         photons_per_event)
        
        # Adding file names to be run
        init_fnames += [init_fname]
        dst_fnames  += [dst_fname]
        log_fnames  += [log_fname]

        # Launching simulation job
        if(len(init_fnames) == points_per_job):
            print(f"* Submitting job {job_id} with {len(init_fnames)} points\n")
            run_sims(init_fnames, dst_fnames, log_fnames, events_per_point)
            job_id += 1
            init_fnames = []
            dst_fnames  = []
            log_fnames  = []

    # Running last set of sims if needed.
    if len(init_fnames):
        print(f"* Submitting job {job_id} with {len(init_fnames)} points\n")
        run_sims(init_fnames, dst_fnames, log_fnames, events_per_point)




#################### GENERATING LIGHT TABLE ####################

if GENERATE_TABLE:

    dimensions = get_detector_dimensions(det_name)
    light_table_fname = table_path + get_table_fname(det_name, table_type,
                                                     signal_type, sensor_name)
    
    # Light Table
    light_table = build_table(det_name, table_type, signal_type, sensor_name, pitch, tracking_maxDist)
    
    light_table.to_hdf(light_table_fname, '/LightTable', mode   = 'w',
                       format = 'table', data_columns = True)

    # Config Table
    config_columns =  ['parameter', 'value']

    config_data    = [['detector' ,            det_name],
                      ['ACTIVE_rad',           str(dimensions['ACTIVE_radius'])],
                      ['ACTIVE_length',        str(dimensions['ACTIVE_length'])],
                      ['EL_GAP',               str(dimensions['EL_gap'])],
                      ['reference_sensor_id',  str(dimensions['ref_sensor'][0])],
                      ['table_type',           table_type],
                      ['signal_type',          signal_type],
                      ['sensor',               sensor_name],
                      ['pitch_x',              str(pitch[0])],
                      ['pitch_y',              str(pitch[1])],
                      ['pitch_z',              str(pitch[2])],
                      ['photons_per_point',    str(photons_per_point)],
                      ['photons_per_event',    str(photons_per_event)],
                      ['events_per_point',     str(events_per_point)],
                      ['total_points',         str(num_points)],
                      ['table_path',           table_path],
                      ['dst_path',             dst_path],
                      ['config_path',          config_path],
                      ['log_path',             log_path]]

    config_table = pd.DataFrame(config_data, columns = config_columns)
    config_table.set_index("parameter", inplace = True)
    
    config_table.to_hdf(light_table_fname, '/Config', mode   = 'a',
                        format = 'table', data_columns = True)

    # Verbosing
    print(f"\n*** Storing Light Table in {light_table_fname} ...\n")
