import sys
import os
import subprocess

import pandas as pd

from datetime import datetime

# Specific LightTable stuff
from table_functions import get_host_name


###
def get_seed() -> int :
    dt = datetime.now()
    return dt.microsecond



###
def make_init_file(det_name     : str,
                   init_fname   : str,
                   config_fname : str
                  )            -> None :

    content = f'''### GEOMETRY
/Geometry/RegisterGeometry {det_name}

### GENERATOR
/Generator/RegisterGenerator    SCINTGENERATOR

### ACTIONS
/Actions/RegisterRunAction      DEFAULT
/Actions/RegisterEventAction    EL_SIM
/Actions/RegisterTrackingAction DEFAULT
/Actions/RegisterSteppingAction ANALYSIS

### PHYSICS
/PhysicsList/RegisterPhysics G4EmStandardPhysics_option4
/PhysicsList/RegisterPhysics G4EmExtraPhysics
/PhysicsList/RegisterPhysics G4DecayPhysics
/PhysicsList/RegisterPhysics G4RadioactiveDecayPhysics
/PhysicsList/RegisterPhysics G4HadronElasticPhysicsHP
/PhysicsList/RegisterPhysics G4HadronPhysicsQGSP_BERT_HP
/PhysicsList/RegisterPhysics G4StoppingPhysics
/PhysicsList/RegisterPhysics G4IonPhysics
/PhysicsList/RegisterPhysics G4OpticalPhysics
/PhysicsList/RegisterPhysics NexusPhysics
/PhysicsList/RegisterPhysics G4StepLimiterPhysics

### EXTRA CONFIGURATION
/nexus/RegisterMacro {config_fname}'''
    
    #print(content)
    init_file = open(init_fname, 'w')
    init_file.write(content)
    init_file.close()



###
def get_geometry_config(det_name : str) -> str :
    
    valid_geometries = ["NEXT_NEW", "NEXT100", "NEXT_FLEX"]
    assert det_name in valid_geometries, "Wrong Geometry"
    
    content = "### GEOMETRY"
    
    ## "NEW"
    if (det_name == "NEXT_NEW"):
        content += '''
/Geometry/NextNew/pressure            10. bar
/Geometry/NextNew/elfield             false
/Geometry/PmtR11410/SD_depth          4
/Geometry/PmtR11410/time_binning      10. ms
/Geometry/SiPMSensl/time_binning      10. ms

/Geometry/Next100/shielding_vis       false
/Geometry/NextNew/table_vis           false
/Geometry/NextNew/ics_vis             false
/Geometry/NextNew/vessel_vis          false
/Geometry/NextNew/energy_plane_vis    false
/Geometry/NextNew/enclosure_vis       false
/Geometry/NextNew/tracking_plane_vis  false
/Geometry/KDB/visibility              false
/Geometry/SiPMSensl/visibility        false
/Geometry/PmtR11410/visibility        false
/Geometry/NextNew/field_cage_vis      false
        '''
    
    ## "NEXT100"
    elif (det_name == "NEXT100"):
        content += '''
/Geometry/Next100/pressure           15. bar
/Geometry/Next100/max_step_size       1. mm
/Geometry/Next100/elfield            false
/Geometry/PmtR11410/SD_depth         3
/Geometry/PmtR11410/time_binning     10. ms
/Geometry/SiPMSensl/time_binning     10. ms

/Geometry/Next100/shielding_vis      false
/Geometry/Next100/vessel_vis         false
/Geometry/Next100/ics_vis            false
/Geometry/Next100/field_cage_vis     false
/Geometry/Next100/grids_vis          false
/Geometry/Next100/energy_plane_vis   false
/Geometry/Next100/tracking_plane_vis false
/Geometry/SiPMSensl/visibility       false
        '''
    
    ## "NextFlex"
    elif (det_name == "NEXT_FLEX"):
        content += '''
# GAS SETTING
/Geometry/NextFlex/gas              enrichedXe
/Geometry/NextFlex/gas_pressure     15. bar
/Geometry/NextFlex/gas_temperature  300. kelvin

# ACTIVE
/Geometry/NextFlex/active_length      116. cm
/Geometry/NextFlex/drift_transv_diff  1. mm/sqrt(cm)
/Geometry/NextFlex/drift_long_diff    .3 mm/sqrt(cm)

# FIELD CAGE
/Geometry/NextFlex/buffer_length    280. mm

/Geometry/NextFlex/el_gap_length    10.  mm
/Geometry/NextFlex/el_field_on      false
/Geometry/NextFlex/el_field_int     16. kilovolt/cm
/Geometry/NextFlex/el_transv_diff   0. mm/sqrt(cm)
/Geometry/NextFlex/el_long_diff     0. mm/sqrt(cm)

/Geometry/NextFlex/fc_wls_mat       TPB

/Geometry/NextFlex/fc_with_fibers   true
/Geometry/NextFlex/fiber_mat        EJ280
/Geometry/NextFlex/fiber_claddings  2

/Geometry/NextFlex/fiber_sensor_pde           1.
/Geometry/NextFlex/fiber_sensor_time_binning  10. ms

# ENERGY PLANE
/Geometry/NextFlex/ep_with_PMTs         true
/Geometry/NextFlex/ep_with_teflon       true
/Geometry/NextFlex/ep_copper_thickness  12. cm
/Geometry/NextFlex/ep_wls_mat           TPB

/Geometry/PmtR11410/SD_depth            3
/Geometry/PmtR11410/time_binning        10. ms

# TRACKING PLANE
/Geometry/NextFlex/tp_copper_thickness   12. cm
/Geometry/NextFlex/tp_wls_mat            TPB
/Geometry/NextFlex/tp_sipm_anode_dist    10. mm
/Geometry/NextFlex/tp_sipm_size          1.  mm
/Geometry/NextFlex/tp_sipm_pitchX        15. mm
/Geometry/NextFlex/tp_sipm_pitchY        15. mm
/Geometry/NextFlex/tp_sipm_time_binning  10. ms

# ICS
/Geometry/NextFlex/ics_thickness  12. cm

# VERBOSITY
/Geometry/NextFlex/verbosity     true
/Geometry/NextFlex/fc_verbosity  true
/Geometry/NextFlex/ep_verbosity  true
/Geometry/NextFlex/tp_verbosity  true

# VISIBILITIES
/Geometry/NextFlex/fc_visibility  false
/Geometry/NextFlex/ep_visibility  false
/Geometry/PmtR11410/visibility    false
/Geometry/NextFlex/tp_visibility  false
/Geometry/NextFlex/ics_visibility false
        '''
    
    return content



###
def make_config_file(det_name     : str,
                     config_fname : str,
                     dst_fname    : str,
                     pos_x        : int,
                     pos_y        : int,
                     pos_z        : int,
                     num_photons  : int
                    )            -> None :

    # Geometry Content
    geometry_content = get_geometry_config(det_name)
    
    # Detector String for parameters
    if   (det_name == "NEXT_NEW" ): det_str = "NextNew"
    elif (det_name == "NEXT100"  ): det_str = "Next100"
    elif (det_name == "NEXT_FLEX"): det_str = "NextFlex"
    else:
        print(f"{det_name} is not a valid detector.")
        sys.exit()


    content = f'''
{geometry_content}
    
### GENERATOR
/Generator/ScintGenerator/region      AD_HOC
/Geometry/{det_str}/specific_vertex_X  {pos_x} mm
/Geometry/{det_str}/specific_vertex_Y  {pos_y} mm
/Geometry/{det_str}/specific_vertex_Z  {pos_z} mm
/Generator/ScintGenerator/nphotons    {num_photons}

### PHYSICS
/process/optical/scintillation/setTrackSecondariesFirst true
/PhysicsList/Nexus/clustering           true
/PhysicsList/Nexus/drift                true
/PhysicsList/Nexus/electroluminescence  true

### VERBOSITIES
/control/verbose   0
/run/verbose       0
/event/verbose     0
/tracking/verbose  0

### CONTROL
/nexus/random_seed            {get_seed()}
/nexus/persistency/start_id   0
/nexus/persistency/outputFile {dst_fname}
'''
    #print(content)
    config_file = open(config_fname, 'w')
    config_file.write(content)
    config_file.close()



#def get_num_photons(dst_fname):
#    mcConfig = pd.read_hdf(dst_fname, 'MC/configuration')
#    mcConfig.set_index("param_key", inplace = True)
#    num_photons_event = int(mcConfig.at["/Generator/ScintGenerator/nphotons" , "param_value"])
#    num_events        = int(mcConfig.at["num_events" , "param_value"])
#    return num_events * num_photons_event

def get_num_photons(dst_fname):
    mcConfig = pd.read_hdf(dst_fname, 'MC/configuration')
    mcConfig.set_index("param_key", inplace = True)
    try :
        num_photons_event = int(mcConfig.at["/Generator/ScintGenerator/nphotons" , "param_value"])
        num_events        = int(mcConfig.at["num_events" , "param_value"])
        return num_events * num_photons_event
    except KeyError:
        print("  No 'nphotons' info in the config table.")
        return 20000000



###
def make_majorana_script(script_fname : str,
                         exe_path     : str,
                         init_fname   : str,
                         log_fname    : str,
                         num_evts     : int
                        )            -> None :
    
    content = f'''
#PBS -q medium
#PBS -M jmunoz@ific.uv.es
#PBS -m ae
#PBS -o ./tmp
#PBS -e ./tmp
#PBS -j oe

source $HOME/.bashrc
source $HOME/.setNEXUS2

{exe_path}nexus -b {init_fname} -n {num_evts} > {log_fname}
'''

    script_file = open(script_fname, 'w')
    script_file.write(content)
    script_file.close()



###
def make_harvard_script(script_fname : str,
                        exe_path     : str,
                        init_fname   : str,
                        log_fname    : str,
                        num_evts     : int
                       )            -> None :
    content = f'''#!/bin/bash

#SBATCH -n 1               # Number of cores requested
#SBATCH -N 1               # Ensure that all cores are on one machine
#SBATCH -t 150             # Runtime in minutes
#SBATCH -p guenette        # Partition to submit to
#SBATCH --mem=2000        # Memory per cpu in MB (see also –mem-per-cpu)
#SBATCH -o tmp/%j.out      # Standard out goes to this file
#SBATCH -e tmp/%j.err      # Standard err goes to this filehostname

source /n/home11/jmunozv/.bashrc
source /n/home11/jmunozv/.setNEXUS

{exe_path}nexus -b {init_fname} -n {num_evts} > {log_fname}
'''

    script_file = open(script_fname, 'w')
    script_file.write(content)
    script_file.close()



###
def run_sim(init_fname : str,
            log_fname  : str,
            num_evts   : int
           )          -> None :

    # Getting local host
    host = get_host_name()

    ## Runing locally
    if host == "local":
        exe_path = "/Users/Javi/Development/nexus/bin/"
        inst = [exe_path + "nexus", "-b", init_fname, "-n", str(num_evts), ">", log_fname]
        
        #os.system("source /Users/Javi/.profile")
        #os.system("source /Users/Javi/.setNEXUS")
        my_env = os.environ.copy()
        subprocess.run(inst, env=my_env)
        

    ## Runing in MAJORANA queue system
    elif host == "majorana":
        script_fname = "sim.script"
        exe_path = "/home/jmunoz/Development/nexus/bin/"
        make_majorana_script(script_fname, exe_path, init_fname, log_fname, num_evts)
        
        os.system(f"qsub -N tst {script_fname}")
    

    ## Runing in HARVARD queue system
    elif host == "harvard":
        script_fname = "sim.slurm"
        exe_path = "/n/holylfs02/LABS/guenette_lab/users/jmunozv/Development/nexus/bin/"
        make_harvard_script(script_fname, exe_path, init_fname, log_fname, num_evts)
        
        os.system(f"sbatch {script_fname}")
    

    # No other machine is supported yet
    else:
        print(f"Light Table simulations in {host} are not supported yet.")
        sys.exit()