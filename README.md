# AML Robot Cutting Dataset

* The AML Robot Cutting Dataset consists of approximately 1500 seconds of real data collected on 
Kinova Jaco 2 robot retrofitted with a custom end-effector fixture and dremel performing cutting tasks on wood specimens for 5 materials and 5 thicknesses. 

### Cutting Setup
* The test bed consists of the following components:
    1. **[Kinova Jaco 2 Arm](https://www.kinovarobotics.com/en/products/robotic-arms/kinova-gen2-ultra-lightweight-robot):**
 A light-weight six-DOF robotic manipulator with a maximum payload 
of 2.6 kg without the original gripper. The robot is equipped with joint encoders and joint 
torque sensors. During the data collection, the robot was controlled manually through
 Cartesian velocity control via a joy stick controller.
    1.  **Cutting Tool and End-effector Fixture:** Designed as a replacement for the original 
three-finger gripper of the robot, the end-effector fixture is responsible for holding 
the cutting tool. The cutting tool, equipped with a wood cutting circular saw blade,
is a Dremel 100 Single Speed Rotary Tool.
    1. **Specimen Fixture:** This component provides a firm support for holding the
wood specimens and measuring the cutting force using an integrated force/torque sensor
in the middle of the fixture.
    1. **Force/Torque Sensor:**: We have used an [ATI Mini40](https://www.ati-ia.com/products/ft/ft_models.aspx?id=Mini40)
 as the force/torque sensor. The following table shows the sensor properties:
  
|                    | F_x, F_y | F_z     | T_x, T_y   | T_z        |
|--------------------|----------|---------|------------|------------|
| **Sensing Ranges** | 20 N     | 60 N    | 1 N.m      | 1 N.m      |
| **Resolution**     | 1/200 N  | 1/100 N | 1/8000 N.m | 1/8000 N.m |

* The cutting test bed is set up as the picture below: 

![Alt text](figures/cutting_testbed.jpg?raw=true "Cutting test bed" )


### Citation
If you are using this dataset in your work, please cite the following paper. It will be published in IROS 2020. 
```
@article{rezaei2020learning,
  title={Learning the Latent Space of Robot Dynamics for Cutting Interaction Inference},
  author={Rezaei-Shoshtari, Sahand and Meger, David and Sharf, Inna},
  journal={arXiv preprint arXiv:2007.11167},
  year={2020}
}
```


### Dataset Details
* The dataset has been collected on 12 unique wood specimens each being cut 15 times, 
thus resulting in a total of 180 cuts. The rods have been selected from sets of 
five materials and five thicknesses, but due to the limitations in the selections, 
not every size was available for each material. The following table presents the 
details of the cutting dataset:

| Cut No. | Material | Thickness (in) | Datapoints |
|---------|:--------:|:--------------:|:----------:|
| 1       |    LVL   |      3/16      |     980    |
| 2       |    LVL   |       1/4      |     923    |
| 3       |    LVL   |      5/16      |     937    |
| 4       |    LVL   |       3/8      |    1721    |
| 5       |    LVL   |      7/16      |    1865    |
| 6       |   Maple  |       1/4      |    1206    |
| 7       |    Oak   |       1/4      |    1070    |
| 8       | Birch    | 1/4            | 1033       |
| 9       | Maple    | 3/8            | 1420       |
| 10      | Oak      | 3/8            | 1369       |
| 11      | Birch    | 3/8            | 1228       |
| 12      | Hardwood | 3/8            | 1111       |
| **Total** |        |                | 14863      |

* The dataset consists of three directories:
   * `robot_data`: Robot states and some other useful information collected in the 
   form of bagfiles.     
        ```
        ROS topics list in each bag file:
        /j2n6s300_driver/in/cartesian_velocity           100 Hz    : kinova_msgs/PoseVelocity   
        /j2n6s300_driver/out/actual_joint_torques         10 Hz    : kinova_msgs/JointAngles    
        /j2n6s300_driver/out/cartesian_command            10 Hz    : kinova_msgs/KinovaPose     
        /j2n6s300_driver/out/compensated_joint_torques    10 Hz    : kinova_msgs/JointAngles    
        /j2n6s300_driver/out/joint_angles                 10 Hz    : kinova_msgs/JointAngles    
        /j2n6s300_driver/out/joint_command                10 Hz    : kinova_msgs/JointAngles    
        /j2n6s300_driver/out/joint_state                  10 Hz    : sensor_msgs/JointState     
        /j2n6s300_driver/out/tool_pose                    10 Hz    : geometry_msgs/PoseStamped  
        /j2n6s300_driver/out/tool_wrench                  10 Hz    : geometry_msgs/WrenchStamped
        ```
   * `ft_sensor_data`: Force/Torque sensor data measuring the cutting force and torque
   at 200 Hz.  
   
   * `data`: Processed robot data (see [Instructions](README.md#instructions) for more information).

* The two data streams were not synchronized at the time of collection and a 
post-processing step is required for their synchronization.

* **Note:** The synchronization is a work in progress. 
 
### Dependencies
* Python 2.7+
* Rosbag 
* Matplotlib 
* Numpy 
* Pandas

### Instructions
The `process_data.py` script loads the bagfiles and reorganizes them in CSV files while adding the 
corresponding labels. The CSV files are easier to handle in PyTorch and TensorFlow. To generate them, 
run the following command:
```
# From aml_robot_cutting_dataset/aml_robot_cutting
python2 process_data.py   
``` 
This creates the `data` folder in the root directory, containing all the CSV files for each cut. 
Use the argument `--save_plots` to save the corresponding plots.
