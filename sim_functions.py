import sys
import os
import subprocess

import pandas     as pd
from   typing import List
from   time   import sleep

# Specific LightTable stuff
from general_functions import get_host_name
from general_functions import get_seed
from general_functions import give_tmp_harvard_path



###
def make_init_file(det_name     : str,
                   init_fname   : str,
                   config_fname : str
                  )            -> None :

    if   ("NEXT100" == det_name): det_name += "_OPT"         # XXX To be deleted asap
    elif ("DEMOpp"  in det_name): det_name  = "NEXT_DEMO"
    elif ("FLEX"    in det_name): det_name  = "NEXT_FLEX"
    elif ("TEST"    == det_name): det_name  = "NEXT_FLEX"
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

    if get_host_name() == "harvard":
        dst_fname = give_tmp_harvard_path(dst_fname)

    # Geometry Content
    template_file = f"templates/{det_name}.geometry.config"
    geometry_content = open(template_file).read()

    # Detector String for parameters
    if   ("NEXT_NEW" == det_name): det_str = "NextNew"
    elif ("DEMOpp"   in det_name): det_str = "NextDemo"
    elif ("NEXT100"  == det_name): det_str = "Next100"
    elif ("FLEX"     in det_name): det_str = "NextFlex"
    elif ("TEST"     == det_name): det_str = "NextFlex"
    else:
        print(f"{det_name} is not a valid detector.")
        sys.exit()


    content  = f"{geometry_content}\n"
    
    content +=  "### GENERATOR\n"
    content +=  "/Generator/ScintGenerator/region      AD_HOC\n"
    content += f"/Geometry/{det_str}/specific_vertex_X  {pos_x} mm\n"
    content += f"/Geometry/{det_str}/specific_vertex_Y  {pos_y} mm\n"
    content += f"/Geometry/{det_str}/specific_vertex_Z  {pos_z} mm\n"
    content += f"/Generator/ScintGenerator/nphotons    {num_photons}\n"

    content +=  "### PHYSICS\n"
    content +=  "/process/optical/scintillation/setTrackSecondariesFirst true\n"
    content +=  "/process/optical/processActivation Cerenkov             false\n"
    content +=  "/PhysicsList/Nexus/clustering           true\n"
    content +=  "/PhysicsList/Nexus/drift                true\n"
    content +=  "/PhysicsList/Nexus/electroluminescence  true\n"
    content +=  "/PhysicsList/Nexus/photoelectric        false\n"

    content +=  "### VERBOSITIES\n"
    content +=  "/control/verbose   0\n"
    content +=  "/run/verbose       0\n"
    content +=  "/event/verbose     0\n"
    content +=  "/tracking/verbose  0\n"

    content +=  "### CONTROL\n"
    content += f"/nexus/random_seed            {get_seed()}\n"
    content +=  "/nexus/persistency/start_id   0\n"
    content += f"/nexus/persistency/outputFile {dst_fname}\n"

    #print(content)
    config_file = open(config_fname, 'w')
    config_file.write(content)
    config_file.close()



###
def get_num_photons(dst_fname : str) -> int:
    try :
        mcConfig = pd.read_hdf(dst_fname, 'MC/configuration')
        mcConfig.set_index("param_key", inplace = True)
        num_photons_event = int(mcConfig.at["/Generator/ScintGenerator/nphotons" , "param_value"])
        num_events        = int(mcConfig.at["num_events" , "param_value"])
        return num_events * num_photons_event
    except KeyError:
        print("  No 'nphotons' info in the config table.")
        return 0
    except:
        print("  File corrupted.")
        return 0



###
def make_majorana_script(script_fname : str,
                         exe_path     : str,
                         init_fnames  : List[str],
                         log_fnames   : List[str],
                         num_evts     : int
                        )            -> None :
    
    content  =  ""
    content +=  "#PBS -q medium\n"
    content +=  "#PBS -M jmunoz@ific.uv.es\n"
    content +=  "#PBS -m ae\n"
    content +=  "#PBS -o ./tmp\n"
    content +=  "#PBS -e ./tmp\n"
    content +=  "#PBS -j oe\n"

    content +=  "source $HOME/.bashrc\n"
    content +=  "source $HOME/.setNEXUS2\n"

    for i in range(len(init_fnames)):
        content += f"{exe_path}nexus -b {init_fnames[i]} -n {num_evts} > {log_fnames[i]}\n"

    script_file = open(script_fname, 'w')
    script_file.write(content)
    script_file.close()



###
def make_harvard_script(script_fname : str,
                        exe_path     : str,
                        init_fnames  : List[str],
                        dst_fnames   : List[str],
                        log_fnames   : List[str],
                        num_evts     : int
                       )            -> None :
    content = "#!/bin/bash\n"

    content += "#SBATCH -n 1               # Number of cores requested\n"
    content += "#SBATCH -N 1               # Ensure that all cores are on one machine\n"
    content += "#SBATCH -t 2200            # Runtime in minutes\n"
    content += "#SBATCH -p guenette        # Partition to submit to\n"
    content += "#SBATCH --mem=1500         # Memory per cpu in MB (see also –mem-per-cpu)\n"
    content += "#SBATCH -o tmp/%j.out      # Standard out goes to this file\n"
    content += "#SBATCH -e tmp/%j.err      # Standard err goes to this filehostname\n"

    content +=  "source /n/home11/jmunozv/.bashrc\n"
    content +=  "source /n/home11/jmunozv/.setNEXUS\n"

    for i in range(len(init_fnames)):
        tmp_log_fname = give_tmp_harvard_path(log_fnames[i])
        tmp_dst_fname = give_tmp_harvard_path(dst_fnames[i])

        content += f"{exe_path}nexus -b {init_fnames[i]} -n {num_evts} > {tmp_log_fname}\n"

        content += f"mv {tmp_log_fname}    {log_fnames[i]}\n"
        content += f"mv {tmp_dst_fname}.h5 {dst_fnames[i]}.h5\n"


    script_file = open(script_fname, 'w')
    script_file.write(content)
    script_file.close()



###
def run_sims(init_fnames : List[str],
             dst_fnames  : List[str],
             log_fnames  : List[str],
             num_evts    : int
            )           -> None :

    # Getting local host
    host = get_host_name()

    ## Runing locally
    if host == "local":
        # Locally only 1 point per job, so check
        assert len(init_fnames) == 1, "When running locally, points_per_job MUST BE 1"
        
        exe_path = "/Users/Javi/Development/nexus/bin/"
        inst = [exe_path + "nexus", "-b", init_fnames[0], "-n", str(num_evts), ">", log_fnames[0]]
        
        #os.system("source /Users/Javi/.profile")
        #os.system("source /Users/Javi/.setNEXUS")
        my_env = os.environ.copy()
        subprocess.run(inst, env=my_env)
        

    ## Runing in MAJORANA queue system
    elif host == "majorana":
        script_fname = "sim.script"
        exe_path = "/home/jmunoz/Development/nexus/bin/"
        make_majorana_script(script_fname, exe_path, init_fnames, log_fnames, num_evts)
        
        os.system(f"qsub -N tst {script_fname}")
    

    ## Runing in HARVARD queue system
    elif host == "harvard":

        # Limit the maximum number of jobt to run at the same time
        while int(os.popen('squeue -u $USER | wc -l').read()) > 400:
            sleep(30)

        script_fname = "sim.slurm"
        exe_path = "/n/holystore01/LABS/guenette_lab/Users/jmunozv/Development/nexus/bin/"
        make_harvard_script(script_fname, exe_path, init_fnames, dst_fnames, log_fnames, num_evts)        
        os.system(f"sbatch {script_fname}")
    

    # No other machine is supported yet
    else:
        print(f"Light Table simulations in {host} are not supported yet.")
        sys.exit()
