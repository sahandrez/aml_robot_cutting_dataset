import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import time
import os
import pandas as pd
import rosbag


class RobotDataHelper:
    """
    Provides some utilities for loading, plotting and processing the recorded robot data from bag files.
    """
    def __init__(self, bag_file, sampling_rate=10., material_label=0, thickness_label=0):
        """
        Initializes the DataHelper instance.
        :param bag_file: name of the bag file
        :param sampling_rate: sampling rate of the collected data
        :param material_label: label for the material class
        :param thickness_label: label for the thickness class
        """
        # Robot parameters
        self.N_JOINTS = 6
        self.PRE_FIX = '/j2n6s300'

        # Data parameters
        self.dataset_name = bag_file[:-4]
        self.sampling_rate = sampling_rate
        self.material_label = material_label
        self.thickness_label = thickness_label

        # Start time of the robot motion
        self.start_time = 0.
        # Velocity threshold for determining the start of the motion
        self.VEL_THRESHOLD = 0.02

        # Robot Joint States [N_samples, 7] for each key:
        # [position (rad), velocity (rad/s), torque (N.m), time (s), cutting_flag, material_label, thickness_label]
        self.robot_joint_states = {'joint_1': [], 'joint_2': [], 'joint_3': [],
                                   'joint_4': [], 'joint_5': [], 'joint_6': []}

        # Directories
        self.bag_directory = 'robot_data'
        self.plot_directory = 'plots'
        self.data_directory = 'data'
        current_path = os.path.abspath(__file__)
        self.root = os.path.dirname(os.path.dirname(current_path))
        bagfile_path = os.path.join(self.root, self.bag_directory, bag_file)

        # Load and preprocess the data
        self.bag = rosbag.Bag(bagfile_path, 'r')
        self.load_joint_states()
        self.add_labels()

    def load_joint_states(self):
        """
        Loads the joint states from the opened bagfile. Trims the beginning of the data to the point when the robot
        starts moving.
        """
        start_flag = True
        topic = self.PRE_FIX + '_driver/out/joint_state'

        for topic, msg, _ in self.bag.read_messages(topics=[topic]):
            time_stamp = self.to_sec(msg.header.stamp)

            # check the robot velocity to determine the start of the robot motion
            if start_flag:
                for joint_number in range(self.N_JOINTS):
                    if start_flag and abs(msg.velocity[joint_number]) >= self.VEL_THRESHOLD:
                        self.start_time += time_stamp
                        start_flag = False

            elif start_flag is None:
                self.start_time += time_stamp
                start_flag = False

            # set the starting point when the interaction started and set it to zero
            time_stamp -= self.start_time

            stop_count = 0
            for joint_number in range(self.N_JOINTS):
                if abs(msg.velocity[joint_number]) <= self.VEL_THRESHOLD:
                    stop_count += 1
            stop_flag = (stop_count == self.N_JOINTS)

            if not start_flag and time_stamp >= 0.:
                for joint_number in range(self.N_JOINTS):
                    if stop_flag:
                        break
                    self.robot_joint_states['joint_' + str(joint_number + 1)].append([msg.position[joint_number],
                                                                                      msg.velocity[joint_number],
                                                                                      msg.effort[joint_number],
                                                                                      time_stamp])

        for j in range(self.N_JOINTS):
            self.robot_joint_states['joint_' + str(j + 1)] = np.array(self.robot_joint_states['joint_' + str(j + 1)])

    def add_labels(self):
        """
        Checks if the cutting is happening or the robot is in free motion. Uses a moving window standard deviation to
        detect sudden changes in torque signal. Concatenates the cutting flag and material and thickness labels to the
        end of the robot joint states.
        """
        total_cutting_flag = np.ones((len(self.robot_joint_states['joint_1']), 1))
        window = 5

        for j in range(self.N_JOINTS):
            cutting_flag = np.zeros((len(self.robot_joint_states['joint_1']), 1))
            torque = self.robot_joint_states['joint_' + str(j + 1)][:, 2]

            torque_std = pd.Series(torque).rolling(window).std().to_numpy()
            torque_std[:window - 1] = torque_std[window:2 * window - 1]
            torque_std = np.expand_dims(torque_std, axis=1)

            mean_torque_std = np.mean(torque_std)
            cutting_indices = np.where(torque_std > mean_torque_std)
            cutting_flag[cutting_indices, 0] = 1.

            if j in [0, 2, 3, 4]:
                total_cutting_flag *= cutting_flag

        # add material and thickness labels
        material = self.material_label * np.ones((len(self.robot_joint_states['joint_1']), 1))
        thickness = self.thickness_label * np.ones((len(self.robot_joint_states['joint_1']), 1))

        total_cutting_flag[0, 0] = 0.
        for j in range(self.N_JOINTS):
            self.robot_joint_states['joint_' + str(j + 1)] = \
                np.concatenate((self.robot_joint_states['joint_' + str(j + 1)],
                                total_cutting_flag, material, thickness), axis=1)

    def save_data(self):
        """
        Saves data in a CSV file to be used later for learning. Each row represents one time step and data is organized
        as follows:
        [position (rad), velocity (rad/s), torque (N.m), time (s), cutting_flag, material_label, thickness_label]
        """
        directory = os.path.join(self.root, self.data_directory, self.dataset_name)
        if not os.path.exists(directory):
            os.makedirs(directory)

        for j in range(self.N_JOINTS):
            path = os.path.join(directory, 'joint_' + str(j + 1) + '.csv')
            pd.DataFrame(self.robot_joint_states['joint_' + str(j + 1)]).to_csv(path, index=None, header=None)

    def plot_joint_state(self, data):
        """
        Plots the joint state data versus time.
        :param data: 'position', 'velocity', 'effort'
        """
        # Set the plots properties
        matplotlib.rcParams.update({'font.size': 5})
        matplotlib.rcParams['figure.figsize'] = 20, 10
        t, y = [], []

        for joint_number in range(self.N_JOINTS):
            if data == 'position':
                y, _, _, t, _, _, _ = zip(*self.robot_joint_states['joint_' + str(joint_number + 1)])
            elif data == 'velocity':
                _, y, _, t, _, _, _ = zip(*self.robot_joint_states['joint_' + str(joint_number + 1)])
            elif data == 'effort':
                _, _, y, t, _, _, _ = zip(*self.robot_joint_states['joint_' + str(joint_number + 1)])
            else:
                exit("Error. Wrong usage of plot_raw_data")

            # plot
            plt.subplot(self.N_JOINTS, 1, joint_number + 1)
            plt.plot(t, y, 'r', label=data, linewidth=0.5)

            # plot information
            plt.title(data + ' of joint ' + str(joint_number + 1))
            plt.legend(prop={'size': 10})
            plt.xlabel('time (s)')
            plt.ylabel(data)

        directory = os.path.join(self.root, self.plot_directory, self.dataset_name)
        if not os.path.exists(directory):
            os.makedirs(directory)
        time_str = time.strftime("%Y%m%d-%H%M%S")
        plot_name = data + '_' + time_str + '.svg'
        plot_path = os.path.join(directory, plot_name)
        plt.savefig(plot_path, format='svg', dpi=1600)
        plt.close()

    @staticmethod
    def to_sec(duration):
        """
        Converts rospy.Duration to seconds.
        """
        return duration.secs + duration.nsecs * 10 ** -9
