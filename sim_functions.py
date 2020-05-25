import sys
import os
import subprocess

import pandas as pd

# Specific LightTable stuff
from general_functions import get_host_name
from general_functions import get_seed



###
def make_init_file(det_name     : str,
                   init_fname   : str,
                   config_fname : str
                  )            -> None :

    if (det_name == "NEXT100"): det_name += "_OPT" # XXX To be deleted asap
    params = locals()

    # Getting & formatting the template
    template_file = 'templates/init.mac'
    template      = open(template_file).read()
    content       = template.format(**params)

    #print(content)
    init_file = open(init_fname, 'w')
    init_file.write(content)
    init_file.close()



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
    if   (det_name == "NEXT_NEW" ): template_file = 'templates/NEXT_NEW.geometry.config'
    elif (det_name == "NEXT100"  ): template_file = 'templates/NEXT100.geometry.config'
    elif (det_name == "NEXT_FLEX"): template_file = 'templates/NEXT_FLEX_Ala100.geometry.config'
    else:
        print(f"{det_name} is not a valid detector.")
        sys.exit()

    geometry_content = open(template_file).read()


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
    content += f"#SBATCH --mem=1500         # Memory per cpu in MB (see also –mem-per-cpu)\n"
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
        #exe_path = "/Users/Javi/Development/nexus/bin/"
        exe_path = "/Users/Javi/Development/nexus/"
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
