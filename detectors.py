from typing import Dict

import invisible_cities.core.system_of_units  as units



###
# Ideally to be read from the DataBase if this info is stored there.
def get_detector_dimensions(det_name : str
                           )        -> Dict :
    dimensions = {
        'NEXT_NEW': {
            'ACTIVE_radius' : 208.0 * units.mm,
            'ACTIVE_length' : 532.0 * units.mm,
            'BUFFER_length' : 129.9 * units.mm,
            'EL_gap'        :   6.0 * units.mm,
            'ref_sensor'    : (17018, (25.0, 25.0))   # Reference sensor (id, (x,y))
        },

        'NEXT100': {
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :   10.0  * units.mm,
            'ref_sensor'    : (33000, (7.83, 7.83))   # Reference sensor (id, (x,y))
        },

        'FLEX100': {
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :   10.0  * units.mm,
            'ref_sensor'    : (2546, (0.0, 0.0))   # Reference sensor (id, (x,y))
        },

        'FLEX100_M10': {
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :   10.0  * units.mm,
            'ref_sensor'    : (2546, (0.0, 0.0))   # Reference sensor (id, (x,y))
        },

        'FLEX100_M12': {
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :   10.0  * units.mm,
            'ref_sensor'    : (2546, (0.0, 0.0))   # Reference sensor (id, (x,y))
        },

        'FLEX100_M6_O6': {
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :   10.0  * units.mm,
            'ref_sensor'    : (2546, (0.0, 0.0))   # Reference sensor (id, (x,y))
        },

        'FLEX100_7_3': {
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :    7.0  * units.mm,
            'ref_sensor'    : (2546, (0.0, 0.0))   # Reference sensor (id, (x,y))
        },

        'FLEX_NEW': {
            'ACTIVE_radius' :  208.0  * units.mm,
            'ACTIVE_length' :  532.0  * units.mm,
            'BUFFER_length' :  129.9  * units.mm,
            'EL_gap'        :    6.0  * units.mm,
            'ref_sensor'    : (1656, (0.0, 0.0))   # Reference sensor (id, (x,y))
        },

        'TEST': {                                   # == FLEX100
            'ACTIVE_radius' :  492.0  * units.mm,
            'ACTIVE_length' : 1204.95 * units.mm,
            'BUFFER_length' :  254.6  * units.mm,
            'EL_gap'        :   10.0  * units.mm,
            'ref_sensor'    : (2546, (0.0, 0.0))   # Reference sensor (id, (x,y))
        }
    }
    
    return dimensions[det_name]

