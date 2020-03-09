#! /usr/bin/env python2
"""
This script loads the robot data from the bagfiles and reorganizes them in CSV files that can be later used for a
data loader.
"""

import argparse
from robot_data_helper import RobotDataHelper


parser = argparse.ArgumentParser(description='Processes robot data')
parser.add_argument('--save_plots', default=False, action='store_true', help='Saves the plots.')

if __name__ == '__main__':
    """
    Material labels for the cuts: 
        0: LVL, 1: Maple, 2: Oak, 3: Birch, 4: Hardwood
    Thickness labels for the cuts: 
        0: 3/16, 1: 1/4, 2: 5/16, 3: 3/8, 4: 7/16
    """
    MATERIAL_LABELS = [0, 0, 0, 0, 0, 1, 2, 3, 1, 2, 3, 4]
    THICKNESS_LABELS = [0, 1, 2, 3, 4, 1, 1, 1, 3, 3, 3, 3]
    N_CUTS = 12
    N_EACH_CUT = 15

    args = parser.parse_args()

    for i in range(N_CUTS):
        for j in range(N_EACH_CUT):
            bag_name = 'cut_' + str(i + 1) + '/cut_' + str(i + 1) + '_' + str(j + 1) + '.bag'
            print('Processing bagfile ' + bag_name)
            dh = RobotDataHelper(bag_name,
                                 sampling_rate=10.,
                                 material_label=MATERIAL_LABELS[i],
                                 thickness_label=THICKNESS_LABELS[i])

            if args.save_plots:
                for data_type in ['position', 'velocity', 'effort']:
                    dh.plot_joint_state(data_type)

            dh.save_data()
