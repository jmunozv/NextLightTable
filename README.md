# NextLightTable
Repository with the functionality to create NEXT Light Tables to be used
in parametrized nexus-simulations.

The LightTable generation is implemented in 2 steps:
1. Runing the simulations needed
2. Building the table based on results given by step-1 sims.


To run the sw just type:

python generateLightTable.py config.example.json


The config file must contain the following parameters:

"RUN_SIMULATIONS"   : Set it to true to run the sims.

"GENERATE_TABLE"    : Set it to true to build the table, once the sims are run

"det_name"          : VALID_DETECTORS    = ["NEXT_NEW", "NEXT100", "NEXT_FLEX"]

"table_type"        : VALID_TABLE_TYPES  = ["energy", "tracking"]

"signal_type"       : VALID_SIGNAL_TYPES = ["S1", "S2"]

"sensor_name"       : Sensor to sample. Typically: "PmtR11410", "SiPM", "TP_SiPM"

"pitch"             : Table pitch in mm

"photons_per_point" : Number of photons per point

"points_per_job"    : Number of points per job

"VERBOSITY"         : Set it to true to ahve an idea of what is going on.
