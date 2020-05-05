import sys
import os
import subprocess

import pandas as pd

from datetime import datetime

# Specific LightTable stuff
from general_functions import get_host_name
from general_functions import get_seed



###
def make_init_file(det_name     : str,
                   init_fname   : str,
                   config_fname : str
                  )            -> None :

    # GEOMETRY
    content  = f"/Geometry/RegisterGeometry {det_name}\n"

    # GENERATOR
    content += f"/Generator/RegisterGenerator    SCINTGENERATOR\n"

    # ACTIONS
    content += f"/Actions/RegisterRunAction      DEFAULT\n"
    content += f"/Actions/RegisterEventAction    EL_SIM\n"
    content += f"/Actions/RegisterTrackingAction DEFAULT\n"
    content += f"/Actions/RegisterSteppingAction ANALYSIS\n"

    # PHYSICS
    content += f"/PhysicsList/RegisterPhysics G4EmStandardPhysics_option4\n"
    content += f"#/PhysicsList/RegisterPhysics G4EmExtraPhysics\n"
    content += f"/PhysicsList/RegisterPhysics G4DecayPhysics\n"
    content += f"/PhysicsList/RegisterPhysics G4RadioactiveDecayPhysics\n"
    content += f"#/PhysicsList/RegisterPhysics G4HadronElasticPhysicsHP\n"
    content += f"#/PhysicsList/RegisterPhysics G4HadronPhysicsQGSP_BERT_HP\n"
    content += f"#/PhysicsList/RegisterPhysics G4StoppingPhysics\n"
    content += f"#/PhysicsList/RegisterPhysics G4IonPhysics\n"
    content += f"/PhysicsList/RegisterPhysics G4OpticalPhysics\n"
    content += f"/PhysicsList/RegisterPhysics NexusPhysics\n"
    content += f"/PhysicsList/RegisterPhysics G4StepLimiterPhysics\n"

    # EXTRA CONFIGURATION
    content += f"/nexus/RegisterMacro {config_fname}\n"
    
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
        content += f"/Geometry/NextNew/pressure            10. bar\n"
        content += f"/Geometry/NextNew/sc_yield            25510. 1/MeV\n"
        content += f"/Geometry/NextNew/elfield             false\n"
        content += f"/Geometry/NextNew/EL_field            12.83 kV/cm\n"
    
        content += f"/Geometry/PmtR11410/SD_depth          4\n"
        content += f"/Geometry/PmtR11410/time_binning      10. ms\n"
        content += f"/Geometry/SiPMSensl/time_binning      10. ms\n"
    
        content += f"/Geometry/Next100/shielding_vis       false\n"
        content += f"/Geometry/NextNew/table_vis           false\n"
        content += f"/Geometry/NextNew/ics_vis             false\n"
        content += f"/Geometry/NextNew/vessel_vis          false\n"
        content += f"/Geometry/NextNew/energy_plane_vis    false\n"
        content += f"/Geometry/NextNew/enclosure_vis       false\n"
        content += f"/Geometry/NextNew/tracking_plane_vis  false\n"
        content += f"/Geometry/KDB/visibility              false\n"
        content += f"/Geometry/SiPMSensl/visibility        false\n"
        content += f"/Geometry/PmtR11410/visibility        false\n"
        content += f"/Geometry/NextNew/field_cage_vis      false\n"

    ## "NEXT100"
    elif (det_name == "NEXT100"):
        content += f"/Geometry/Next100/pressure        15. bar\n"
        content += f"/Geometry/Next100/sc_yield        25510. 1/MeV\n"
        content += f"/Geometry/Next100/max_step_size   1.  mm\n"
        content += f"/Geometry/Next100/elfield         false\n"
        content += f"/Geometry/Next100/EL_field        16. kilovolt/cm\n"
    
        content += f"/Geometry/PmtR11410/SD_depth      3\n"
        content += f"/Geometry/PmtR11410/time_binning  10. ms\n"
        content += f"/Geometry/SiPM/time_binning       10. ms\n"

        content += f"/Geometry/Next100/shielding_vis          false\n"
        content += f"/Geometry/Next100/vessel_vis             false\n"
        content += f"/Geometry/Next100/ics_vis                false\n"
        content += f"/Geometry/Next100/field_cage_vis         false\n"
        content += f"/Geometry/Next100/grids_vis              false\n"
        content += f"/Geometry/Next100/energy_plane_vis       false\n"
        content += f"/Geometry/Next100/tracking_plane_vis     false\n"
        content += f"/Geometry/GenericPhotosensor/visibility  false\n"
        content += f"/Geometry/PmtR11410/visibility           false\n"

    ## "NextFlex"
    elif (det_name == "NEXT_FLEX"):
        content += f"# GAS SETTING\n"
        content += f"/Geometry/NextFlex/gas              enrichedXe\n"
        content += f"/Geometry/NextFlex/gas_pressure     15. bar\n"
        content += f"/Geometry/NextFlex/gas_temperature  303. kelvin\n"
        content += f"/Geometry/NextFlex/e_lifetime       1000. ms\n"

        content += f"# ACTIVE\n"
        content += f"/Geometry/NextFlex/active_length      116. cm\n"
        content += f"/Geometry/NextFlex/drift_transv_diff  1. mm/sqrt(cm)\n"
        content += f"/Geometry/NextFlex/drift_long_diff    .3 mm/sqrt(cm)\n"

        content += f"# FIELD CAGE\n"
        content += f"/Geometry/NextFlex/buffer_length              280. mm\n"
        content += f"/Geometry/NextFlex/cathode_transparency       .98\n"
        content += f"/Geometry/NextFlex/anode_transparency         .88\n"
        content += f"/Geometry/NextFlex/gate_transparency          .88\n"
        content += f"/Geometry/NextFlex/el_gap_length              10.  mm\n"
        content += f"/Geometry/NextFlex/el_field_on                false\n"
        content += f"/Geometry/NextFlex/el_field_int               16. kilovolt/cm\n"
        content += f"/Geometry/NextFlex/el_transv_diff             0. mm/sqrt(cm)\n"
        content += f"/Geometry/NextFlex/el_long_diff               0. mm/sqrt(cm)\n"
        content += f"/Geometry/NextFlex/fc_wls_mat                 TPB\n"
        content += f"/Geometry/NextFlex/fc_with_fibers             true\n"
        content += f"/Geometry/NextFlex/fiber_mat                  EJ280\n"
        content += f"/Geometry/NextFlex/fiber_claddings            2\n"
        content += f"/Geometry/NextFlex/fiber_sensor_pde           1.\n"
        content += f"/Geometry/NextFlex/fiber_sensor_time_binning  10. ms\n"

        content += f"# ENERGY PLANE\n"
        content += f"/Geometry/NextFlex/ep_with_PMTs         true\n"
        content += f"/Geometry/NextFlex/ep_with_teflon       true\n"
        content += f"/Geometry/NextFlex/ep_copper_thickness  12. cm\n"
        content += f"/Geometry/NextFlex/ep_wls_mat           TPB\n"
        content += f"/Geometry/PmtR11410/SD_depth            3\n"
        content += f"/Geometry/PmtR11410/time_binning        10. ms\n"

        content += f"# TRACKING PLANE\n"
        content += f"/Geometry/NextFlex/tp_copper_thickness   12.  cm\n"
        content += f"/Geometry/NextFlex/tp_teflon_thickness    5.  mm\n"
        content += f"/Geometry/NextFlex/tp_teflon_hole_diam    7.  mm\n"
        content += f"/Geometry/NextFlex/tp_wls_mat            TPB\n"
        content += f"/Geometry/NextFlex/tp_sipm_anode_dist    15.  mm\n"
        content += f"/Geometry/NextFlex/tp_sipm_sizeX         1.   mm\n"
        content += f"/Geometry/NextFlex/tp_sipm_sizeY         1.   mm\n"
        content += f"/Geometry/NextFlex/tp_sipm_pitchX        15.6 mm\n"
        content += f"/Geometry/NextFlex/tp_sipm_pitchY        15.6 mm\n"
        content += f"/Geometry/NextFlex/tp_sipm_time_binning  10.  ms\n"

        content += f"# ICS\n"
        content += f"/Geometry/NextFlex/ics_thickness  12. cm\n"

        content += f"# VERBOSITY\n"
        content += f"/Geometry/NextFlex/verbosity     true\n"
        content += f"/Geometry/NextFlex/fc_verbosity  true\n"
        content += f"/Geometry/NextFlex/ep_verbosity  true\n"
        content += f"/Geometry/NextFlex/tp_verbosity  true\n"

        content += f"# VISIBILITIES\n"
        content += f"/Geometry/NextFlex/fc_visibility  false\n"
        content += f"/Geometry/NextFlex/ep_visibility  false\n"
        content += f"/Geometry/PmtR11410/visibility    false\n"
        content += f"/Geometry/NextFlex/tp_visibility  false\n"
        content += f"/Geometry/NextFlex/ics_visibility false\n"
    
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


    content  = f"{geometry_content}\n"
    
    content += f"### GENERATOR\n"
    content += f"/Generator/ScintGenerator/region      AD_HOC\n"
    content += f"/Geometry/{det_str}/specific_vertex_X  {pos_x} mm\n"
    content += f"/Geometry/{det_str}/specific_vertex_Y  {pos_y} mm\n"
    content += f"/Geometry/{det_str}/specific_vertex_Z  {pos_z} mm\n"
    content += f"/Generator/ScintGenerator/nphotons    {num_photons}\n"

    content += f"### PHYSICS\n"
    content += f"/process/optical/scintillation/setTrackSecondariesFirst true\n"
    content += f"/PhysicsList/Nexus/clustering           true\n"
    content += f"/PhysicsList/Nexus/drift                true\n"
    content += f"/PhysicsList/Nexus/electroluminescence  true\n"

    content += f"### VERBOSITIES\n"
    content += f"/control/verbose   0\n"
    content += f"/run/verbose       0\n"
    content += f"/event/verbose     0\n"
    content += f"/tracking/verbose  0\n"

    content += f"### CONTROL\n"
    content += f"/nexus/random_seed            {get_seed()}\n"
    content += f"/nexus/persistency/start_id   0\n"
    content += f"/nexus/persistency/outputFile {dst_fname}\n"

    #print(content)
    config_file = open(config_fname, 'w')
    config_file.write(content)
    config_file.close()



###
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
    
    content  = f""
    content += f"#PBS -q medium\n"
    content += f"#PBS -M jmunoz@ific.uv.es\n"
    content += f"#PBS -m ae\n"
    content += f"#PBS -o ./tmp\n"
    content += f"#PBS -e ./tmp\n"
    content += f"#PBS -j oe\n"

    content += f"source $HOME/.bashrc\n"
    content += f"source $HOME/.setNEXUS2\n"

    content += f"{exe_path}nexus -b {init_fname} -n {num_evts} > {log_fname}\n"

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
    content = f"#!/bin/bash\n"

    content += f"#SBATCH -n 1               # Number of cores requested\n"
    content += f"#SBATCH -N 1               # Ensure that all cores are on one machine\n"
    content += f"#SBATCH -t 150             # Runtime in minutes\n"
    content += f"#SBATCH -p guenette        # Partition to submit to\n"
    content += f"#SBATCH --mem=2000         # Memory per cpu in MB (see also –mem-per-cpu)\n"
    content += f"#SBATCH -o tmp/%j.out      # Standard out goes to this file\n"
    content += f"#SBATCH -e tmp/%j.err      # Standard err goes to this filehostname\n"

    content += f"source /n/home11/jmunozv/.bashrc\n"
    content += f"source /n/home11/jmunozv/.setNEXUS\n"

    content += f"{exe_path}nexus -b {init_fname} -n {num_evts} > {log_fname}\n"

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
        exe_path = "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/nexus/bin/"
        make_harvard_script(script_fname, exe_path, init_fname, log_fname, num_evts)
        
        os.system(f"sbatch {script_fname}")
    

    # No other machine is supported yet
    else:
        print(f"Light Table simulations in {host} are not supported yet.")
        sys.exit()