# main.py

from vex import *
import time


# Initialize devices
brain = Brain()
controller_1 = Controller(PRIMARY)
left_motor_a = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
left_motor_b = Motor(Ports.PORT3, GearSetting.RATIO_6_1, True)
left_motor_c = Motor(Ports.PORT4, GearSetting.RATIO_6_1, True)
 
right_motor_a = Motor(Ports.PORT5, GearSetting.RATIO_6_1, False)
right_motor_b = Motor(Ports.PORT12, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT17, GearSetting.RATIO_6_1, False)
 
left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)
High_scoring = Motor(Ports.PORT20)
intake_lower = Motor(Ports.PORT1)
intake_upper = Motor(Ports.PORT13)
mogo_p = DigitalOut(brain.three_wire_port.f)
donker = DigitalOut(brain.three_wire_port.h)
intake_p = DigitalOut(brain.three_wire_port.d)
rotational_sensor = Rotation(Ports.PORT19, False)
rotational_sensor.set_position(0, DEGREES)

# Constants
MSEC_PER_SEC = 1000

# define an enum for intake state
class IntakeState:
    STOPPED = 0
    RUNNING = 1
    STALLED = 2
    FIXINGSTALL = 3

intake_state = IntakeState.STOPPED

# Global variables
reverse_drive = True
high_scoring_running = False
current_direction = FORWARD
high_scoring_mode = False
# Constants
STALL_THRESHOLD = 5       # Adjust as needed
STALL_COUNT = 5
RETRY_LIMIT = 30
MSEC_PER_SEC = 1000
# Define constants for the target angles
HIGH_SCORE_TARGET_ANGLE_SCORE = 300
HIGH_SCORE_TARGET_ANGLE_WAIT = 75
HIGH_SCORE_TARGET_ANGLE_CAPTURE = 25
HIGH_SCORE_TARGET_ANGLE_DOWN = 0
# Global variables
retry_count = 0
consecutive_stall_count = 0
high_scoring_running = False
high_score_stall = False  # Set this accordingly in your main code if needed
high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_DOWN

# Function to set the state of the high scoring motor
def adjust_high_scoring_motor_position():
    global high_score_target_angle

    High_scoring.set_stopping(BRAKE)
    High_scoring.spin_to_position(high_score_target_angle, DEGREES, 30, PERCENT, False)


# Function to set the state of the intake motor
def set_intake_motor_state(direction=FORWARD):
    global intake_state, current_direction
    if intake_state == IntakeState.RUNNING or intake_state == IntakeState.FIXINGSTALL:
        intake_lower.set_velocity(95, PERCENT)
        intake_upper.set_velocity(95, PERCENT)
        intake_lower.spin(direction)
        if intake_state == IntakeState.FIXINGSTALL:
            intake_upper.spin(direction)
        else:
            intake_upper.spin(REVERSE if direction == FORWARD else FORWARD)
        current_direction = direction
    else:
        intake_lower.stop()
        intake_upper.stop()

# Stall detection and handling for the intake motor
def stall_detection_and_handling():
    global intake_state, consecutive_stall_count, retry_count, high_score_stall, high_score_target_angle, high_scoring_running
    global current_direction
    if intake_state == IntakeState.RUNNING or intake_state == IntakeState.STALLED:
        current_velocity = intake_upper.velocity(PERCENT)
        if abs(current_velocity) <= STALL_THRESHOLD:
            #print("Stalled" + str(consecutive_stall_count))
            consecutive_stall_count += 1
        else:
            consecutive_stall_count = 0

        if consecutive_stall_count >= STALL_COUNT:
            #print("Unstaling")
            intake_state = IntakeState.FIXINGSTALL
            # This state will change upper motor in opposite direction
            set_intake_motor_state(current_direction)
            if high_scoring_running:
                high_score_stall = True
                high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_WAIT
                adjust_high_scoring_motor_position()
                high_scoring_running = False
            consecutive_stall_count = 0
            retry_count = RETRY_LIMIT
    else:
        consecutive_stall_count = 0
    if intake_state == IntakeState.FIXINGSTALL:
        if retry_count == 0:
            if high_score_stall:
                high_score_stall = False
                intake_state = IntakeState.STOPPED
                set_intake_motor_state(FORWARD)
            else:
                #print("Fixed")
                intake_state = IntakeState.RUNNING
                set_intake_motor_state(current_direction)
        else:
            #print("Retrying")
            retry_count -= 1


# wait for rotation sensor to fully initialize
wait(30, MSEC)

#Paths
red_left_tomogo = [(-151.774, 126.162), (-132.813, 121.614), (-116.614, 109.405), (-101.657, 95.657), (-87.22, 81.358), (-72.93, 66.912), (-62.038, 56.275)]

# Testing paths
decreasing_x = [(150,00),(100,0), (50,0), (0,0)]
increasing_x = [(0,00),(50,0), (100,0), (0,0)]
#red_left_tomogo = [(-57.389, 70.195), (-57.595, 85.434), (-58.117, 100.664), (-58.991, 115.879), (-59.156, 118.226)]
red_left_totower = [(-56.005, 109.686), (-48.833, 90.678), (-42.278, 71.445), (-35.999, 52.12), (-28.954, 28.954), (-28.954, 28.954)]
red_left_tofirststack = [(-66.948, 66.505), (-64.771, 81.588), (-63.049, 96.73), (-60.55, 111.758), (-59.156, 118.226), (-59.156, 118.226)]
#[(-66.948, 66.505), (-65.755, 81.698), (-63.714, 96.795), (-60.605, 111.714), (-59.156, 118.226), (-59.156, 118.226)]
#[(-66.948, 66.505), (-74.311, 79.794), (-75.997, 94.745), (-69.597, 108.353), (-59.156, 118.226), (-59.156, 118.226)]
red_left_lasttwo = [(-69.531, 148.924), (-57.392, 152.459), (-44.93, 151.127), (-34.453, 144.166), (-27.05, 133.892), (-21.979, 122.263), (-18.617, 110.025), (-16.793, 97.468), (-16.696, 94.821), (-16.696, 94.821)]
#red_left_tofirststack = [ (-59.156, 118.226)]
blue_right_tomogo = [(148.309, 121.108), (131.65, 109.473), (114.99, 97.838), (98.331, 86.203), (81.672, 74.568), (57.543, 57.716), (57.543, 57.716)]
blue_right_tofirststack = [(58.984, 75.725), (58.984, 96.045), (58.984, 101.595), (58.984, 118.947), (58.984, 118.947)]
blue_right_totower =  [(62.345, 117.716), (46.169, 80.438), (38.288, 61.709), (30.311, 43.02), (25.572, 34.448), (25.572, 34.448)]
start_pos_size = -1


test_square = [(-0.949, -137.545), (1.05, -137.464), (3.048, -137.383), (5.047, -137.302), (7.045, -137.221), (9.043, -137.14), (11.042, -137.06), (13.04, -136.979), (15.038, -136.898), (17.037, -136.817), (19.035, -136.736), (21.033, -136.655), (23.032, -136.574), (25.03, -136.493), (27.028, -136.412), (29.027, -136.331), (31.025, -136.251), (33.024, -136.17), (35.022, -136.089), (37.02, -136.008), (39.019, -135.927), (41.017, -135.846), (43.015, -135.765), (45.014, -135.684), (47.012, -135.603), (49.01, -135.522), (51.009, -135.441), (53.007, -135.361), (55.006, -135.28), (57.004, -135.199), (59.002, -135.118), (61.001, -135.037), (62.999, -134.956), (64.997, -134.875), (66.996, -134.794), (68.994, -134.713), (70.992, -134.632), (72.991, -134.551), (74.989, -134.471), (76.988, -134.39), (78.986, -134.309), (80.984, -134.228), (82.983, -134.147), (84.981, -134.066), (86.979, -133.985), (88.978, -133.904), (90.976, -133.823), (92.974, -133.742), (94.973, -133.662), (96.971, -133.581), (98.97, -133.5), (100.968, -133.419), (102.966, -133.338), (104.965, -133.257), (106.963, -133.176), (108.961, -133.095), (110.96, -133.014), (112.958, -132.933), (114.956, -132.852), (116.2, -132.048), (116.197, -130.048), (116.193, -128.048), (116.189, -126.048), (116.185, -124.048), (116.182, -122.048), (116.178, -120.048), (116.174, -118.048), (116.17, -116.048), (116.166, -114.048), (116.163, -112.048), (116.159, -110.048), (116.155, -108.048), (116.151, -106.048), (116.148, -104.048), (116.144, -102.048), (116.14, -100.048), (116.136, -98.048), (116.132, -96.048), (116.129, -94.048), (116.125, -92.048), (116.121, -90.048), (116.117, -88.048), (116.114, -86.048), (116.11, -84.049), (116.106, -82.049), (116.102, -80.049), (116.098, -78.049), (116.095, -76.049), (116.091, -74.049), (116.087, -72.049), (116.083, -70.049), (116.08, -68.049), (116.076, -66.049), (116.072, -64.049), (116.068, -62.049), (116.065, -60.049), (116.061, -58.049), (116.057, -56.049), (116.053, -54.049), (116.049, -52.049), (116.046, -50.049), (116.042, -48.049), (116.038, -46.049), (116.034, -44.049), (116.031, -42.049), (116.027, -40.049), (116.023, -38.049), (116.019, -36.049), (116.015, -34.049), (116.012, -32.049), (116.008, -30.049), (116.004, -28.049), (116.0, -26.049), (115.997, -24.049), (115.993, -22.049), (115.989, -20.049), (115.985, -18.049), (115.982, -16.049), (115.978, -14.049), (115.974, -12.049), (115.97, -10.049), (115.966, -8.049), (115.963, -6.049), (115.959, -4.049), (115.955, -2.049), (115.951, -0.049), (115.948, 1.951), (115.944, 3.951), (115.94, 5.951), (115.936, 7.951), (115.932, 9.951), (115.929, 11.951), (115.925, 13.951), (115.921, 15.951), (115.917, 17.951), (115.914, 19.951), (115.91, 21.951), (115.906, 23.951), (115.902, 25.951), (115.898, 27.951), (115.895, 29.951), (115.891, 31.951), (115.887, 33.951), (115.883, 35.951), (115.88, 37.951), (115.876, 39.951), (115.872, 41.951), (115.868, 43.951), (115.865, 45.951), (115.861, 47.951), (115.857, 49.951), (115.853, 51.951), (115.849, 53.951), (115.846, 55.951), (115.842, 57.951), (115.838, 59.951), (115.834, 61.951), (115.831, 63.951), (115.827, 65.951), (115.823, 67.951), (115.819, 69.951), (115.815, 71.951), (115.812, 73.951), (115.808, 75.951), (115.804, 77.951), (115.8, 79.951), (115.797, 81.951), (115.793, 83.951), (115.789, 85.951), (115.785, 87.951), (115.782, 89.951), (115.778, 91.951), (115.774, 93.951), (115.77, 95.951), (115.766, 97.951), (115.763, 99.951), (115.759, 101.951), (115.755, 103.951), (115.751, 105.951), (115.748, 107.951), (115.744, 109.951), (115.74, 111.951), (115.736, 113.951), (115.732, 115.951), (115.729, 117.951), (114.35, 118.593), (112.35, 118.622), (110.35, 118.651), (108.35, 118.679), (106.351, 118.708), (104.351, 118.737), (102.351, 118.766), (100.351, 118.794), (98.351, 118.823), (96.352, 118.852), (94.352, 118.881), (92.352, 118.909), (90.352, 118.938), (88.352, 118.967), (86.353, 118.995), (84.353, 119.024), (82.353, 119.053), (80.353, 119.082), (78.353, 119.11), (76.354, 119.139), (74.354, 119.168), (72.354, 119.197), (70.354, 119.225), (68.355, 119.254), (66.355, 119.283), (64.355, 119.312), (62.355, 119.34), (60.355, 119.369), (58.356, 119.398), (56.356, 119.427), (54.356, 119.455), (52.356, 119.484), (50.356, 119.513), (48.357, 119.542), (46.357, 119.57), (44.357, 119.599), (42.357, 119.628), (40.357, 119.657), (38.358, 119.685), (36.358, 119.714), (34.358, 119.743), (32.358, 119.772), (30.358, 119.8), (28.359, 119.829), (26.359, 119.858), (24.359, 119.887), (22.359, 119.915), (20.359, 119.944), (18.36, 119.973), (16.36, 120.002), (14.36, 120.03), (12.36, 120.059), (10.361, 120.088), (8.361, 120.117), (6.361, 120.145), (4.361, 120.174), (2.361, 120.203), (0.362, 120.232), (-1.638, 120.26), (-3.638, 120.289), (-5.638, 120.318), (-7.638, 120.346), (-9.637, 120.375), (-11.637, 120.404), (-13.637, 120.433), (-15.637, 120.461), (-17.637, 120.49), (-19.636, 120.519), (-21.636, 120.548), (-23.636, 120.576), (-25.636, 120.605), (-27.636, 120.634), (-29.635, 120.663), (-31.635, 120.691), (-33.635, 120.72), (-35.635, 120.749), (-37.635, 120.778), (-39.634, 120.806), (-41.634, 120.835), (-43.634, 120.864), (-45.634, 120.893), (-47.633, 120.921), (-49.633, 120.95), (-51.633, 120.979), (-53.633, 121.008), (-55.633, 121.036), (-57.632, 121.065), (-59.632, 121.094), (-61.632, 121.123), (-63.632, 121.151), (-65.632, 121.18), (-67.631, 121.209), (-69.631, 121.238), (-71.631, 121.266), (-73.631, 121.295), (-75.631, 121.324), (-77.63, 121.353), (-79.63, 121.381), (-81.63, 121.41), (-83.63, 121.439), (-85.63, 121.468), (-87.629, 121.496), (-89.629, 121.525), (-91.629, 121.554), (-93.629, 121.582), (-95.629, 121.611), (-97.628, 121.64), (-99.628, 121.669), (-101.628, 121.697), (-103.628, 121.726), (-105.628, 121.755), (-107.627, 121.784), (-109.627, 121.812), (-111.627, 121.841), (-113.627, 121.87), (-115.26, 121.52), (-115.297, 119.52), (-115.334, 117.521), (-115.371, 115.521), (-115.408, 113.521), (-115.445, 111.522), (-115.482, 109.522), (-115.519, 107.522), (-115.556, 105.523), (-115.593, 103.523), (-115.63, 101.524), (-115.667, 99.524), (-115.704, 97.524), (-115.741, 95.525), (-115.778, 93.525), (-115.815, 91.525), (-115.852, 89.526), (-115.888, 87.526), (-115.925, 85.526), (-115.962, 83.527), (-115.999, 81.527), (-116.036, 79.527), (-116.073, 77.528), (-116.11, 75.528), (-116.147, 73.528), (-116.184, 71.529), (-116.221, 69.529), (-116.258, 67.529), (-116.295, 65.53), (-116.332, 63.53), (-116.369, 61.53), (-116.406, 59.531), (-116.443, 57.531), (-116.48, 55.531), (-116.517, 53.532), (-116.554, 51.532), (-116.591, 49.532), (-116.628, 47.533), (-116.665, 45.533), (-116.702, 43.533), (-116.739, 41.534), (-116.776, 39.534), (-116.813, 37.534), (-116.849, 35.535), (-116.886, 33.535), (-116.923, 31.535), (-116.96, 29.536), (-116.997, 27.536), (-117.034, 25.536), (-117.071, 23.537), (-117.108, 21.537), (-117.145, 19.538), (-117.182, 17.538), (-117.219, 15.538), (-117.256, 13.539), (-117.293, 11.539), (-117.33, 9.539), (-117.367, 7.54), (-117.404, 5.54), (-117.441, 3.54), (-117.478, 1.541), (-117.515, -0.459), (-117.552, -2.459), (-117.589, -4.458), (-117.626, -6.458), (-117.663, -8.458), (-117.7, -10.457), (-117.737, -12.457), (-117.774, -14.457), (-117.811, -16.456), (-117.847, -18.456), (-117.884, -20.456), (-117.921, -22.455), (-117.958, -24.455), (-117.995, -26.455), (-118.032, -28.454), (-118.069, -30.454), (-118.106, -32.454), (-118.143, -34.453), (-118.18, -36.453), (-118.217, -38.453), (-118.254, -40.452), (-118.291, -42.452), (-118.328, -44.452), (-118.365, -46.451), (-118.402, -48.451), (-118.439, -50.451), (-118.476, -52.45), (-118.513, -54.45), (-118.55, -56.45), (-118.587, -58.449), (-118.624, -60.449), (-118.661, -62.448), (-118.698, -64.448), (-118.735, -66.448), (-118.772, -68.447), (-118.808, -70.447), (-118.845, -72.447), (-118.882, -74.446), (-118.919, -76.446), (-118.956, -78.446), (-118.993, -80.445), (-119.03, -82.445), (-119.067, -84.445), (-119.104, -86.444), (-119.141, -88.444), (-119.178, -90.444), (-119.215, -92.443), (-119.252, -94.443), (-119.289, -96.443), (-119.326, -98.442), (-119.363, -100.442), (-119.4, -102.442), (-119.437, -104.441), (-119.474, -106.441), (-119.511, -108.441), (-119.548, -110.44), (-119.585, -112.44), (-119.622, -114.44), (-119.659, -116.439), (-119.696, -118.439), (-119.733, -120.439), (-119.77, -122.438), (-119.806, -124.438), (-119.843, -126.438), (-119.88, -128.437), (-119.917, -130.437), (-119.954, -132.437), (-119.991, -134.436), (-118.259, -134.699), (-116.259, -134.699), (-114.259, -134.699), (-112.259, -134.699), (-110.259, -134.699), (-108.259, -134.699), (-106.259, -134.699), (-104.259, -134.699), (-102.259, -134.699), (-100.259, -134.699), (-98.259, -134.699), (-96.259, -134.699), (-94.259, -134.699), (-92.259, -134.699), (-90.259, -134.699), (-88.259, -134.699), (-86.259, -134.699), (-84.259, -134.699), (-82.259, -134.699), (-80.259, -134.699), (-78.259, -134.699), (-76.259, -134.699), (-74.259, -134.699), (-72.259, -134.699), (-70.259, -134.699), (-68.259, -134.699), (-66.259, -134.699), (-64.259, -134.699), (-62.259, -134.699), (-60.259, -134.699), (-58.259, -134.699), (-56.259, -134.699), (-54.259, -134.699), (-52.259, -134.699), (-50.259, -134.699), (-48.259, -134.699), (-46.259, -134.699), (-44.259, -134.699), (-42.259, -134.699), (-40.259, -134.699), (-38.259, -134.699), (-36.259, -134.699), (-34.259, -134.699), (-32.259, -134.699), (-30.259, -134.699), (-28.259, -134.699), (-26.259, -134.699), (-24.259, -134.699), (-22.259, -134.699), (-19.92, -134.699), (-19.92, -134.699)]

# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    #urandom.seed(int(random))
      
# Set random seed 
initializeRandomSeed()


def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

#gyro start
gyro = Inertial(Ports.PORT14)
gyro.orientation(OrientationType.YAW)
gyro.calibrate()
gyro.set_rotation(0, DEGREES)
gyro.set_heading(0, DEGREES)
 
 
gear_ratio = 3/4
tolerance = 6
lookahead = 50
current_x = -1
current_y =  -1
previous_right_encoder = 0
previous_left_encoder = 0
forward_velocity = 30
turn_velocity_k = 30
left_velocity = 5
right_velocity = 5
#forward_velocity/100
wheel_circumference = 8.6393798
feet_to_unit = 2.5
gear_ratio = 3/4
current_angle = 0


def leftEncoder():
    return left_drive_smart.position(DEGREES)
 
def rightEncoder():
    return right_drive_smart.position(DEGREES)
 
def update_position():
    global current_x, current_y, current_angle, previous_left_encoder, previous_right_encoder
   
    # Calculate the distance traveled by each wheel
    left_encoder = ((leftEncoder() / 360) * wheel_circumference * gear_ratio) * feet_to_unit
    right_encoder = ((rightEncoder() / 360) * wheel_circumference * gear_ratio) * feet_to_unit
    delta_left = left_encoder - previous_left_encoder
    delta_right = right_encoder - previous_right_encoder
    #print("delta_left: "+ str(delta_left)+" delta_rhgt: " + str(delta_right) + " left_enc: " + str(left_encoder) + " right_enc: " + str(right_encoder))
    # Update previous encoder values
    previous_left_encoder = left_encoder
    previous_right_encoder = right_encoder
   
    current_angle = 2* math.pi - math.radians(gyro.heading(DEGREES))
   
    # Calculate the robot's linear change
    delta_d = (delta_left + delta_right) / 2
   
    current_y += delta_d * math.sin(current_angle)
    current_x += delta_d * math.cos(current_angle)
    #print("x: "+ str(current_x)+" y: " + str(current_y) + " angle: " + str(current_angle))
 
def calculate_lookahead_point(points_list, lookahead_distance):
    global current_x, current_y, start_pos_size, forward_velocity, tolerance
    closest_offset = -1
    lookahead_offset = -1
    closest_distance = float('inf')

    #if len(points_list) == 0:
    #    return 
    min_distance = float('inf')
    min_index = -1  # To keep track of the nearest valid point index

    num_points = len(points_list)  # Number of points to check
    for i in range(num_points-1):
        dist = math.sqrt((points_list[i][0] - current_x) ** 2 + (points_list[i][1] - current_y) ** 2)    
        if dist < tolerance:
            min_index = i
        else:
            break
    if min_index != -1:
        del points_list[:min_index]
        min_index = -1
        num_points = len(points_list)  # Number of points to check

    if len(points_list) == 0:
        return 
    lookahead_point = None
    closest_point = points_list[0]
    for i in range(num_points-1):
        start = points_list[i]
        end = points_list[i + 1]
        segment_length = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        if segment_length == 0:
            continue
        t = ((current_x - start[0]) * (end[0] - start[0]) + (current_y - start[1]) * (end[1] - start[1])) / segment_length ** 2
        t = max(0, min(1, t))
        closest_x = start[0] + t * (end[0] - start[0])
        closest_y = start[1] + t * (end[1] - start[1])
        distance = math.sqrt((closest_x - current_x) ** 2 + (closest_y - current_y) ** 2)

        if len(points_list) == 2 and distance <  2* tolerance:
            closest_point = (points_list[1][0], points_list[1][1])
            del points_list[0]
            break

        if distance < closest_distance:
            closest_distance = distance
            closest_offset = i
            closest_point = (closest_x, closest_y)

        if distance >= lookahead_distance:
            lookahead_offset = i
            lookahead_point = (closest_x, closest_y)
            break

    if closest_offset > 0 and lookahead_point is None:
        #print("Dropping1 :" + str(points_list[:closest_offset]))
        del points_list[:closest_offset]
        closest_offset = 0
    if lookahead_point:
        #print("Dropping2 :" + str(points_list[:lookahead_offset]))
        del points_list[:lookahead_offset]
    return lookahead_point if lookahead_point else closest_point

# Function to calculate drive speeds
def calculate_drive_speeds(lookahead_point, direction):
    global current_x, current_y, current_angle, left_velocity, right_velocity, forward_velocity, turn_velocity_k
    dx = lookahead_point[0] - current_x
    dy = lookahead_point[1] - current_y

    # Calculate the angle to the target point
    point_angle = math.atan2(dy, dx)
    
    # Calculate the angle difference between the current heading and the target point
    point_angle_diff = point_angle - current_angle

    # Normalize the angle difference to be within the range [-π, π]
    if point_angle_diff > math.pi:
        point_angle_diff -= 2 * math.pi
    elif point_angle_diff < -math.pi:
        point_angle_diff += 2 * math.pi

    # Calculate the wheel velocities based on the specified direction
    curr_forward_velocity = forward_velocity * direction
    curr_turn_velocity_k = turn_velocity_k * direction
    left_velocity = curr_forward_velocity - point_angle_diff * curr_turn_velocity_k
    right_velocity = curr_forward_velocity + point_angle_diff * curr_turn_velocity_k

    # Clamp the velocities to the range [-100, 100]
    left_velocity = max(min(left_velocity, 100), -100)
    right_velocity = max(min(right_velocity, 100), -100)


def walk_path(points_list, lookahead_distance, stop_threshold, direction):
    global current_x, current_y, start_pos_size, forward_velocity, turn_velocity_k, left_velocity, right_velocity

    start_pos_size = len(points_list)

    if current_x == -1:
        current_x = points_list[0][0]
        current_y = points_list[0][1]

    running = True
    while running:
        if len(points_list) == 1:
            running = False
            break

        # Calculate the lookahead point
        next_point = calculate_lookahead_point(points_list, lookahead_distance)

        # Calculate drive speeds based on the specified direction
        calculate_drive_speeds(next_point, direction)
        print("x: "+ str(current_x)+" y: " + str(current_y) + " angle: " + str(current_angle) + " lspeed" + str(left_velocity) + " rspeed" + str(right_velocity))

        # Update the robot's position
        update_position()

        # Check if the robot has reached the current target point
        distance_to_point = math.sqrt((points_list[0][0] - current_x) ** 2 + (points_list[0][1] - current_y) ** 2)
        if distance_to_point < stop_threshold:  # Adjust the threshold as needed
            points_list.pop(0)  # Remove the reached point

        # Check if the robot has reached the last point
        if len(points_list) == 0:
            final_distance = math.sqrt((points_list[-1][0] - current_x) ** 2 + (points_list[-1][1] - current_y) ** 2)
            if final_distance < stop_threshold:
                running = False

        # Set motor velocities
        left_drive_smart.set_velocity(left_velocity, PERCENT)
        left_drive_smart.spin(FORWARD)
        right_drive_smart.set_velocity(right_velocity, PERCENT)
        right_drive_smart.spin(FORWARD)

        wait(20, MSEC)

    # Stop motors when path is complete
    left_drive_smart.stop()
    right_drive_smart.stop()

def autonomous_sample(): 
    global current_x, current_y, current_angle
    print("Starting autonomous sample")
    while True:
        update_position()
        print("x: "+ str(current_x)+" y: " + str(current_y) + " angle: " + str(current_angle))
        wait(1, SECONDS)

def autonomous_blue_right():
    autonomous_more_donuts_side(blue_right_tomogo, blue_right_tofirststack, blue_right_totower)

def autonomous_red_left():
    autonomous_more_donuts_side(red_left_tomogo, red_left_tofirststack, red_left_totower)

def autonomous_red_right():
    autonomous_extra_mogo_side(None, None)  #red_right_tomogo*/, nul /*red_right_tofirststack*
        
def autonomous_blue_left():
    pass

def autonomous_extra_mogo_side(tomogo, tofirststack):
    autonomous_empty()

def autonomous_more_donuts_side(tomogo, tofirststack, last_two):
    global intake_state, lookahead

    #pick up intake so ramps drop
    intake_p.set(True)

    # Bring up high scoring motor
    high_score_target_angle = 75
    adjust_high_scoring_motor_position()

    # go to mogo
    walk_path(tomogo, lookahead, tolerance, -1)
    # Capture the mogo
    mogo_p.set(True)

    # start intake to pick up the top donut including the stall code
    intake_state = IntakeState.RUNNING
    set_intake_motor_state(REVERSE)

    # Bring down the intake to knock off the top donut
    intake_p.set(False)
    update_position()
    intake_p.set(True)
    wait(250, MSEC)
    intake_p.set(False)
    walk_path(tofirststack, lookahead, tolerance, 1)
    update_position()
    lookahead = 20
    walk_path(last_two, lookahead, tolerance, -1)

# driver.py 

# Function to display joystick positions (optional)
def display_joystick_positions():
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    #joystick_positions = f"{int(controller_1.axis3.position())} {int(controller_1.axis2.position())}"
    #brain.screen.print(joystick_positions)
    wait(0.1, SECONDS)

def scale_joystick_input(input_value):
    # Normalize the input to the range [-1, 1]
    normalized_input = input_value / 100.0
    # Apply cubic scaling
    scaled_input = normalized_input ** 3
    # Scale back to the range [-100, 100]
    return scaled_input * 100

# Function to set drive motor velocities based on controller input
def set_drive_motor_velocities():
    global reverse_drive
    if controller_1.buttonA.pressing():
        reverse_drive = not reverse_drive
        while controller_1.buttonA.pressing():
            wait(10, MSEC)

    if reverse_drive:
        # Reverse joystick inputs
        left_joystick_y = -controller_1.axis2.position()
        right_joystick_y = -controller_1.axis3.position()
    else:
        # Normal control
        left_joystick_y = controller_1.axis3.position()
        right_joystick_y = controller_1.axis2.position()

    # Apply scaling to joystick inputs
    left_joystick_y = scale_joystick_input(left_joystick_y)
    right_joystick_y = scale_joystick_input(right_joystick_y)

    # Set velocities for left and right drive motors
    left_drive_smart.set_velocity(left_joystick_y, PERCENT)
    if abs(left_joystick_y) < 5:
        left_drive_smart.stop()
    else:
        left_drive_smart.spin(FORWARD)

    right_drive_smart.set_velocity(right_joystick_y, PERCENT)
    if abs(right_joystick_y) < 5:
        right_drive_smart.stop()
    else:
        right_drive_smart.spin(FORWARD)
        
# Function to toggle the high scoring motor
def toggle_high_scoring_motor():
    global high_scoring_running, high_score_target_angle
    if controller_1.buttonLeft.pressing():
        high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_SCORE
        high_scoring_running = False
        while controller_1.buttonLeft.pressing():
            wait(10, MSEC)

    if controller_1.buttonUp.pressing():
        high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_WAIT
        high_scoring_running = False
        while controller_1.buttonLeft.pressing():
            wait(10, MSEC)

    if controller_1.buttonRight.pressing():
        high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_CAPTURE
        high_scoring_running = True
        while controller_1.buttonLeft.pressing():
            wait(10, MSEC)

    if controller_1.buttonDown.pressing():
        high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_DOWN
        high_scoring_running = False
        while controller_1.buttonDown.pressing():
            wait(10, MSEC)

# Function to toggle the intake motor
def toggle_intake_motor():
    global intake_state
    global consecutive_stall_count, retry_count, high_score_stall
    global intake_running

    if controller_1.buttonR1.pressing():

        intake_state = IntakeState.RUNNING if intake_state == IntakeState.STOPPED else IntakeState.STOPPED
        consecutive_stall_count = 0
        retry_count = 0
        high_score_stall = False        

        set_intake_motor_state(FORWARD)
        wait(100, MSEC)  # Debounce delay
        while controller_1.buttonR1.pressing():
            wait(100, MSEC)

    if controller_1.buttonR2.pressing():
        intake_state = IntakeState.RUNNING if intake_state == IntakeState.STOPPED else IntakeState.STOPPED
        consecutive_stall_count = 0
        retry_count = 0
        high_score_stall = False        
        set_intake_motor_state(REVERSE)
        wait(100, MSEC)  # Debounce delay
        while controller_1.buttonR2.pressing():
            wait(100, MSEC)

# Function to handle digital outputs based on controller buttons
def handle_digital_outputs():
    if controller_1.buttonL1.pressing():
        print("Mogo 1")
        mogo_p.set(False)
    if controller_1.buttonL2.pressing():
        print("Mogo 2")
        mogo_p.set(True)
    if controller_1.buttonX.pressing():
        intake_p.set(not intake_p.value())
    if controller_1.buttonY.pressing():
        donker.set(True)
    if controller_1.buttonB.pressing():
        donker.set(False)

# Autonomous function
def autonomous():
    # Autonomous code
    # For example, move forward for a certain distance
    # define a variable slot_no and switch case based on the slot_no
    # to run the corresponding autonomous routine
    #wait(3, SECONDS)
    slot_no = 4
    if slot_no == 1:
        gyro.set_heading(180, DEGREES)
        autonomous_empty()
    elif slot_no == 2:
        gyro.set_heading(180, DEGREES)
        autonomous_blue_right()
    elif slot_no == 3:
        gyro.set_heading(0, DEGREES)
        autonomous_empty()
    elif slot_no == 4:
        gyro.set_heading(180, DEGREES)
        autonomous_red_left()
    elif slot_no == 5:
        gyro.set_heading(0, DEGREES)

        left_drive_smart.spin_to_position(((38/(2.75*(math.pi)))*360), DEGREES, 100, PERCENT)
        right_drive_smart.spin_to_position(((38/(2.75*(math.pi)))*360), DEGREES, 100, PERCENT)
        left_drive_smart.stop()
        right_drive_smart.stop()
        mogo_p.set(True)
        intake_lower.set_velocity(100, PERCENT)
        intake_upper.set_velocity(100, PERCENT)   
# Driver control function
def drivercontrol():
    # Main control loop for driver control
    while True:
        set_drive_motor_velocities()
        toggle_high_scoring_motor()
        adjust_high_scoring_motor_position()
        toggle_intake_motor()
        handle_digital_outputs()
        stall_detection_and_handling()
        wait(20, MSEC)

def autonomous_empty():
    left_drive_smart.set_velocity(95, PERCENT)
    right_drive_smart.set_velocity(95, PERCENT)
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)
    wait(200, MSEC)
    left_drive_smart.stop()
    right_drive_smart.stop()

def autonomous_test():
    global lookahead, tolerance, increasing_x, test_square
    #walk_path(increasing_x, lookahead, tolerance, 1)
    walk_path(test_square, lookahead, tolerance, -1)
    
def unscoring():
    print("Hi")

# Create a Competition object
#competition = Competition(drivercontrol, autonomous)
def main():
    # Any initialization code before the match starts
    print("Running main.py")
    wait(3, SECONDS)
    #mogo_p.set(False)
    #intake_p.set(True)
    #autonomous()
    autonomous_test()
    #intake_p.set(True)
    #drive
    #unscoring()

main()