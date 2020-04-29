import sys
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
