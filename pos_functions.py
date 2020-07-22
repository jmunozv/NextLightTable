import numpy    as np

from typing import List
from typing import Tuple
from math   import sqrt

from detectors import get_detector_dimensions

import invisible_cities.core.system_of_units  as units



###
def get_table_positions(det_name        : str,
                        table_type      : str,
                        signal_type     : str,
                        pitch           : Tuple[float, float, float],
                        tracking_maxDist: float
                       )               -> List[Tuple[float, float, float]] :
    
    if table_type == "energy":
        return get_energy_table_positions(det_name, signal_type, pitch)
    
    elif table_type == "tracking":
        return get_tracking_table_positions(det_name, pitch, tracking_maxDist)



###
def get_energy_table_positions(det_name    : str,
                               signal_type : str,
                               pitch       : Tuple[float, float, float]
                              )           -> List[Tuple[float, float, float]] :
    
    # Getting detector dimensions
    det_dim = get_detector_dimensions(det_name)
    det_rad = int(det_dim["ACTIVE_radius"])
    det_len = int(det_dim["ACTIVE_length"] + det_dim["BUFFER_length"])
    det_el  = int(det_dim["EL_gap"])

    # Getting table pitch
    pitch_x = int(pitch[0])
    pitch_y = int(pitch[1])
    pitch_z = int(pitch[2])
    
    # Generating positions
    positions = []
    for x in range(-det_rad, det_rad, pitch_x):
        for y in range(-det_rad, det_rad, pitch_y):
            # Checking if current point fits into ACTIVE
            pos_rad = sqrt(x**2 + y**2)
            if (pos_rad < det_rad):
                # Generating S2 table (from the center of the EL gap)
                if signal_type == "S2":
                    positions.append((x, y, -det_el/2.))
                
                # Generating S1 table
                else:
                    for z in range(0, det_len, pitch_z):
                        positions.append((x, y, z))
            
    return positions



###
def get_tracking_table_positions(det_name        : str,
                                 pitch           : Tuple[float, float, float],
                                 tracking_maxDist: float
                                )               -> List[Tuple[float, float, float]] :
        
    # Getting detector dimensions
    det_dim = get_detector_dimensions(det_name)
    det_el  = int(det_dim["EL_gap"])

    # Getting reference sensor
    sns_id, sns_pos = det_dim["ref_sensor"]
    sns_pos_x       = sns_pos[0]
    sns_pos_y       = sns_pos[1]
    
    # Getting table pitch
    pitch_x = int(pitch[0])
    pitch_y = int(pitch[1])
    pitch_z = int(pitch[2])
    assert (pitch_x == pitch_y), "pitch_x must be equal to pitch_y for tracking tables"
    assert (pitch_z <= det_el),  "pitch_z must be equal or lower to detector EL GAP"
    
    # Generating positions
    positions = []
    for dist_xy in range(0, tracking_maxDist, pitch_x):
        for z in np.arange(pitch_z/2., det_el, pitch_z):
            positions.append((sns_pos_x + dist_xy, sns_pos_y, -z))

    return positions
