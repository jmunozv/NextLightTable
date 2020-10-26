import os

from datetime import datetime


###
def get_seed() -> int :
    dt = datetime.now()
    return dt.microsecond



###
def get_host_name() -> str :

    local_host = os.uname()[1]

    my_host = "local"
    if    "majorana"  in local_host: my_host = "majorana"
    elif  "neutrinos" in local_host: my_host = "neutrinos"
    elif  "harvard"   in local_host: my_host = "harvard"

    return my_host



###
def give_tmp_harvard_path(fname : str) -> str :
  tmp_path = "/n/holyscratch01/guenette_lab/Users/jmunozv/"
  return tmp_path + fname.split("/")[-1]

