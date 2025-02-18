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
intake_lower = Motor(Ports.PORT21)
intake_upper = Motor(Ports.PORT13)
mogo_p = DigitalOut(brain.three_wire_port.f)
ejection_p = DigitalOut(brain.three_wire_port.a)
ejection_p.set(False)
donker = DigitalOut(brain.three_wire_port.h)
donker.set(False)
intake_p = DigitalOut(brain.three_wire_port.d)
rotational_sensor = Rotation(Ports.PORT19, True)
rotational_sensor.set_position(0, DEGREES)

left_rotational_sensor = Rotation(Ports.PORT7, True)
right_rotational_sensor = Rotation(Ports.PORT6, False)
left_rotational_sensor.set_position(0, DEGREES)
right_rotational_sensor.set_position(0, DEGREES)


# Constants
MSEC_PER_SEC = 1000

# define an enum for intake state
class IntakeState:
    STOPPED = 0
    RUNNING = 1
    STALLED = 2
    FIXINGSTALL = 3

class RingType:
    NONE = 0
    RED = 1
    BLUE = 2

MIN_REJECT_SIZE=5000
# Define the color signatures based of the config copied below
REDD = Signature(1, 9907, 12073, 10990, -1991, -879, -1435, 2.5, 0)
BLUEE = Signature(2, -4415, -3205, -3810, 5461, 8989, 7225, 2.5, 0)
'''{
  "brightness": 50,
  "signatures": [
    {
      "name": "REDD",
      "parameters": {
        "uMin": 9907,
        "uMax": 12073,
        "uMean": 10990,
        "vMin": -1991,
        "vMax": -879,
        "vMean": -1435,
        "rgb": 5973535,
        "type": 0,
        "name": "REDD"
      },
      "range": 2.5
    },
    {
      "name": "BLUEE",
      "parameters": {
        "uMin": -4415,
        "uMax": -3205,
        "uMean": -3810,
        "vMin": 5461,
        "vMax": 8989,
        "vMean": 7225,
        "rgb": 1714760,
        "type": 0,
        "name": "BLUEE"
      },
      "range": 2.5
    }
  ],
  "codes": []
}'''
Color_sensor = Optical(Ports.PORT15)
Color_sensor.set_light_power(100)
# Initialize eject_counter
eject_counter = 0
eject_object = RingType.NONE

intake_state = IntakeState.STOPPED

# Global variables
slow_drive = False
high_scoring_running = False
current_direction = FORWARD
high_scoring_mode = False
# Constants
STALL_THRESHOLD = 0       # Adjust as needed
STALL_COUNT = 20
RETRY_LIMIT = 15
EJECT_LIMIT= 20
MSEC_PER_SEC = 1000
# Define constants for the target angles
HIGH_SCORE_TARGET_ANGLE_SCORE = -430
HIGH_SCORE_TARGET_ANGLE_WAIT = -200
HIGH_SCORE_TARGET_ANGLE_CAPTURE = -60
HIGH_SCORE_TARGET_ANGLE_DOWN = 0
MAX_CAPTURE_POSITION_COUNT = 51
# Global variables
retry_count = 0
consecutive_stall_count = 0
high_scoring_running = False
high_score_stall = False  # Set this accordingly in your main code if needed
high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_DOWN
capture_position_counter = 0

def set_high_score_angle(angle):
    global high_score_target_angle, capture_position_counter
    if (angle == HIGH_SCORE_TARGET_ANGLE_CAPTURE):
        high_score_target_angle = angle
        capture_position_counter = MAX_CAPTURE_POSITION_COUNT
    elif (angle == HIGH_SCORE_TARGET_ANGLE_SCORE) and high_score_target_angle <= angle:
        high_score_target_angle -= 40
    else:
        high_score_target_angle = angle

# Function to set the state of the high scoring motor
def adjust_high_scoring_motor_position():
    global high_score_target_angle, capture_position_counter

    #print(" Rotating angle is " + str(rotational_sensor.position(DEGREES)) + "high score motor angle is " + str(High_scoring.position(DEGREES)))
    High_scoring.set_stopping(BRAKE)
    High_scoring.set_velocity(100, PERCENT)
    if high_score_target_angle == HIGH_SCORE_TARGET_ANGLE_CAPTURE and abs(High_scoring.position(DEGREES) - rotational_sensor.position(DEGREES)) > 2:
        if capture_position_counter > 0:
            capture_position_counter -= 1
        else:
            print("Chaning motor position")
            print(" Rotating angle is " + str(rotational_sensor.position(DEGREES)) + "high score motor angle is " + str(High_scoring.position(DEGREES)))
            High_scoring.set_position(rotational_sensor.position(DEGREES), DEGREES)
    High_scoring.spin_to_position(high_score_target_angle, DEGREES, 30, PERCENT, False)

def auto_adjust_high_scoring_motor_position():
    global high_score_target_angle, capture_position_counter

    stall_detection_and_handling()

    #print(" Rotating angle is " + str(rotational_sensor.position(DEGREES)) + "high score motor angle is " + str(High_scoring.position(DEGREES)))
    High_scoring.set_stopping(BRAKE)
    High_scoring.set_velocity(100, PERCENT)
    if high_score_target_angle == HIGH_SCORE_TARGET_ANGLE_CAPTURE and abs(High_scoring.position(DEGREES) - rotational_sensor.position(DEGREES)) > 2:
        if capture_position_counter > 0:
            capture_position_counter -= 1
        else:
            print("Chaning motor position")
            print(" Rotating angle is " + str(rotational_sensor.position(DEGREES)) + "high score motor angle is " + str(High_scoring.position(DEGREES)))
            High_scoring.set_position(rotational_sensor.position(DEGREES), DEGREES)
    High_scoring.spin_to_position(high_score_target_angle, DEGREES, 30, PERCENT, False)
    while (High_scoring.position(DEGREES) != high_score_target_angle):
        stall_detection_and_handling()

# Function to set the state of the intake motor
def set_intake_motor_state(direction=FORWARD):
    global intake_state, current_direction, eject_counter
    if intake_state == IntakeState.RUNNING or intake_state == IntakeState.FIXINGSTALL:
        intake_lower.set_velocity(90, PERCENT)
        intake_upper.set_velocity(90, PERCENT)
        intake_lower.spin(direction)
        if intake_state == IntakeState.FIXINGSTALL:
            print("Intake motor state is fixing stall")
            intake_upper.spin(direction)
        else:
            intake_upper.spin(REVERSE if direction == FORWARD else FORWARD)
        current_direction = direction
    else:
        intake_lower.stop()
        intake_upper.stop()

# Stall detection and handling for the intake motor
def stall_detection_and_handling():
    global intake_state, consecutive_stall_count, retry_count, high_score_stall, high_score_target_angle, high_scoring_running, eject_counter
    global current_direction
    if intake_state == IntakeState.RUNNING or intake_state == IntakeState.STALLED:
        if intake_state == IntakeState.RUNNING and eject_counter > 0:
                eject_counter = eject_counter - 1
                print("Decremeting eject counter " + str(eject_counter))
                if eject_counter == 0:
                    print("stopping the motor momentarily")
                    intake_state = IntakeState.STOPPED
                    set_intake_motor_state(current_direction)
                    wait(100, MSEC)
                    #intake_state = IntakeState.RUNNING
                    #set_intake_motor_state(current_direction)
        current_velocity = intake_upper.velocity(PERCENT)
        if abs(current_velocity) <= STALL_THRESHOLD:
            #print("Stalled" + str(consecutive_stall_count))
            consecutive_stall_count += 1
        else:
            consecutive_stall_count = 0

        if consecutive_stall_count >= STALL_COUNT:
            print("Unstaling")
            intake_state = IntakeState.FIXINGSTALL
            # This state will change upper motor in opposite direction
            set_intake_motor_state(current_direction)
            if high_scoring_running:
                high_score_stall = True
                set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_WAIT)
                adjust_high_scoring_motor_position()
            consecutive_stall_count = 0
            retry_count = RETRY_LIMIT
    else:
        consecutive_stall_count = 0
    if intake_state == IntakeState.FIXINGSTALL:
        if retry_count == 0:
            if high_score_stall:
                print("Stoppping because of high stall")
                high_score_stall = False
                intake_state = IntakeState.STOPPED
                set_intake_motor_state(FORWARD)
            else:
                print("Fixed")
                intake_state = IntakeState.RUNNING
                set_intake_motor_state(current_direction)
        else:
            #print("Retrying")
            retry_count -= 1


# wait for rotation sensor to fully initialize
wait(30, MSEC)


#Paths
red_left_tomogo = [(-151.774, 126.162), (-146.975, 127.301), (-142.079, 126.393), (-137.475, 124.457), (-133.118, 122.009), (-128.948, 119.253), (-124.916, 116.296), (-121.0, 113.188), (-117.168, 109.976), (-113.407, 106.682), (-109.703, 103.323), (-106.048, 99.911), (-102.43, 96.461), (-98.847, 92.974), (-95.288, 89.461), (-91.75, 85.929), (-88.228, 82.379), (-84.715, 78.821), (-81.208, 75.258), (-77.699, 71.695), (-74.183, 68.141), (-70.649, 64.603), (-67.087, 61.094), (-62.038, 56.275), (-62.038, 56.275)]
red_left_tofirststack = [(-66.948, 66.505), (-64.771, 81.588), (-63.049, 96.73), (-60.55, 111.758), (-59.156, 118.226), (-59.156, 118.226)]
red_left_totower = [(-56.005, 109.686), (-55.187, 107.861), (-54.426, 106.011), (-53.718, 104.141), (-53.062, 102.251), (-52.459, 100.345), (-51.91, 98.421), (-51.418, 96.483), (-50.985, 94.531), (-50.614, 92.565), (-50.31, 90.589), (-50.077, 88.602), (-49.92, 86.609), (-49.844, 84.61), (-49.855, 82.611), (-49.96, 80.614), (-50.165, 78.624), (-50.476, 76.649), (-50.898, 74.694), (-51.438, 72.769), (-52.099, 70.882), (-52.883, 69.042), (-53.793, 67.261), (-54.822, 65.547), (-55.972, 63.912), (-56.915, 62.728), (-56.915, 62.728)]
red_left_lasttwo = [(-48.378, 156.517), (-46.712, 155.41), (-45.102, 154.225), (-43.546, 152.968), (-42.048, 151.643), (-40.605, 150.258), (-39.218, 148.818), (-37.888, 147.324), (-36.613, 145.783), (-35.396, 144.196), (-34.235, 142.568), (-33.131, 140.901), (-32.085, 139.196), (-31.096, 137.458), (-30.168, 135.687), (-29.298, 133.886), (-28.488, 132.057), (-27.742, 130.202), (-27.057, 128.323), (-26.436, 126.422), (-25.882, 124.5), (-25.394, 122.561), (-24.973, 120.606), (-24.622, 118.637), (-24.343, 116.656), (-24.136, 114.667), (-24.002, 112.672), (-23.943, 110.673), (-23.962, 108.673), (-24.057, 106.676), (-24.229, 104.683), (-24.479, 102.699), (-24.811, 100.727), (-25.221, 98.769), (-25.709, 96.83), (-26.274, 94.912), (-26.917, 93.018), (-27.635, 91.152), (-28.427, 89.316), (-29.292, 87.512), (-30.227, 85.744), (-31.23, 84.014), (-32.298, 82.323), (-33.428, 80.673), (-34.149, 79.681), (-34.149, 79.681)]
first_red_left_4 = [(-38.418, 106.242), (-38.361, 108.24), (-38.381, 110.238), (-38.496, 112.234), (-38.698, 114.222), (-39.011, 116.196), (-39.423, 118.152), (-39.944, 120.081), (-40.582, 121.976), (-41.329, 123.829), (-42.187, 125.634), (-43.158, 127.381), (-44.235, 129.065), (-45.408, 130.682), (-46.672, 132.231), (-48.025, 133.702), (-49.454, 135.1), (-50.949, 136.426), (-52.506, 137.679), (-54.118, 138.861), (-55.775, 139.979), (-57.476, 141.029), (-59.211, 142.021), (-60.978, 142.955), (-62.773, 143.836), (-64.591, 144.665), (-66.43, 145.448), (-68.289, 146.184), (-70.162, 146.882), (-72.05, 147.538), (-73.95, 148.159), (-75.861, 148.747), (-77.782, 149.301), (-79.711, 149.825), (-81.647, 150.323), (-83.589, 150.793), (-85.538, 151.238), (-87.492, 151.66), (-89.45, 152.061), (-91.413, 152.442), (-93.379, 152.802), (-95.349, 153.144), (-97.321, 153.469), (-99.296, 153.778), (-101.273, 154.071), (-103.252, 154.351), (-105.234, 154.617), (-107.217, 154.87), (-109.201, 155.11), (-111.187, 155.339), (-113.174, 155.557), (-115.162, 155.765), (-117.151, 155.964), (-119.141, 156.153), (-121.132, 156.334), (-123.123, 156.507), (-125.115, 156.672), (-127.108, 156.831), (-129.101, 156.982), (-131.095, 157.127), (-133.089, 157.266), (-135.084, 157.4), (-137.079, 157.528), (-139.074, 157.652), (-141.069, 157.771), (-143.065, 157.886), (-145.061, 157.998), (-147.057, 158.106), (-149.053, 158.21), (-151.049, 158.312), (-153.046, 158.411), (-155.043, 158.507), (-157.039, 158.602), (-159.036, 158.694), (-161.033, 158.785), (-163.03, 158.875), (-165.027, 158.964), (-167.024, 159.051), (-169.021, 159.139), (-171.018, 159.225), (-171.42, 159.243), (-171.42, 159.243)]
red_left_back_4 = [(-171.42, 159.243), (-169.42, 159.268), (-167.42, 159.293), (-165.42, 159.318), (-163.42, 159.342), (-161.42, 159.365), (-159.42, 159.387), (-157.42, 159.408), (-155.421, 159.428), (-153.421, 159.446), (-151.421, 159.463), (-149.421, 159.479), (-147.421, 159.492), (-145.421, 159.503), (-143.421, 159.511), (-141.421, 159.516), (-139.421, 159.516), (-137.421, 159.513), (-135.421, 159.505), (-133.421, 159.493), (-131.421, 159.476), (-129.421, 159.455), (-127.421, 159.433), (-125.421, 159.41), (-123.422, 159.387), (-121.422, 159.366), (-119.422, 159.346), (-117.422, 159.329), (-115.422, 159.313), (-113.422, 159.299), (-111.422, 159.287), (-109.422, 159.277), (-107.422, 159.269), (-105.422, 159.261), (-103.422, 159.256), (-101.422, 159.251), (-99.422, 159.247), (-97.422, 159.245), (-95.422, 159.243), (-92.961, 159.243), (-92.961, 159.243)]

blue_right_tomogo = [(abs(x), y) for x, y in red_left_tomogo]
blue_right_tofirststack = [(abs(x), y) for x, y in red_left_tofirststack]
blue_right_totower = [(abs(x), y) for x, y in red_left_totower]
blue_right_lasttwo = [(abs(x), y) for x, y in red_left_lasttwo]
first_blue_right_4 =[(abs(x), y) for x, y in first_red_left_4]
blue_right_back_4 = [(abs(x), y) for x, y in red_left_back_4]

blue_left_tomogo = [(abs(x), -y) for x, y in red_left_tomogo]
blue_left_tofirststack = [(abs(x), -y) for x, y in red_left_tofirststack]
blue_left_totower = [(abs(x), -y) for x, y in red_left_totower]
blue_left_lasttwo = [(abs(x), -y) for x, y in red_left_lasttwo]
first_blue_left_4 =[(abs(x), -y) for x, y in first_red_left_4]
blue_left_back_4 = [(abs(x), -y) for x, y in red_left_back_4]

red_right_tomogo = [((x), -y) for x, y in red_left_tomogo]
red_right_tofirststack = [((x), -y) for x, y in red_left_tofirststack]
red_right_totower = [((x), -y) for x, y in red_left_totower]
red_right_lasttwo = [((x), -y) for x, y in red_left_lasttwo]
first_red_right_4 =[((x), -y) for x, y in first_red_left_4]
red_right_back_4 = [((x), -y) for x, y in red_left_back_4]


# Testing paths
decreasing_x = [(150,00),(100,0), (50,0), (0,0)]
#increasing_x = increasing_x_points = [(x, 0) for x in range(0, 200, 10)]

#[(-66.948, 66.505), (-65.755, 81.698), (-63.714, 96.795), (-60.605, 111.714), (-59.156, 118.226), (-59.156, 118.226)]
#[(-66.948, 66.505), (-74.311, 79.794), (-75.997, 94.745), (-69.597, 108.353), (-59.156, 118.226), (-59.156, 118.226)]
#red_left_tofirststack = [ (-59.156, 118.226)]
start_pos_size = -1

p1redright = [(-161.178, -60.913), (-159.178, -60.896), (-157.178, -60.878), (-155.178, -60.861), (-153.178, -60.843)] # ,(-151.178, -60.826), (-149.178, -60.808), (-147.178, -60.791),(-145.178, -60.773), (-143.178, -60.756), (-141.179, -60.738), (-139.179, -60.72), (-137.179, -60.703), (-135.179, -60.685), (-133.179, -60.668), (-131.179, -60.65), (-129.179, -60.633), (-127.179, -60.615), (-125.179, -60.598), (-123.179, -60.58), (-121.179, -60.563), (-119.179, -60.545), (-117.179, -60.527), (-115.18, -60.51), (-113.18, -60.492)
p2redright = [(-102.342, -58.793), (-100.343, -58.837), (-98.343, -58.881), (-96.344, -58.925), (-94.344, -58.969), (-92.345, -59.013), (-90.345, -59.057), (-88.346, -59.101), (-86.346, -59.145), (-84.347, -59.189), (-82.347, -59.233), (-80.347, -59.277), (-78.348, -59.321), (-76.348, -59.364), (-74.349, -59.408), (-72.349, -59.452), (-70.35, -59.496), (-68.35, -59.54), (-66.351, -59.584), (-64.351, -59.628), (-62.352, -59.672), (-60.352, -59.716), (-58.353, -59.76), (-56.353, -59.804), (-54.108, -59.853), (-54.108, -59.853)]
p3redright = [(-54.108, -59.853), (-54.267, -61.847), (-54.427, -63.84), (-54.586, -65.834), (-54.746, -67.828), (-54.905, -69.821), (-55.065, -71.815), (-55.224, -73.808), (-55.384, -75.802), (-55.543, -77.796), (-55.703, -79.789), (-55.862, -81.783), (-56.022, -83.777), (-56.181, -85.77), (-56.341, -87.764), (-56.5, -89.757), (-56.66, -91.751), (-56.819, -93.745), (-56.979, -95.738), (-57.138, -97.732), (-57.298, -99.726), (-57.457, -101.719), (-57.616, -103.713), (-57.776, -105.707), (-57.935, -107.7), (-58.095, -109.694), (-58.254, -111.687), (-58.414, -113.681), (-58.573, -115.675), (-58.733, -117.668), (-58.892, -119.662), (-59.052, -121.656), (-59.211, -123.649), (-59.408, -126.11), (-59.408, -126.11)]
p4redright = [(-59.408, -126.11), (-58.758, -144.674), (-60.758, -144.688), (-62.758, -144.701), (-64.758, -144.714), (-66.758, -144.727), (-68.758, -144.741), (-70.758, -144.754), (-72.758, -144.767), (-74.758, -144.78), (-76.758, -144.794), (-78.758, -144.807), (-80.757, -144.82), (-82.757, -144.833), (-84.757, -144.847), (-86.757, -144.86), (-88.757, -144.873), (-90.757, -144.886), (-92.757, -144.9), (-94.757, -144.913), (-96.757, -144.926), (-98.757, -144.939), (-100.757, -144.953), (-102.757, -144.966), (-104.757, -144.979), (-106.757, -144.992), (-108.757, -145.006), (-110.757, -145.019), (-112.757, -145.032), (-114.757, -145.045), (-116.757, -145.059), (-118.757, -145.072), (-120.757, -145.085), (-122.757, -145.098), (-124.757, -145.112), (-126.756, -145.125), (-128.756, -145.138), (-130.756, -145.151)] # , (-132.756, -145.165), (-134.756, -145.178), (-136.795, -145.191), (-136.795, -145.191)
#p5redright = [(-136.795, -145.191), (-134.83, -144.819), (-132.865, -144.447), (-130.9, -144.074), (-128.935, -143.702), (-126.97, -143.33), (-125.005, -142.958), (-123.04, -142.586), (-121.075, -142.213), (-119.109, -141.841), (-117.144, -141.469), (-115.179, -141.097), (-113.214, -140.724), (-111.249, -140.352), (-109.284, -139.98), (-107.319, -139.608), (-105.354, -139.236), (-103.389, -138.863), (-101.424, -138.491), (-99.459, -138.119), (-97.494, -137.747), (-95.529, -137.375), (-93.564, -137.002), (-91.599, -136.63), (-89.634, -136.258), (-87.669, -135.886), (-85.703, -135.513), (-83.738, -135.141), (-81.773, -134.769), (-79.808, -134.397), (-77.843, -134.025), (-75.878, -133.652), (-73.913, -133.28), (-71.948, -132.908), (-69.983, -132.536), (-68.018, -132.164), (-66.053, -131.791), (-64.088, -131.419), (-62.123, -131.047), (-60.158, -130.675), (-58.193, -130.302), (-56.228, -129.93), (-54.263, -129.558), (-52.297, -129.186), (-50.332, -128.814), (-48.367, -128.441), (-46.402, -128.069), (-44.437, -127.697), (-42.472, -127.325), (-40.507, -126.953)] #, (-38.542, -126.58), (-36.577, -126.208), (-34.612, -125.836), (-31.788, -125.301), (-31.788, -125.301)
#p6redright = [(-40.507, -126.953), (-42.047, -125.676), (-43.586, -124.4), (-45.126, -123.123), (-46.665, -121.846), (-48.205, -120.57), (-49.744, -119.293), (-51.284, -118.017), (-52.823, -116.74), (-54.363, -115.463), (-55.902, -114.187), (-57.442, -112.91), (-58.982, -111.633), (-60.521, -110.357), (-62.061, -109.08), (-63.6, -107.803), (-65.14, -106.527), (-66.679, -105.25), (-68.219, -103.974), (-69.758, -102.697), (-71.298, -101.42), (-72.837, -100.144), (-74.377, -98.867), (-75.917, -97.59), (-77.456, -96.314), (-78.996, -95.037), (-80.535, -93.76), (-82.075, -92.484), (-83.614, -91.207), (-85.154, -89.931), (-86.693, -88.654), (-88.233, -87.377), (-89.772, -86.101), (-91.312, -84.824), (-92.851, -83.547), (-94.391, -82.271), (-95.931, -80.994), (-97.47, -79.717), (-99.01, -78.441), (-99.692, -77.875), (-99.692, -77.875)]
p7redright = [(-130.756, -145.151), (-129.439, -143.646), (-128.123, -142.14), (-126.806, -140.635), (-125.489, -139.129), (-124.173, -137.624), (-122.856, -136.118), (-121.539, -134.613), (-120.223, -133.107), (-118.906, -131.602), (-117.589, -130.097), (-116.272, -128.591), (-114.956, -127.086), (-113.639, -125.58), (-112.322, -124.075), (-111.006, -122.569), (-109.689, -121.064), (-108.372, -119.559), (-107.056, -118.053), (-105.739, -116.548), (-104.422, -115.042), (-103.106, -113.537), (-101.789, -112.031), (-100.472, -110.526), (-99.156, -109.02), (-97.839, -107.515), (-96.522, -106.01), (-95.206, -104.504), (-93.889, -102.999), (-92.572, -101.493), (-91.256, -99.988), (-89.939, -98.482), (-88.622, -96.977), (-87.305, -95.472), (-85.989, -93.966), (-84.672, -92.461), (-83.355, -90.955), (-82.039, -89.45), (-80.722, -87.944), (-79.405, -86.439), (-78.089, -84.933), (-76.772, -83.428), (-75.455, -81.923), (-74.139, -80.417), (-72.822, -78.912), (-71.505, -77.406), (-70.189, -75.901), (-68.872, -74.395), (-67.555, -72.89), (-66.239, -71.384), (-64.922, -69.879), (-63.605, -68.374), (-62.289, -66.868), (-60.972, -65.363), (-59.655, -63.857), (-58.338, -62.352), (-57.022, -60.846), (-55.705, -59.341), (-54.388, -57.836), (-53.072, -56.33), (-51.755, -54.825), (-50.438, -53.319), (-49.122, -51.814)] #, (-47.805, -50.308), (-46.488, -48.803), (-45.172, -47.297), (-43.855, -45.792), (-42.538, -44.287), (-41.222, -42.781), (-39.905, -41.276), (-38.588, -39.77), (-37.146, -38.121), (-37.146, -38.121)
#p6redright = [(-31.788, -125.301), (-31.804, -123.301), (-31.819, -121.301), (-31.835, -119.301), (-31.85, -117.301), (-31.866, -115.301), (-31.881, -113.301), (-31.897, -111.301), (-31.912, -109.301), (-31.928, -107.302), (-31.944, -105.302), (-31.959, -103.302), (-31.975, -101.302), (-31.99, -99.302), (-32.006, -97.302), (-32.021, -95.302), (-32.037, -93.302), (-32.052, -91.302), (-32.068, -89.302), (-32.084, -87.302), (-32.099, -85.302), (-32.115, -83.302), (-32.13, -81.302), (-32.146, -79.302), (-32.161, -77.302), (-32.177, -75.303), (-32.193, -73.303), (-32.208, -71.303), (-32.224, -69.303), (-32.239, -67.303), (-32.255, -65.303), (-32.27, -63.303), (-32.286, -61.303), (-32.301, -59.303), (-32.317, -57.303), (-32.333, -55.303), (-32.348, -53.303), (-32.364, -51.303), (-32.375, -49.782), (-32.375, -49.782)]

p1blueleft = [(abs(x), y) for x, y in p1redright]
p2blueleft = [(abs(x), y) for x, y in p2redright]
p3blueleft = [(abs(x), y) for x, y in p3redright]
p4blueleft = [(abs(x), y) for x, y in p4redright]
p7blueleft = [(abs(x), y) for x, y in p7redright]




straight_line_test = [(0,0), (5, 0), (10, 0), (15, 0), (20, 0), (25, 0), (30, 0), (35, 0), (45, 0), (50, 0)]



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
gyro = Inertial(Ports.PORT16)
gyro.orientation(OrientationType.PITCH)
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
robot_not_walking = 0
MAX_WAIT_FOR_NO_WALK= 20
forward_velocity = 40
turn_velocity_k = 40
left_velocity = 5
right_velocity = 5
#forward_velocity/100
wheel_circumference = 8.6393798
feet_to_unit = 2.5
gear_ratio = 3/4
current_angle = 0

def leftEncoder():
    global left_rotational_sensor
    return left_rotational_sensor.position(DEGREES)

def rightEncoder():
    global right_rotational_sensor
    return right_rotational_sensor.position(DEGREES)
 
def update_position():
    global current_x, current_y, current_angle, previous_left_encoder, previous_right_encoder, robot_not_walking

    # Calculate the distance traveled by each wheel
    left_encoder = ((leftEncoder() / 360) * wheel_circumference * gear_ratio) * feet_to_unit
    right_encoder = ((rightEncoder() / 360) * wheel_circumference * gear_ratio) * feet_to_unit
    delta_left = left_encoder - previous_left_encoder
    delta_right = right_encoder - previous_right_encoder
    #print("delta_left: "+ str(delta_left)+" delta_rhgt: " + str(delta_right) + " left_enc: " + str(left_encoder) + " right_enc: " + str(right_encoder))
    # Update previous encoder values

    if delta_left == delta_right and delta_left == 0:
        robot_not_walking = robot_not_walking + 1
    else:
        robot_not_walking = 0
    previous_left_encoder = left_encoder
    previous_right_encoder = right_encoder
   
    current_angle = 2* math.pi - math.radians(gyro.heading(DEGREES))
   
    # Calculate the robot's linear change
    delta_d = (delta_left + delta_right) / 2
   
    current_y += delta_d * math.sin(current_angle)
    current_x += delta_d * math.cos(current_angle)
    #print("x: "+ str(current_x)+" y: " + str(current_y) + " angle: " + str(current_angle))

def calculate_lookahead_point(points_list, lookahead_distance):
    global current_x, current_y, tolerance
    closest_offset = -1
    lookahead_offset = -1
    closest_distance = float('inf')

    if len(points_list) == 0:
        return None
   
    num_points = len(points_list)
    search_range = min(40, num_points - 1)  # Limit search to the next 40 points

    # Remove points that are within the tolerance range
    min_index = -1
    for i in range(search_range):
        dist = math.sqrt((points_list[i][0] - current_x) ** 2 + (points_list[i][1] - current_y) ** 2)
        if dist < tolerance:
            min_index = i
        else:
            break
   
    if min_index != -1:
        del points_list[:min_index + 1]
        num_points = len(points_list)
        search_range = min(20, num_points - 1)

    if len(points_list) == 0:
        return None

    lookahead_point = None
    closest_point = points_list[0]

    # Search within the limited range
    for i in range(search_range):
        start = points_list[i]
        end = points_list[i + 1]
        segment_length = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
        if segment_length == 0:
            continue

        # Find closest point on segment
        t = ((current_x - start[0]) * (end[0] - start[0]) + (current_y - start[1]) * (end[1] - start[1])) / segment_length ** 2
        t = max(0, min(1, t))
        closest_x = start[0] + t * (end[0] - start[0])
        closest_y = start[1] + t * (end[1] - start[1])
        distance = math.sqrt((closest_x - current_x) ** 2 + (closest_y - current_y) ** 2)

        if len(points_list) == 2 and distance < 2 * tolerance:
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

    # Remove already processed points
    if closest_offset > 0 and lookahead_point is None:
        del points_list[:closest_offset]
    if lookahead_point:
        del points_list[:lookahead_offset]

    return lookahead_point if lookahead_point else closest_point

# Function to calculate drive speeds
def calculate_drive_speeds(lookahead_point, direction):
    global current_x, current_y, current_angle, left_velocity, right_velocity, forward_velocity, turn_velocity_k
    dx = lookahead_point[0] - current_x
    dy = lookahead_point[1] - current_y

    # Calculate the angle to the target point
    point_angle = math.atan2(dy, dx)
   
    # Adjust the current angle based on the direction
    adjusted_current_angle = current_angle
    if direction == -1:
        adjusted_current_angle += math.pi  # Add 180 degrees (π radians) to the current angle

    # Normalize the adjusted current angle to be within the range [-π, π]
    adjusted_current_angle = (adjusted_current_angle + math.pi) % (2 * math.pi) - math.pi

    # Calculate the angle difference between the adjusted current heading and the target point
    point_angle_diff = point_angle - adjusted_current_angle


    # Normalize the angle difference to be within the range [-π, π]
    if point_angle_diff > math.pi:
        point_angle_diff -= 2 * math.pi
    elif point_angle_diff < -math.pi:
        point_angle_diff += 2 * math.pi

    #point_angle_diff = (point_angle_diff + math.pi) % (2 * math.pi) - math.pi

    # Calculate the wheel velocities based on the specified direction
    curr_forward_velocity = forward_velocity * direction
    curr_turn_velocity_k = turn_velocity_k
    left_velocity = curr_forward_velocity - point_angle_diff * curr_turn_velocity_k
    right_velocity = curr_forward_velocity + point_angle_diff * curr_turn_velocity_k

    # Clamp the velocities to the range [-100, 100]
    left_velocity = max(min(left_velocity, 100), -100)
    right_velocity = max(min(right_velocity, 100), -100)

    global current_x, current_y, current_angle, left_velocity, right_velocity, forward_velocity, turn_velocity_k
    dx = lookahead_point[0] - current_x
    dy = lookahead_point[1] - current_y

    # Calculate the angle to the target point
    point_angle = math.atan2(dy, dx)
   
    # Adjust the current angle based on the direction
    adjusted_current_angle = current_angle
    if direction == -1:
        adjusted_current_angle += math.pi  # Add 180 degrees (π radians) to the current angle

    # Normalize the adjusted current angle to be within the range [-π, π]
    adjusted_current_angle = (adjusted_current_angle + math.pi) % (2 * math.pi) - math.pi

    # Calculate the angle difference between the adjusted current heading and the target point
    point_angle_diff = point_angle - adjusted_current_angle


    # Normalize the angle difference to be within the range [-π, π]
    if point_angle_diff > math.pi:
        point_angle_diff -= 2 * math.pi
    elif point_angle_diff < -math.pi:
        point_angle_diff += 2 * math.pi

    #point_angle_diff = (point_angle_diff + math.pi) % (2 * math.pi) - math.pi

    # Calculate the wheel velocities based on the specified direction
    curr_forward_velocity = forward_velocity * direction
    curr_turn_velocity_k = turn_velocity_k
    left_velocity = curr_forward_velocity - point_angle_diff * curr_turn_velocity_k
    right_velocity = curr_forward_velocity + point_angle_diff * curr_turn_velocity_k

    # Clamp the velocities to the range [-100, 100]
    left_velocity = max(min(left_velocity, 100), -100)
    right_velocity = max(min(right_velocity, 100), -100)



def pidTurn(robot_angle, p = 0.45):
    original = robot_angle
    global gyro, left_drive_smart, right_drive_smart
    robot_angle = gyro.rotation(DEGREES) + robot_angle
    error = robot_angle - gyro.heading(DEGREES)
    print((gyro.rotation(DEGREES), robot_angle, error))
    left_drive_smart.set_velocity(p * error, PERCENT)
    right_drive_smart.set_velocity(-p * error, PERCENT)
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)
   
    while abs(error) > 1.3:
        update_position()
        error = robot_angle - gyro.rotation(DEGREES)
        if (abs(error) < 10): p = 0.7
        if (abs(error) < 7): p = 0.8
        if (abs(error) < 5): p = 0.9
        if (abs(error) < 2.5): p = 1.4
        left_drive_smart.set_velocity(p * error, PERCENT)
        right_drive_smart.set_velocity(-p * error, PERCENT)
       
        wait(200, MSEC)
       
        print(( error))

    left_drive_smart.stop()
    right_drive_smart.stop()
    wait(100, MSEC)

def pidTurnToAngle(robot_angle, p = 0.45):
    original = robot_angle
    global gyro, left_drive_smart, right_drive_smart
    error = robot_angle - gyro.heading(DEGREES)
    print((gyro.rotation(DEGREES), robot_angle, error))
    left_drive_smart.set_velocity(p * error, PERCENT)
    right_drive_smart.set_velocity(-p * error, PERCENT)
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)
   
    while abs(error) > 1.5:
        update_position()
        error = robot_angle - gyro.rotation(DEGREES)
        if (abs(error) < 10): p = 0.7
        if (abs(error) < 5): p = 0.9
        if (abs(error) < 2): p = 1.2
        left_drive_smart.set_velocity(p * error, PERCENT)
        right_drive_smart.set_velocity(-p * error, PERCENT)
        if (abs(error) > 10):
            wait(200, MSEC)
        else:
            wait(100, MSEC)
        if (abs(p * error) < 1):
            break
       
        

    left_drive_smart.stop()
    right_drive_smart.stop()
    


def walk_path(points_list, lookahead_distance, stop_threshold, direction, decl = True, decl_dis = 22, decl_rate = 0.6, last_point_tolerance = 2.5):

    global current_x, current_y, start_pos_size, forward_velocity, turn_velocity_k, left_velocity, right_velocity, robot_not_walking
    
    original_list = len(points_list)

    numDeceleratePoints = 0
    start_pos_size = len(points_list)

    if current_x == -1:
        current_x = points_list[0][0]
        current_y = points_list[0][1]

    running = True
    while running:
        adjust_high_scoring_motor_position()
        check_vision_sensor()
        stall_detection_and_handling()
        if len(points_list) == 0 or robot_not_walking > MAX_WAIT_FOR_NO_WALK:
            running = False
            robot_not_walking = 0
            break

        # Calculate the lookahead point
        next_point = calculate_lookahead_point(points_list, lookahead_distance)

        # Calculate drive speeds based on the specified direction
        calculate_drive_speeds(next_point, direction)
        #print("x: "+ str(current_x)+" y: " + str(current_y) + " angle: " + str(current_angle) + " lspeed" + str(left_velocity) + " rspeed" + str(right_velocity))
        #len(points_list) < original_list/10 and 
        if (len(points_list) != 0):
            dis_to_end = math.sqrt((points_list[-1][0] - current_x) ** 2 + (points_list[-1][1] - current_y) ** 2)
            print(dis_to_end)
            if dis_to_end < decl_dis and decl:
                print("declerating" + str((dis_to_end/(dis_to_end+5))))
                if (dis_to_end < decl_dis /2):
                    decl_rate = 0.4
                    left_velocity = left_velocity * decl_rate
                    right_velocity = right_velocity * decl_rate
                else:
                    left_velocity = left_velocity * (dis_to_end/(dis_to_end+(dis_to_end/2))) * decl_rate
                    right_velocity = right_velocity * (dis_to_end/(dis_to_end+(dis_to_end/2))) * decl_rate
        
        # Update the robot's position/stop
        update_position()

        # Check if the robot has reached the current target point
        distance_to_point = math.sqrt((points_list[0][0] - current_x) ** 2 + (points_list[0][1] - current_y) ** 2)
        if len(points_list) == 1:
            final_distance = math.sqrt((points_list[-1][0] - current_x) ** 2 + (points_list[-1][1] - current_y) ** 2)
            if final_distance < last_point_tolerance:
                running = False
        elif distance_to_point < stop_threshold:  # Adjust the threshold as needed
            points_list.pop(0)  # Remove the reached point

        # Check if the robot has reached the last point
        

        # Set motor velocities
        left_drive_smart.set_velocity(left_velocity, PERCENT)
        left_drive_smart.spin(FORWARD)
        right_drive_smart.set_velocity(right_velocity, PERCENT)
        right_drive_smart.spin(FORWARD)
        #print("(" + str(current_x)+"," + str(current_y) + "),")

        wait(20, MSEC)

    # Stop motors when path is complete

    #print(dis_to_end)
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
    autonomous_more_donuts_side(blue_right_tomogo, blue_right_tofirststack, blue_right_lasttwo, first_blue_right_4, blue_right_back_4, blue_right_totower)

def autonomous_red_left():
    autonomous_more_donuts_side(red_left_tomogo, red_left_tofirststack, red_left_lasttwo, first_red_left_4, red_left_back_4, red_left_totower)

def autonomous_red_right():
    global p1redight, p2redright, p3redright, p4redright, p7redright
    autonomous_more_donuts_side_modified(red_right_tomogo, red_right_tofirststack, red_right_lasttwo, first_red_right_4, red_right_back_4, red_right_totower)
    #autonomous_extra_mogo_side(p1redright, p2redright, p3redright, p4redright, p7redright)

def autonomous_blue_left():
    global p1blueleft, p2blueleft, p3blueleft, p4blueleft, p7blueleft
    autonomous_more_donuts_side(blue_left_tomogo, blue_left_tofirststack, blue_left_lasttwo, first_blue_left_4, blue_left_back_4, blue_left_totower)
    #autonomous_extra_mogo_side(p1blueleft, p2blueleft, p3blueleft, p4blueleft, p7blueleft)

def autonomous_extra_mogo_side(p1, p2, p3, p4, p7):
    global intake_state, lookahead, tolerance
    #confirm about tolerance and direction    
    lookahead = 50
    print("autonomous_red_right: before p1")  
    walk_path(p1, lookahead, tolerance, 1)
   
    walk_path(p2, lookahead, tolerance, -1)
    print("autonomous_red_right: before p2")
    mogo_p.set(True)
    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_WAIT)
    adjust_high_scoring_motor_position()
    wait(10, MSEC)
    intake_state = IntakeState.RUNNING
    set_intake_motor_state(REVERSE)
    wait(1000, MSEC)
   
    walk_path(p3, lookahead, tolerance, 1)
    print("autonomous_red_right: before p3")
   
 
    walk_path(p4, lookahead, tolerance, 1)
    print("autonomous_red_right: before p4")
    mogo_p.set(False)
    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_DOWN)
    adjust_high_scoring_motor_position()

    walk_path(p7, lookahead, tolerance, 1)
    print("autonomous_red_right: before p4")

   
    """walk_path(p5, lookahead, tolerance, 1)
    print("autonomous_red_right: before p6")
    wait(100, MSEC)
    donker.set(True)"""
   
    #walk_path(p6, lookahead, tolerance, 1)
   
    print("autonomous_red_right: before p7")
   
    """walk_path(p5, lookahead, tolerance, 1)
    print("autonomous_red_right: END")"""
       

def autonomous_more_donuts_side(tomogo, tofirststack, last_two, first_4, back_4, to_tower):
    global intake_state, lookahead, high_score_target_angle, tolerance, forward_velocity, turn_velocity_k

    # Bring up high scoring motor
    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_WAIT)
    adjust_high_scoring_motor_position()

    lookahead = 50
    tolerance = 2
    # go to mogo
    walk_path(tomogo, lookahead, tolerance, -1)
    # Capture the mogo
    mogo_p.set(True)
    wait(100, MSEC)

    # start intake to pick up the top donut including the stall code
    intake_state = IntakeState.RUNNING
    set_intake_motor_state(REVERSE)

    # Bring down the intake to knock off the top donut
    update_position()
    print("autonomous_more_donuts_side: before tofirststack")
    walk_path(tofirststack, lookahead, tolerance, 1)
    update_position()
    lookahead = 20
    tolerance = 6
    print("autonomous_more_donuts_side: before last_two")
    walk_path(last_two, lookahead, tolerance, 1)
    print("autonomous_more_donuts_side: before first_4")
    update_position()
    lookahead = 50
    walk_path(first_4, lookahead, tolerance, 1)
    print("autonomous_more_donuts_side: before to_tower")
    back_reverse = back_4[::-1]
    print("autonomous_more_donuts_side: going back1")
    walk_path(back_4, lookahead, tolerance, -1)
    walk_path(back_reverse, lookahead, tolerance, 1)
    print("autonomous_more_donuts_side: going back2")
    walk_path(back_4, lookahead, tolerance, -1)
    walk_path(back_reverse, lookahead, tolerance, 1)
    walk_path(back_4, lookahead, tolerance, -1)
    # Bring up high scoring motor
    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_DOWN)
    adjust_high_scoring_motor_position()
    intake_state = IntakeState.STOPPED
    set_intake_motor_state()
    walk_path(to_tower, lookahead, tolerance, 1)
def autonomous_more_donuts_side_modified(tomogo, tofirststack, last_two, first_4, back_4, to_tower):
    global intake_state, lookahead, high_score_target_angle, tolerance, forward_velocity, turn_velocity_k
    # Bring up high scoring motor
    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_WAIT)
    adjust_high_scoring_motor_position()

    lookahead = 50
    tolerance = 2
    # go to mogo
    walk_path(tomogo, lookahead, tolerance, -1)
    # Capture the mogo
    mogo_p.set(True)
    wait(100, MSEC)

    # start intake to pick up the top donut including the stall code
    intake_state = IntakeState.RUNNING
    set_intake_motor_state(REVERSE)

    # Bring down the intake to knock off the top donut
    update_position()
    print("autonomous_more_donuts_side: before tofirststack")
    walk_path(tofirststack, lookahead, tolerance, 1)
    update_position()
    lookahead = 20
    tolerance = 6
    print("autonomous_more_donuts_side: before last_two")
    #walk_path(last_two, lookahead, tolerance, 1)
    print("autonomous_more_donuts_side: before first_4")
    update_position()
    lookahead = 50
    walk_path(first_4, lookahead, tolerance, 1)
    print("autonomous_more_donuts_side: before to_tower")
    back_reverse_first = back_4[::-1]
    back_reverse_second = back_4[::-1]
    back_4_first = back_4[:]
    back_4_second = back_4[:]
    back_4_third = back_4[:]
    print("autonomous_more_donuts_side: going back1")
    walk_path(back_4_first, lookahead, tolerance, -1)
    walk_path(back_reverse_first, lookahead, tolerance, 1)
    wait(300, MSEC)
    print("autonomous_more_donuts_side: going back2")
    walk_path(back_4_second, lookahead, tolerance, -1)
    walk_path(back_reverse_second, lookahead, tolerance, 1)
    wait(300, MSEC)
    walk_path(back_4_third, lookahead, tolerance, -1)
    # Bring up high scoring motor
    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_DOWN)
    adjust_high_scoring_motor_position()
    intake_state = IntakeState.STOPPED
    set_intake_motor_state()
    turn_velocity_k = 40
    forward_velocity = 40
    walk_path(to_tower, lookahead, tolerance, 1)

# driver.py
def valid_seen_object(seen_objects):
    # A placeholder to check if the objects array is valid
    if len(seen_objects) > 0:
        for obj in seen_objects:
            object_size = obj.width * obj.height
            #print("Detected object with size: " + str(object_size))
            if object_size > MIN_REJECT_SIZE:
                return True
    return False

BRIGHTNESS_THRESHOLD = 0
# Function to check the vision sensor
def check_vision_sensor():
    global eject_object
    if Color_sensor.brightness() > BRIGHTNESS_THRESHOLD:
        if eject_object == RingType.RED:
            if Color_sensor.color() == Color.RED:
               print("Ejecting Red")
               ejection_p.set(True)
            else:
                ejection_p.set(False)
        else:
            if eject_object == RingType.BLUE:
                if Color_sensor.color() == Color.BLUE:
                    #print("Ejecting Blue")
                    ejection_p.set(True)
                else:
                    ejection_p.set(False)

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
    if slow_drive:
        return scaled_input * 25
    else:
        return scaled_input * 100

# Function to set drive motor velocities based on controller input
def set_drive_motor_velocities():
    global slow_drive
    if controller_1.buttonA.pressing():
        slow_drive = not slow_drive
        while controller_1.buttonA.pressing():
            wait(10, MSEC)

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
        set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_SCORE)
        high_scoring_running = False
        while controller_1.buttonLeft.pressing():
            wait(10, MSEC)

    if controller_1.buttonUp.pressing():
        set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_WAIT)
        high_scoring_running = False
        while controller_1.buttonLeft.pressing():
            wait(10, MSEC)

    if controller_1.buttonRight.pressing():
        set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_CAPTURE)
        high_scoring_running = True
        while controller_1.buttonLeft.pressing():
            wait(10, MSEC)

    if controller_1.buttonDown.pressing():
        set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_DOWN)
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
    global eject_object, gyro
    # Autonomous code
    # For example, move forward for a certain distance
    # define a variable slot_no and switch case based on the slot_no
    # to run the corresponding autonomous routine
    #wait(3, SECONDS)
    slot_no = 2
    if slot_no == 1:
        gyro.set_heading(180, DEGREES)
        eject_object = RingType.BLUE
        autonomous_red_left()
    elif slot_no == 2:
        gyro.set_heading(180, DEGREES)
        eject_object = RingType.BLUE
        autonomous_red_right()
    elif slot_no == 3:
        eject_object = RingType.NONE
        autonomous_blue_left()
    elif slot_no == 4:
        eject_object = RingType.RED
        autonomous_blue_right()
    elif slot_no == 5:
        eject_object = RingType.NONE
        autonomous_test()

    eject_object = RingType.NONE
    ejection_p.set(False)
    left_drive_smart.stop()
    right_drive_smart.stop()

# Driver control function
def drivercontrol():
    # Main control loop for driver control
    while True:
        set_drive_motor_velocities()
        toggle_high_scoring_motor()
        adjust_high_scoring_motor_position()
        toggle_intake_motor()
        #check_vision_sensor()
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

alliance_stake = [(-159.385, 0.323), (-165, 0), (-100.925, 0.154), (-80.925, 0.154)]

grabbing_mogo = [(-120.483, 5.068), (-120.451, 7.067), (-120.419, 9.067), (-120.387, 11.067), (-120.355, 13.067), (-120.323, 15.066), (-120.291, 17.066), (-120.259, 19.066), (-120.227, 21.066), (-120.195, 23.065), (-120.163, 25.065), (-120.131, 27.065), (-120.099, 29.065), (-120.067, 31.064), (-120.035, 33.064), (-120.003, 35.064), (-119.971, 37.064), (-119.939, 39.063), (-119.907, 41.063), (-119.875, 43.063), (-119.843, 45.063), (-119.811, 47.062), (-119.779, 49.062), (-119.747, 51.062), (-119.715, 53.062), (-119.683, 55.061), (-119.651, 57.061), (-119.619, 59.061), (-119.587, 61.061), (-119.555, 63.06), (-119.523, 65.06), (-119.491, 67.06), (-119.468, 68.533), (-119.468, 68.533)]

first_double_donuts = [(-119.345, 59.459), (-117.346, 59.529), (-115.347, 59.599), (-113.349, 59.669), (-111.35, 59.738), (-109.351, 59.808), (-107.352, 59.878), (-105.354, 59.948), (-103.355, 60.018), (-101.356, 60.088), (-99.357, 60.158), (-97.358, 60.228), (-95.36, 60.298), (-93.361, 60.368), (-91.362, 60.438), (-89.363, 60.508), (-87.365, 60.578), (-85.366, 60.648), (-83.367, 60.718), (-81.368, 60.788), (-79.369, 60.858), (-77.371, 60.928), (-75.372, 60.998), (-73.373, 61.068), (-71.374, 61.138), (-69.376, 61.208), (-67.377, 61.278), (-65.378, 61.348), (-63.379, 61.418), (-61.38, 61.488), (-59.382, 61.558), (-57.383, 61.628), (-55.384, 61.698), (-53.385, 61.768), (-51.387, 61.838), (-49.682, 62.761), (-48.065, 63.938), (-46.449, 65.116), (-44.834, 66.295), (-43.221, 67.478), (-41.611, 68.665), (-40.004, 69.856), (-38.403, 71.054), (-36.808, 72.261), (-35.22, 73.477), (-33.641, 74.704), (-32.074, 75.946), (-30.519, 77.204), (-28.979, 78.481), (-27.457, 79.778), (-25.955, 81.099), (-24.477, 82.446), (-23.024, 83.821), (-21.601, 85.226), (-20.21, 86.663), (-18.854, 88.133), (-17.536, 89.637), (-16.257, 91.175), (-15.02, 92.746), (-13.826, 94.35), (-12.673, 95.985), (-11.563, 97.648), (-10.496, 99.34), (-9.469, 101.056), (-8.48, 102.794), (-7.53, 104.554), (-6.613, 106.331), (-5.73, 108.126), (-4.876, 109.934), (-4.051, 111.756), (-3.252, 113.59), (-2.477, 115.433), (-1.724, 117.286), (-0.99, 119.147), (-0.276, 121.015), (0.422, 122.889), (0.605, 124.856), (0.604, 126.856), (0.602, 128.856), (0.601, 130.856), (0.599, 132.856), (0.597, 134.856), (0.596, 136.856), (0.594, 138.856), (0.592, 140.856), (0.591, 142.856), (0.59, 144.383), (0.59, 144.383)]

robot_rotation = [(0.012, 144.687), (0.019, 142.687), (0.026, 140.687), (0.033, 138.687), (0.04, 136.687), (0.047, 134.687), (0.054, 132.687), (0.061, 130.687), (0.068, 128.687), (0.075, 126.687), (0.082, 124.687), (0.089, 122.687), (0.097, 120.687), (0.104, 118.687), (0.111, 116.687), (0.118, 114.687), (0.125, 112.687), (0.132, 110.687), (0.139, 108.687), (0.146, 106.687), (0.152, 104.925), (0.152, 104.925)]

first_last_four_donuts = [(-14.134, 117.4), (-16.133, 117.35), (-18.132, 117.299), (-20.132, 117.249), (-22.131, 117.198), (-24.13, 117.148), (-26.13, 117.097), (-28.129, 117.047), (-30.129, 116.996), (-32.128, 116.946), (-34.127, 116.895), (-36.127, 116.845), (-38.126, 116.794), (-40.125, 116.744), (-42.125, 116.693), (-44.124, 116.643), (-46.123, 116.592), (-48.123, 116.542), (-50.122, 116.491), (-52.122, 116.441), (-54.121, 116.39), (-56.12, 116.34), (-58.12, 116.289), (-60.119, 116.239), (-62.118, 116.188), (-64.118, 116.138), (-66.117, 116.087), (-68.116, 116.034), (-70.116, 115.976), (-72.115, 115.921), (-74.114, 115.868), (-76.113, 115.817), (-78.113, 115.769), (-80.112, 115.723), (-82.112, 115.681), (-84.111, 115.641), (-86.111, 115.606), (-88.111, 115.574), (-90.111, 115.546), (-92.111, 115.522), (-94.11, 115.504), (-96.11, 115.491), (-98.11, 115.484), (-100.11, 115.484), (-102.11, 115.492), (-104.11, 115.509), (-106.11, 115.537), (-108.11, 115.577), (-110.109, 115.632), (-112.108, 115.704), (-114.105, 115.798), (-116.102, 115.92), (-118.096, 116.076), (-120.086, 116.274), (-122.07, 116.52), (-124.051, 116.801), (-126.031, 117.077), (-128.019, 117.296), (-130.014, 117.444), (-132.012, 117.532), (-134.011, 117.575), (-136.011, 117.584), (-138.011, 117.568), (-140.011, 117.534), (-142.01, 117.485), (-144.009, 117.424), (-146.008, 117.354), (-148.006, 117.275), (-150.005, 117.189), (-152.003, 117.098), (-154.0, 117.002), (-156.737, 116.863), (-156.737, 116.863)]


mogo_triangle =  [(-154.663, 118.262), (-153.485, 116.646), (-152.307, 115.03), (-151.129, 113.413), (-149.951, 111.797), (-148.773, 110.18), (-147.595, 108.564), (-146.418, 106.948), (-145.24, 105.331), (-144.062, 103.715), (-142.884, 102.099), (-141.706, 100.482), (-140.528, 98.866), (-139.35, 97.25), (-138.173, 95.633), (-136.995, 94.017), (-135.817, 92.4), (-134.639, 90.784), (-133.461, 89.168), (-132.283, 87.551), (-131.105, 85.935), (-129.927, 84.319), (-128.75, 82.702), (-127.572, 81.086), (-126.394, 79.47), (-125.216, 77.853), (-124.038, 76.237), (-122.86, 74.62), (-121.682, 73.004), (-120.505, 71.388), (-119.327, 69.771), (-118.149, 68.155), (-116.971, 66.539), (-115.793, 64.922), (-114.615, 63.306), (-113.437, 61.689), (-112.26, 60.073), (-111.082, 58.457), (-109.904, 56.84), (-108.726, 55.224), (-107.548, 53.608), (-106.37, 51.991), (-105.192, 50.375), (-104.015, 48.759), (-102.764, 47.042), (-102.764, 47.042)]

mogo_triangle_2 = [(-103.05, 45.734), (-103.987, 47.501), (-104.925, 49.267), (-105.863, 51.034), (-106.801, 52.8), (-107.739, 54.567), (-108.677, 56.333), (-109.615, 58.1), (-110.553, 59.866), (-111.491, 61.632), (-112.429, 63.399), (-113.366, 65.165), (-114.304, 66.932), (-115.242, 68.698), (-116.18, 70.465), (-117.118, 72.231), (-118.056, 73.998), (-118.994, 75.764), (-119.932, 77.531), (-120.87, 79.297), (-121.808, 81.063), (-122.745, 82.83), (-123.683, 84.596), (-124.621, 86.363), (-125.559, 88.129), (-126.497, 89.896), (-127.435, 91.662), (-128.373, 93.429), (-129.311, 95.195), (-130.249, 96.961), (-131.187, 98.728), (-132.124, 100.494), (-133.062, 102.261), (-134.0, 104.027), (-134.938, 105.794), (-135.876, 107.56), (-136.814, 109.327), (-137.752, 111.093), (-138.69, 112.86), (-139.628, 114.626), (-140.566, 116.392), (-141.503, 118.159), (-142.441, 119.925), (-143.379, 121.692), (-144.317, 123.458), (-145.255, 125.225), (-146.193, 126.991), (-147.131, 128.758), (-148.069, 130.524), (-149.007, 132.29), (-149.945, 134.057), (-151.261, 136.536), (-151.261, 136.536)]


corner_to_mogo = [(-160.86, 161.306), (-160.369, 159.367), (-159.879, 157.428), (-159.388, 155.489), (-158.898, 153.55), (-158.407, 151.611), (-157.917, 149.672), (-157.426, 147.733), (-156.936, 145.795), (-156.445, 143.856), (-155.955, 141.917), (-155.464, 139.978), (-154.974, 138.039), (-154.483, 136.1), (-153.993, 134.161), (-153.502, 132.222), (-153.012, 130.283), (-152.521, 128.344), (-152.031, 126.405), (-151.54, 124.466), (-151.05, 122.528), (-150.559, 120.589), (-150.069, 118.65), (-149.578, 116.711), (-149.088, 114.772), (-148.597, 112.833), (-148.107, 110.894), (-147.616, 108.955), (-147.126, 107.016), (-146.635, 105.077), (-146.145, 103.138), (-145.654, 101.199), (-145.164, 99.261), (-144.673, 97.322), (-144.183, 95.383), (-143.692, 93.444), (-143.202, 91.505), (-142.711, 89.566), (-142.221, 87.627), (-141.73, 85.688), (-141.24, 83.749), (-140.749, 81.81), (-140.259, 79.871), (-139.768, 77.932), (-139.278, 75.994), (-138.787, 74.055), (-138.297, 72.116), (-137.806, 70.177), (-137.316, 68.238), (-136.825, 66.299), (-136.335, 64.36), (-135.844, 62.421), (-135.354, 60.482), (-134.863, 58.543), (-134.373, 56.604), (-133.882, 54.665), (-133.391, 52.727), (-132.939, 50.939), (-132.939, 50.939)]

turn_to_mogo = [(-126.727, 57.152), (-126.617, 55.155), (-126.506, 53.158), (-126.396, 51.161), (-126.285, 49.164), (-126.175, 47.167), (-126.064, 45.17), (-125.953, 43.173), (-125.843, 41.176), (-125.732, 39.179), (-125.622, 37.182), (-125.511, 35.185), (-125.401, 33.188), (-125.29, 31.191), (-125.18, 29.194), (-125.069, 27.197), (-124.958, 25.2), (-124.848, 23.203), (-124.737, 21.207), (-124.627, 19.21), (-124.516, 17.213), (-124.406, 15.216), (-124.295, 13.219), (-124.185, 11.222), (-124.074, 9.225), (-123.963, 7.228), (-123.853, 5.231), (-123.742, 3.234), (-123.632, 1.237), (-123.521, -0.76), (-123.411, -2.757), (-123.3, -4.754), (-123.19, -6.751), (-123.079, -8.748), (-122.968, -10.745), (-122.858, -12.741), (-122.747, -14.738), (-122.637, -16.735), (-122.526, -18.732), (-122.416, -20.729), (-122.305, -22.726), (-122.195, -24.723), (-122.084, -26.72), (-121.974, -28.717), (-121.863, -30.714), (-121.752, -32.711), (-121.642, -34.708), (-121.531, -36.705), (-121.421, -38.702), (-121.31, -40.699), (-121.2, -42.696), (-121.089, -44.693), (-120.979, -46.689), (-120.868, -48.686), (-120.757, -50.683), (-120.647, -52.68), (-120.536, -54.677), (-120.426, -56.674), (-120.27, -59.484), (-120.27, -59.484)]

 

collect_right_bottom_rings =   [(-120.515, -79.515), (-118.798, -78.489), (-117.081, -77.464), (-115.364, -76.438), (-113.647, -75.412), (-111.93, -74.387), (-110.213, -73.361), (-108.497, -72.335), (-106.78, -71.309), (-105.063, -70.284), (-103.346, -69.258), (-101.629, -68.232), (-99.912, -67.207), (-98.195, -66.181), (-96.478, -65.155), (-94.761, -64.129), (-93.044, -63.104), (-91.327, -62.078), (-89.61, -61.052), (-87.893, -60.027), (-86.176, -59.001), (-84.459, -57.975), (-82.742, -56.95), (-81.025, -55.924), (-79.308, -54.898), (-77.591, -53.872), (-75.874, -52.847), (-74.157, -51.821), (-72.529, -51.175), (-71.429, -52.846), (-70.304, -54.499), (-69.152, -56.134), (-67.973, -57.75), (-66.772, -59.348), (-65.546, -60.929), (-64.297, -62.491), (-63.028, -64.037), (-61.738, -65.565), (-60.426, -67.075), (-59.096, -68.568), (-57.748, -70.045), (-56.38, -71.505), (-54.995, -72.947), (-53.593, -74.374), (-52.175, -75.784), (-50.74, -77.177), (-49.289, -78.554), (-47.824, -79.915), (-46.344, -81.261), (-44.849, -82.588), (-43.34, -83.901), (-41.817, -85.198), (-40.281, -86.479), (-38.731, -87.742), (-37.168, -88.991), (-35.594, -90.224), (-34.006, -91.44), (-32.406, -92.639), (-30.794, -93.823), (-29.17, -94.991), (-27.535, -96.142), (-25.887, -97.276), (-24.228, -98.393), (-22.559, -99.495), (-20.877, -100.577), (-19.185, -101.643), (-17.482, -102.692), (-15.768, -103.722), (-14.042, -104.733), (-12.307, -105.727), (-10.56, -106.702), (-8.802, -107.656), (-7.035, -108.591), (-5.256, -109.505), (-3.466, -110.398), (-1.666, -111.27), (0.145, -112.119), (1.966, -112.944), (3.798, -113.747), (5.642, -114.522), (7.495, -115.274), (9.36, -115.996), (11.235, -116.692), (13.122, -117.355), (15.019, -117.989), (16.927, -118.587), (18.846, -119.151), (20.776, -119.676), (22.716, -120.161), (24.666, -120.605), (26.627, -120.999), (28.597, -121.343), (30.576, -121.633), (32.562, -121.864), (34.555, -122.028), (36.553, -122.119), (38.553, -122.131), (40.551, -122.054), (42.544, -121.879), (43.485, -121.758), (43.485, -121.758)]

collect_left_bottom_rings =  [(x, -y) for x, y in collect_right_bottom_rings]

collect_right_bottom_rings2 = [(78.037, -126.338), (76.04, -126.448), (74.046, -126.6), (72.056, -126.795), (70.07, -127.03), (68.089, -127.31), (66.116, -127.636), (64.15, -128.002), (62.192, -128.407), (60.243, -128.858), (58.304, -129.348), (56.375, -129.874), (54.457, -130.443), (52.55, -131.045), (50.655, -131.683), (48.77, -132.354), (46.897, -133.054), (45.035, -133.785), (43.184, -134.54), (41.342, -135.321), (39.509, -136.121), (37.685, -136.941), (35.867, -137.775), (34.055, -138.621), (32.247, -139.475), (30.44, -140.333), (28.633, -141.191), (26.825, -142.045), (25.011, -142.888), (23.191, -143.717), (21.361, -144.523), (19.518, -145.301), (17.661, -146.042), (15.786, -146.739), (13.892, -147.38), (11.976, -147.955), (10.039, -148.453), (8.081, -148.86), (6.105, -149.164), (4.114, -149.354), (2.116, -149.419), (0.117, -149.351), (-1.872, -149.146), (-3.842, -148.804), (-5.784, -148.327), (-7.69, -147.722), (-9.554, -146.999), (-11.374, -146.17), (-13.148, -145.247), (-14.871, -144.232), (-16.55, -143.146), (-18.181, -141.988), (-19.773, -140.777), (-21.318, -139.509), (-22.828, -138.197), (-24.303, -136.846), (-25.742, -135.458), (-27.149, -134.037), (-28.528, -132.587), (-29.879, -131.113), (-31.205, -129.616), (-32.507, -128.098), (-33.787, -126.561), (-35.045, -125.007), (-36.285, -123.437), (-37.506, -121.853), (-38.71, -120.256), (-40.027, -118.905), (-42.027, -118.93), (-44.027, -118.955), (-46.027, -118.981), (-48.027, -119.006), (-50.026, -119.032), (-52.026, -119.057), (-54.026, -119.083), (-56.026, -119.108), (-58.026, -119.134), (-60.026, -119.159), (-62.025, -119.184), (-64.025, -119.21), (-66.025, -119.235), (-68.025, -119.261), (-70.025, -119.286), (-72.025, -119.312), (-74.024, -119.337), (-76.024, -119.363), (-78.024, -119.388), (-80.024, -119.413), (-82.024, -119.439), (-84.024, -119.464), (-86.024, -119.49), (-88.023, -119.515), (-90.023, -119.541), (-92.023, -119.566), (-94.023, -119.592), (-96.023, -119.617), (-98.023, -119.643), (-100.022, -119.668), (-102.022, -119.693), (-104.022, -119.719), (-106.022, -119.744), (-108.022, -119.77), (-110.022, -119.795), (-112.021, -119.821), (-114.021, -119.846), (-116.021, -119.872), (-118.021, -119.897), (-120.021, -119.922), (-122.021, -119.948), (-124.02, -119.973), (-126.02, -119.999), (-128.02, -120.024), (-130.02, -120.05), (-132.02, -120.075), (-134.02, -120.101), (-136.019, -120.126), (-138.019, -120.151), (-140.019, -120.177), (-142.019, -120.202), (-144.019, -120.228), (-146.019, -120.253), (-148.019, -120.279), (-150.018, -120.304), (-152.018, -120.33), (-154.018, -120.355)]
                               #, (-156.018, -120.38), (-158.018, -120.406), (-160.167, -120.433), (-160.167, -120.433)]
collect_left_bottom_rings2 =  [(x, -y) for x, y in collect_right_bottom_rings2]
    
toprightmogo2_missing = [(60.258, -119.894), (58.311, -120.352), (56.365, -120.814), (54.42, -121.281), (52.477, -121.756), (50.536, -122.237), (48.596, -122.723), (46.658, -123.216), (44.722, -123.717), (42.787, -124.226), (40.855, -124.742), (38.925, -125.266), (36.997, -125.799), (35.072, -126.342), (33.15, -126.895), (31.231, -127.458), (29.316, -128.033), (27.404, -128.62), (25.496, -129.22), (23.593, -129.835), (21.694, -130.464), (19.801, -131.109), (17.915, -131.773), (16.035, -132.456), (14.163, -133.161), (12.3, -133.889), (10.448, -134.642), (8.606, -135.421), (6.775, -136.227), (4.954, -137.054), (3.132, -137.878), (1.275, -138.619), (-0.678, -139.016), (-2.658, -138.787), (-4.565, -138.187), (-6.431, -137.468), (-8.285, -136.718), (-10.139, -135.967), (-11.996, -135.224), (-13.857, -134.493), (-15.724, -133.776), (-17.596, -133.072), (-19.473, -132.382), (-21.355, -131.703), (-23.241, -131.037), (-25.13, -130.382), (-27.023, -129.736), (-28.92, -129.101), (-30.819, -128.475), (-32.721, -127.857), (-34.626, -127.248), (-36.534, -126.647), (-38.444, -126.053), (-40.355, -125.466), (-42.269, -124.886), (-44.185, -124.311), (-46.102, -123.742), (-48.022, -123.18), (-49.943, -122.624), (-51.865, -122.072), (-53.789, -121.524), (-55.714, -120.984), (-57.641, -120.446), (-59.568, -119.913), (-61.566, -119.894), (-63.566, -119.894), (-65.566, -119.894), (-67.566, -119.894), (-69.566, -119.894), (-71.566, -119.894), (-73.566, -119.894), (-75.566, -119.894), (-77.566, -119.894), (-79.566, -119.894), (-81.566, -119.894), (-83.566, -119.894), (-85.566, -119.894), (-87.566, -119.894), (-89.566, -119.894), (-91.566, -119.894), (-93.566, -119.894), (-95.566, -119.894), (-97.566, -119.894), (-99.566, -119.894), (-101.566, -119.894), (-103.566, -119.894), (-105.566, -119.894), (-107.566, -119.894), (-109.566, -119.894), (-111.566, -119.894), (-113.566, -119.894), (-115.566, -119.894), (-117.566, -119.894), (-119.566, -119.894), (-121.566, -119.894), (-123.566, -119.894), (-125.566, -119.894), (-127.566, -119.894), (-129.566, -119.894), (-131.566, -119.894), (-133.566, -119.894), (-135.566, -119.894), (-137.566, -119.894), (-139.566, -119.894), (-141.566, -119.894), (-143.566, -119.894), (-145.364, -119.894), (-145.364, -119.894)]

#mogo_to_corner = [(-160.167, -120.433), (-158.167, -120.433), (-156.167, -120.433), (-154.167, -120.433), (-152.167, -120.433), (-150.167, -120.433), (-148.167, -120.433), (-146.167, -120.433), (-144.167, -120.433), (-142.167, -120.433), (-140.167, -120.433), (-138.167, -120.433), (-136.167, -120.433), (-134.167, -120.433), (-132.167, -120.433), (-130.167, -120.433), (-128.167, -120.433), (-126.167, -120.433), (-124.167, -120.433), (-122.167, -120.433), (-120.167, -120.433), (-118.167, -120.433), (-116.167, -120.433), (-114.167, -120.433), (-112.167, -120.433), (-110.167, -120.433), (-108.167, -120.433), (-106.167, -120.433), (-104.167, -120.433), (-102.167, -120.433), (-100.167, -120.433), (-98.167, -120.433), (-96.167, -120.433), (-94.167, -120.433), (-92.167, -120.433), (-90.167, -120.433), (-88.167, -120.433), (-86.167, -120.433), (-84.167, -120.433), (-82.167, -120.433), (-80.167, -120.433), (-78.167, -120.433), (-76.167, -120.433), (-74.167, -120.433), (-72.167, -120.433), (-70.167, -120.433), (-68.167, -120.433), (-66.167, -120.433), (-64.167, -120.433), (-62.167, -120.433), (-60.167, -120.433), (-58.167, -120.433), (-56.167, -120.433), (-54.167, -120.433), (-52.167, -120.433), (-50.167, -120.433), (-48.167, -120.433), (-46.167, -120.433), (-44.167, -120.433), (-42.167, -120.433), (-40.167, -120.433), (-38.167, -120.433), (-36.346, -120.433), (-36.346, -120.433)]
# Optimized Path
mogo_to_corner = [(-160.167, -120.433), (-158.167, -120.433), (-156.167, -120.433), (-154.167, -120.433), (-152.167, -120.433), (-150.167, -120.433), (-148.167, -120.433), (-146.167, -120.433), (-144.167, -120.433), (-142.167, -120.433), (-140.167, -120.433), (-138.167, -120.433), (-136.167, -120.433), (-134.167, -120.433), (-132.167, -120.433), (-130.167, -120.433), (-128.167, -120.433), (-126.167, -120.433), (-124.167, -120.433), (-122.167, -120.433), (-120.167, -120.433), (-118.167, -120.433), (-116.167, -120.433), (-114.167, -120.433), (-112.167, -120.433), (-110.167, -120.433), (-108.167, -120.433), (-106.167, -120.433), (-104.167, -120.433), (-102.167, -120.433), (-100.167, -120.433), (-98.167, -120.433), (-96.167, -120.433), (-94.167, -120.433), (-92.167, -120.433), (-90.167, -120.433), (-88.167, -120.433), (-86.167, -120.433), (-84.167, -120.433), (-82.167, -120.433), (-80.167, -120.433), (-78.167, -120.433), (-76.167, -120.433)]


mogo_to_left_corner  =  [(x, -y) for x, y in mogo_to_corner]

bottom_right_mogo = [(-152.818, -151.576), (-152.659, -149.582), (-152.499, -147.588), (-152.34, -145.595), (-152.18, -143.601), (-152.021, -141.608), (-151.861, -139.614), (-151.702, -137.62), (-151.542, -135.627), (-151.383, -133.633), (-151.223, -131.639), (-151.064, -129.646), (-150.904, -127.652), (-150.745, -125.659), (-150.585, -123.665), (-150.426, -121.671), (-149.494, -120.481), (-147.495, -120.401), (-145.497, -120.32), (-143.499, -120.239), (-141.5, -120.159), (-139.502, -120.078), (-137.504, -119.997), (-135.505, -119.917), (-133.507, -119.836), (-131.508, -119.755), (-129.51, -119.675), (-127.512, -119.594), (-125.513, -119.513), (-123.515, -119.433), (-121.517, -119.352), (-119.518, -119.271), (-117.52, -119.191), (-115.522, -119.11), (-113.523, -119.03), (-111.525, -118.949), (-109.526, -118.868), (-107.528, -118.788), (-105.53, -118.707), (-103.531, -118.626), (-101.533, -118.546), (-99.535, -118.465), (-97.536, -118.384), (-95.538, -118.304), (-93.539, -118.223), (-91.541, -118.142), (-89.543, -118.062), (-87.544, -117.981), (-85.546, -117.9), (-83.548, -117.82), (-81.549, -117.739), (-79.551, -117.658), (-77.552, -117.578), (-75.554, -117.497), (-73.556, -117.417), (-71.557, -117.336), (-69.559, -117.255), (-67.561, -117.175), (-65.562, -117.094), (-63.564, -117.013), (-61.565, -116.933), (-59.567, -116.852), (-57.569, -116.771), (-55.57, -116.691), (-53.572, -116.61), (-51.574, -116.529), (-49.575, -116.449), (-47.577, -116.368), (-45.578, -116.287), (-43.58, -116.207), (-41.582, -116.126), (-39.583, -116.045), (-37.585, -115.965), (-35.587, -115.884), (-33.588, -115.803), (-31.59, -115.723), (-29.591, -115.642), (-27.593, -115.562), (-25.595, -115.481), (-23.596, -115.4), (-21.598, -115.32), (-19.6, -115.239), (-17.601, -115.158), (-15.603, -115.078), (-13.604, -114.997), (-11.803, -114.924), (-11.803, -114.924)]
 

mogo_to_corner2 =  [(-36.346, -120.433), (-38.152, -119.575), (-39.963, -118.725), (-41.777, -117.884), (-43.597, -117.054), (-45.422, -116.236), (-47.251, -115.428), (-49.086, -114.631), (-50.926, -113.848), (-52.772, -113.08), (-54.624, -112.324), (-56.482, -111.583), (-58.345, -110.856), (-60.215, -110.145), (-62.091, -109.454), (-63.975, -108.781), (-65.865, -108.127), (-67.761, -107.493), (-69.665, -106.881), (-71.577, -106.292), (-73.495, -105.727), (-75.421, -105.189), (-77.355, -104.679), (-79.297, -104.199), (-81.246, -103.75), (-83.202, -103.336), (-85.166, -102.957), (-87.137, -102.621), (-89.116, -102.328), (-91.1, -102.08), (-93.09, -101.878), (-95.084, -101.73), (-97.082, -101.642), (-99.082, -101.611), (-101.081, -101.647), (-103.079, -101.752), (-105.07, -101.929), (-107.054, -102.186), (-109.025, -102.524), (-110.98, -102.945), (-112.912, -103.459), (-114.82, -104.058), (-116.697, -104.749), (-118.536, -105.533), (-120.336, -106.404), (-122.093, -107.36), (-123.8, -108.402), (-125.457, -109.522), (-127.063, -110.713), (-128.618, -111.97), (-130.119, -113.292), (-131.57, -114.668), (-132.973, -116.093), (-134.328, -117.564), (-135.638, -119.076), (-136.908, -120.62), (-138.137, -122.197), (-139.332, -123.801), (-140.495, -125.429), (-141.626, -127.078), (-142.732, -128.744), (-143.812, -130.428), (-144.871, -132.124), (-145.91, -133.833), (-146.933, -135.552), (-147.941, -137.279), (-148.936, -139.014), (-149.921, -140.755), (-150.896, -142.501), (-151.864, -144.251), (-152.827, -146.004), (-153.785, -147.759), (-154.741, -149.516)]
# Optimized Path
#mogo_to_corner2 =  [(-36.346, -120.433), (-38.152, -119.575), (-39.963, -118.725), (-41.777, -117.884), (-43.597, -117.054), (-45.422, -116.236), (-47.251, -115.428), (-49.086, -114.631), (-50.926, -113.848), (-52.772, -113.08), (-54.624, -112.324), (-56.482, -111.583), (-58.345, -110.856), (-60.215, -110.145), (-62.091, -109.454), (-63.975, -108.781), (-65.865, -108.127), (-67.761, -107.493), (-69.665, -106.881), (-71.577, -106.292), (-73.495, -105.727), (-75.421, -105.189), (-77.355, -104.679), (-79.297, -104.199), (-81.246, -103.75), (-83.202, -103.336), (-85.166, -102.957), (-87.137, -102.621), (-89.116, -102.328), (-91.1, -102.08), (-93.09, -101.878), (-95.084, -101.73), (-97.082, -101.642), (-99.082, -101.611), (-101.081, -101.647), (-103.079, -101.752), (-105.07, -101.929), (-107.054, -102.186), (-109.025, -102.524), (-110.98, -102.945), (-112.912, -103.459), (-114.82, -104.058), (-116.697, -104.749), (-118.536, -105.533), (-120.336, -106.404), (-122.093, -107.36), (-123.8, -108.402), (-125.457, -109.522), (-127.063, -110.713), (-128.618, -111.97), (-130.119, -113.292), (-131.57, -114.668), (-132.973, -116.093), (-134.328, -117.564), (-135.638, -119.076), (-136.908, -120.62), (-138.137, -122.197), (-139.332, -123.801), (-140.495, -125.429), (-141.626, -127.078), (-142.732, -128.744), (-143.812, -130.428), (-144.871, -132.124), (-145.91, -133.833)]

mogo_to_left_corner2  =  [(x, -y) for x, y in mogo_to_corner2]

emptymogo1 = [(145.364, -145.985), (144.989, -144.02), (144.615, -142.055), (144.241, -140.091), (143.867, -138.126), (143.493, -136.161), (143.118, -134.197), (142.744, -132.232), (142.37, -130.267), (141.996, -128.303), (141.621, -126.338), (141.247, -124.373), (140.873, -122.409), (140.499, -120.444), (140.124, -118.479), (139.75, -116.515), (139.376, -114.55), (139.002, -112.585), (138.628, -110.621), (138.253, -108.656), (137.879, -106.691), (137.505, -104.727), (137.131, -102.762), (136.756, -100.797), (136.382, -98.833), (136.008, -96.868), (135.634, -94.903), (135.26, -92.939), (134.885, -90.974), (134.511, -89.009), (134.137, -87.045), (133.763, -85.08), (133.388, -83.115), (133.014, -81.151), (132.64, -79.186), (132.266, -77.221), (131.892, -75.256), (131.517, -73.292), (131.143, -71.327), (130.769, -69.362), (130.455, -67.712), (130.455, -67.712)]
emptymogo2 = [(134.182, -73.924), (133.831, -71.955), (133.481, -69.986), (133.13, -68.017), (132.779, -66.048), (132.429, -64.079), (132.078, -62.11), (131.727, -60.141), (131.377, -58.172), (131.026, -56.203), (130.675, -54.234), (130.325, -52.265), (129.974, -50.296), (129.623, -48.327), (129.273, -46.358), (128.922, -44.389), (128.571, -42.42), (128.221, -40.451), (127.87, -38.482), (127.52, -36.513), (127.169, -34.544), (126.818, -32.575), (126.468, -30.606), (126.117, -28.637), (125.766, -26.668), (125.416, -24.699), (125.065, -22.73), (124.714, -20.761), (124.364, -18.792), (124.013, -16.823), (123.662, -14.854), (123.312, -12.885), (122.961, -10.916), (122.61, -8.947), (122.26, -6.978), (121.909, -5.008), (121.559, -3.039), (121.208, -1.07), (120.857, 0.899), (120.507, 2.868), (120.156, 4.837), (119.805, 6.806), (119.455, 8.775), (119.104, 10.744), (118.753, 12.713), (118.403, 14.682), (118.03, 16.773), (118.03, 16.773)]
emptymogo3 = [(118.03, 11.803), (116.03, 11.828), (114.032, 11.901), (112.036, 12.024), (110.043, 12.199), (108.057, 12.428), (106.078, 12.715), (104.108, 13.061), (102.15, 13.469), (100.207, 13.941), (98.282, 14.484), (96.377, 15.094), (94.496, 15.772), (92.642, 16.521), (90.817, 17.339), (89.026, 18.228), (87.276, 19.196), (85.566, 20.234), (83.899, 21.338), (82.278, 22.509), (80.713, 23.754), (79.199, 25.06), (77.736, 26.424), (76.332, 27.848), (74.987, 29.328), (73.697, 30.856), (72.465, 32.431), (71.295, 34.053), (70.179, 35.713), (69.118, 37.408), (68.118, 39.14), (67.17, 40.901), (66.272, 42.687), (65.429, 44.501), (64.636, 46.337), (63.888, 48.192), (63.186, 50.064), (62.532, 51.954), (61.918, 53.858), (61.344, 55.774), (60.812, 57.701), (60.318, 59.639), (59.859, 61.586), (59.433, 63.54), (59.044, 65.502), (58.686, 67.469), (58.357, 69.442), (58.057, 71.419), (57.788, 73.401), (57.544, 75.386), (57.325, 77.374), (57.133, 79.365), (56.964, 81.358), (56.818, 83.352), (56.693, 85.348), (56.59, 87.346), (56.506, 89.344), (56.442, 91.343), (56.397, 93.342), (56.368, 95.342), (56.356, 97.342), (56.36, 99.342), (56.379, 101.342), (56.412, 103.342), (56.458, 105.341), (56.516, 107.34), (56.584, 109.339), (56.662, 111.338), (56.746, 113.336), (56.836, 115.334), (56.927, 117.332), (57.015, 119.33), (57.092, 121.328), (57.143, 123.328), (58.017, 124.897), (59.612, 126.104), (61.223, 127.289), (62.844, 128.461), (64.473, 129.621), (66.117, 130.76), (67.772, 131.883), (69.437, 132.99), (71.114, 134.081), (72.806, 135.147), (74.509, 136.195), (76.224, 137.225), (77.95, 138.235), (79.692, 139.218), (81.446, 140.178), (83.213, 141.115), (84.992, 142.028), (86.785, 142.914), (88.591, 143.774), (90.413, 144.6), (92.247, 145.395), (94.096, 146.159), (95.958, 146.889), (97.833, 147.583), (99.722, 148.239), (101.625, 148.856), (103.541, 149.429), (105.47, 149.958), (107.411, 150.439), (109.364, 150.87), (111.328, 151.247), (113.302, 151.568), (115.285, 151.821), (117.276, 152.011), (119.272, 152.132), (121.271, 152.182), (123.271, 152.148), (125.267, 152.028), (127.256, 151.824), (129.232, 151.517), (131.191, 151.112), (133.123, 150.599), (135.023, 149.974), (136.879, 149.231), (138.685, 148.374), (140.424, 147.387), (142.093, 146.286), (143.675, 145.063), (145.159, 143.723), (146.541, 142.279), (147.809, 140.733), (148.955, 139.094), (149.982, 137.379), (150.884, 135.594), (151.659, 133.751), (152.319, 131.864), (152.852, 129.936), (153.279, 127.983), (153.59, 126.008), (153.807, 124.02), (153.916, 122.023), (153.941, 120.023), (153.876, 118.025), (153.728, 116.03), (153.508, 114.043), (153.215, 112.064), (152.851, 110.098), (152.425, 108.144), (151.941, 106.204), (151.401, 104.278), (150.809, 102.368), (150.164, 100.475), (149.472, 98.598), (148.735, 96.739), (147.956, 94.897), (147.137, 93.073), (146.28, 91.266), (145.387, 89.476), (144.46, 87.704), (143.5, 85.95), (142.508, 84.213), (141.487, 82.493), (140.437, 80.791), (139.357, 79.108), (138.251, 77.441), (137.121, 75.792), (135.967, 74.158), (133.751, 71.144), (133.751, 71.144)]
emptymogo4 = [(118.099, 93.436), (116.278, 94.262), (114.457, 95.089), (112.635, 95.915), (110.814, 96.742), (108.993, 97.568), (107.172, 98.395), (105.35, 99.222), (103.529, 100.048), (101.708, 100.875), (99.887, 101.701), (98.066, 102.528), (96.244, 103.354), (94.423, 104.181), (92.602, 105.007), (90.781, 105.834), (88.96, 106.661), (87.138, 107.487), (85.317, 108.314), (83.496, 109.14), (81.675, 109.967), (79.854, 110.793), (78.032, 111.62), (76.211, 112.446), (74.39, 113.273), (72.569, 114.099), (70.747, 114.926), (68.926, 115.753), (67.105, 116.579), (65.284, 117.406), (63.463, 118.232), (61.641, 119.059), (59.82, 119.885), (57.999, 120.712), (56.441, 121.419), (56.441, 121.419)]

#mogo_in_right_top_corner1 = [(-143.5, -152.197), (-141.561, -151.706), (-139.622, -151.215), (-137.684, -150.724), (-135.745, -150.233), (-133.806, -149.742), (-131.867, -149.251), (-129.929, -148.76), (-127.99, -148.269), (-126.051, -147.778), (-124.112, -147.287), (-122.173, -146.795), (-120.235, -146.304), (-118.296, -145.813), (-116.357, -145.322), (-114.418, -144.831), (-112.479, -144.34), (-110.541, -143.849), (-108.602, -143.358), (-106.663, -142.867), (-104.724, -142.376), (-102.786, -141.885), (-100.847, -141.394), (-98.908, -140.903), (-96.969, -140.412), (-95.03, -139.921), (-93.092, -139.43), (-91.153, -138.939), (-89.214, -138.448), (-87.275, -137.957), (-85.337, -137.466), (-83.398, -136.975), (-81.459, -136.484), (-79.52, -135.992), (-77.581, -135.501), (-75.643, -135.01), (-73.704, -134.519), (-71.765, -134.028), (-69.826, -133.537), (-67.888, -133.046), (-65.949, -132.555), (-64.01, -132.064), (-62.071, -131.573), (-60.132, -131.082), (-58.194, -130.591), (-56.255, -130.1), (-54.316, -129.609), (-52.377, -129.118), (-50.438, -128.627), (-48.5, -128.136), (-46.561, -127.645), (-44.622, -127.154), (-42.683, -126.663), (-40.745, -126.172), (-38.806, -125.681), (-36.867, -125.189), (-34.928, -124.698), (-32.989, -124.207), (-31.051, -123.716), (-29.112, -123.225), (-27.173, -122.734), (-25.234, -122.243), (-23.296, -121.752), (-21.357, -121.261), (-19.418, -120.77), (-17.479, -120.279), (-15.54, -119.788), (-13.602, -119.297), (-11.663, -118.806), (-9.724, -118.315), (-7.785, -117.824), (-5.846, -117.333), (-3.908, -116.842), (-1.242, -116.167), (-1.242, -116.167)]
# Optimized Path
mogo_in_right_top_corner1 = [(-147.227, -149.091), (-146.827, -147.131), (-146.427, -145.172), (-146.028, -143.212), (-145.628, -141.252), (-145.228, -139.293), (-144.828, -137.333), (-144.428, -135.374), (-144.028, -133.414), (-143.628, -131.454), (-143.228, -129.495), (-142.828, -127.535), (-142.428, -125.576), (-142.028, -123.616), (-141.628, -121.656), (-141.228, -119.697), (-140.082, -118.643), (-138.082, -118.626), (-136.082, -118.608), (-134.082, -118.59), (-132.082, -118.573), (-130.082, -118.555), (-128.082, -118.538), (-126.083, -118.52), (-124.083, -118.502), (-122.083, -118.485), (-120.083, -118.467), (-118.083, -118.449), (-116.083, -118.432), (-114.083, -118.414), (-112.083, -118.397), (-110.083, -118.379), (-108.083, -118.361), (-106.083, -118.344), (-104.083, -118.326), (-102.083, -118.309), (-100.084, -118.291), (-98.084, -118.273), (-96.084, -118.256), (-94.084, -118.238), (-92.084, -118.22), (-90.084, -118.203), (-88.084, -118.185), (-86.084, -118.168), (-84.084, -118.15), (-82.084, -118.132), (-80.084, -118.115), (-78.084, -118.097), (-76.084, -118.079), (-74.085, -118.062), (-72.085, -118.044), (-70.085, -118.027), (-68.085, -118.009), (-66.085, -117.991), (-64.085, -117.974), (-62.085, -117.956), (-60.085, -117.938), (-58.085, -117.921), (-56.085, -117.903), (-54.085, -117.886), (-52.085, -117.868), (-50.085, -117.85), (-48.086, -117.833), (-46.086, -117.815), (-44.086, -117.798), (-42.086, -117.78), (-40.086, -117.762), (-38.086, -117.745), (-36.086, -117.727), (-34.086, -117.709), (-32.086, -117.692), (-30.086, -117.674), (-28.086, -117.657), (-26.086, -117.639), (-24.087, -117.621), (-22.087, -117.604), (-20.087, -117.586), (-18.087, -117.568), (-16.087, -117.551), (-14.087, -117.533), (-12.087, -117.516), (-10.087, -117.498), (-8.087, -117.48), (-6.087, -117.463), (-4.087, -117.445), (-2.087, -117.427), (0.0, -117.409), (0.0, -117.409)]

mogo_in_right_top_corner2 = [(-1.242, -124.864), (0.613, -124.118), (2.469, -123.373), (4.325, -122.627), (6.181, -121.882), (8.037, -121.136), (9.893, -120.391), (11.749, -119.645), (13.604, -118.9), (15.46, -118.154), (17.316, -117.408), (19.172, -116.663), (21.028, -115.917), (22.884, -115.172), (24.74, -114.426), (26.595, -113.681), (28.451, -112.935), (30.307, -112.19), (32.163, -111.444), (34.019, -110.699), (35.875, -109.953), (37.731, -109.208), (39.586, -108.462), (41.442, -107.717), (43.298, -106.971), (45.154, -106.226), (47.01, -105.48), (48.866, -104.735), (50.722, -103.989), (52.577, -103.244), (54.433, -102.498), (56.289, -101.753), (58.145, -101.007), (60.001, -100.262), (61.857, -99.516), (63.713, -98.771), (65.568, -98.025), (67.424, -97.28), (69.28, -96.534), (71.136, -95.789), (72.992, -95.043), (74.848, -94.298), (76.704, -93.552), (78.559, -92.806), (80.415, -92.061), (82.271, -91.315), (84.127, -90.57), (85.983, -89.824), (87.839, -89.079), (89.695, -88.333), (91.55, -87.588), (93.406, -86.842), (95.262, -86.097), (97.118, -85.351), (98.974, -84.606), (100.83, -83.86), (102.686, -83.115), (104.541, -82.369), (106.397, -81.624), (108.253, -80.878), (110.109, -80.133), (111.965, -79.387), (113.821, -78.642), (115.677, -77.896), (117.532, -77.151), (119.388, -76.405), (121.244, -75.66), (123.1, -74.914), (124.956, -74.169), (126.812, -73.423), (128.668, -72.678), (130.523, -71.932), (132.379, -71.187), (134.235, -70.441), (136.091, -69.695), (137.947, -68.95), (139.803, -68.204), (141.659, -67.459), (144.121, -66.47), (144.121, -66.47)]
mogo_in_right_top_corner3 = [(148.47, -66.47), (148.162, -68.446), (147.899, -70.428), (147.683, -72.417), (147.511, -74.409), (147.376, -76.405), (147.28, -78.402), (147.215, -80.401), (147.179, -82.401), (147.172, -84.401), (147.188, -86.401), (147.224, -88.4), (147.279, -90.4), (147.349, -92.398), (147.432, -94.397), (147.525, -96.394), (147.625, -98.392), (147.729, -100.389), (147.836, -102.386), (147.942, -104.384), (148.043, -106.381), (148.137, -108.379), (148.222, -110.377), (148.292, -112.376), (148.346, -114.375), (148.377, -116.375), (148.385, -118.375), (148.36, -120.375), (148.303, -122.374), (148.201, -124.371), (148.057, -126.366), (147.855, -128.355), (147.594, -130.338), (147.265, -132.311), (146.855, -134.268), (146.36, -136.205), (145.771, -138.117), (145.071, -139.99), (144.258, -141.817), (143.327, -143.586), (142.273, -145.285), (141.094, -146.9), (139.789, -148.415), (138.373, -149.825), (136.854, -151.126), (135.242, -152.308), (133.549, -153.373), (131.795, -154.332), (129.981, -155.173), (128.127, -155.922), (126.235, -156.571), (124.316, -157.135), (122.377, -157.623), (120.42, -158.036), (118.45, -158.38), (116.471, -158.665), (114.484, -158.895), (112.492, -159.074), (110.497, -159.207), (108.499, -159.298), (106.5, -159.348), (104.5, -159.363), (102.5, -159.344), (100.501, -159.295), (98.502, -159.218), (96.505, -159.11), (94.51, -158.977), (92.516, -158.821), (90.524, -158.645), (88.533, -158.45), (86.545, -158.229), (84.56, -157.993), (82.575, -157.742), (80.594, -157.471), (78.614, -157.184), (76.637, -156.886), (74.662, -156.571), (70.818, -155.924), (70.818, -155.924)]
p1_rightmogo = [(164.0, -131.076), (163.293, -129.205), (162.587, -127.334), (161.88, -125.463), (161.174, -123.592), (160.467, -121.721), (159.76, -119.85), (159.054, -117.979), (158.347, -116.108), (157.641, -114.237), (156.934, -112.366), (156.227, -110.495), (155.521, -108.624), (154.814, -106.753), (154.107, -104.882), (153.401, -103.01), (152.694, -101.139), (151.988, -99.268), (151.281, -97.397), (150.574, -95.526), (149.868, -93.655), (149.161, -91.784), (148.455, -89.913), (147.748, -88.042), (147.041, -86.171), (146.335, -84.3), (145.628, -82.429), (144.922, -80.558), (144.215, -78.687), (143.508, -76.816), (142.802, -74.945), (142.095, -73.074), (141.389, -71.203), (140.682, -69.332), (139.975, -67.461), (139.269, -65.59), (138.562, -63.719), (137.856, -61.848), (137.149, -59.977), (136.442, -58.106), (135.736, -56.235), (135.029, -54.364), (134.322, -52.493), (133.616, -50.622), (132.909, -48.751), (132.203, -46.88), (131.496, -45.009), (130.789, -43.138), (130.083, -41.267), (129.376, -39.396), (128.67, -37.525), (127.963, -35.654), (127.256, -33.783), (126.55, -31.912), (125.843, -30.041), (125.137, -28.17), (124.43, -26.299), (123.723, -24.428), (123.017, -22.557), (122.31, -20.686), (121.604, -18.815), (120.897, -16.944), (119.894, -14.288), (119.894, -14.288)]
p2_rightmogo = [(116.788, -3.106), (115.463, -1.608), (114.138, -0.11), (112.812, 1.388), (111.487, 2.886), (110.162, 4.384), (108.837, 5.882), (107.512, 7.38), (106.187, 8.878), (104.862, 10.376), (103.536, 11.874), (102.211, 13.372), (100.886, 14.87), (99.561, 16.368), (98.236, 17.866), (96.911, 19.364), (95.586, 20.862), (94.26, 22.36), (92.935, 23.858), (91.61, 25.356), (90.285, 26.854), (88.96, 28.352), (87.635, 29.85), (86.309, 31.348), (84.984, 32.846), (83.659, 34.344), (82.334, 35.842), (81.009, 37.34), (79.684, 38.838), (78.359, 40.336), (77.033, 41.834), (75.708, 43.332), (74.383, 44.83), (73.058, 46.328), (71.733, 47.826), (70.408, 49.324), (69.083, 50.822), (67.757, 52.32), (66.432, 53.818), (65.107, 55.316), (63.782, 56.814), (62.457, 58.312), (61.132, 59.81), (59.807, 61.308), (59.598, 63.243), (59.554, 65.242), (59.51, 67.242), (59.466, 69.241), (59.422, 71.241), (59.378, 73.24), (59.334, 75.24), (59.29, 77.239), (59.246, 79.239), (59.203, 81.238), (59.159, 83.238), (59.115, 85.237), (59.071, 87.237), (59.027, 89.236), (58.983, 91.236), (58.939, 93.236), (58.895, 95.235), (58.851, 97.235), (58.807, 99.234), (58.763, 101.234), (58.719, 103.233), (58.675, 105.233), (58.631, 107.232), (58.587, 109.232), (58.543, 111.231), (58.499, 113.231), (58.455, 115.23), (58.412, 117.23), (59.425, 118.642), (61.145, 119.663), (62.865, 120.684), (64.585, 121.704), (66.305, 122.725), (68.025, 123.745), (69.745, 124.766), (71.465, 125.787), (73.185, 126.807), (74.905, 127.828), (76.625, 128.849), (78.345, 129.869), (80.065, 130.89), (81.785, 131.911), (83.505, 132.931), (85.225, 133.952), (86.945, 134.973), (88.665, 135.993), (90.385, 137.014), (92.105, 138.034), (93.825, 139.055), (95.545, 140.076), (97.265, 141.096), (98.985, 142.117), (100.705, 143.138), (102.424, 144.158), (104.144, 145.179), (105.864, 146.2), (107.584, 147.22), (109.304, 148.241), (111.024, 149.262), (112.744, 150.282), (114.464, 151.303), (115.987, 150.567), (117.438, 149.19), (118.888, 147.813), (120.339, 146.437), (121.789, 145.06), (123.24, 143.683), (124.691, 142.306), (126.141, 140.929), (127.592, 139.552), (129.042, 138.175), (130.493, 136.799), (131.944, 135.422), (133.394, 134.045), (134.845, 132.668), (136.295, 131.291), (137.746, 129.914), (139.197, 128.537), (140.647, 127.161), (142.098, 125.784), (143.549, 124.407), (144.999, 123.03), (146.45, 121.653), (147.9, 120.276), (149.351, 118.9), (150.802, 117.523), (151.533, 115.856), (151.443, 113.858), (151.352, 111.86), (151.261, 109.862), (151.17, 107.864), (151.079, 105.866), (150.989, 103.869), (150.898, 101.871), (150.807, 99.873), (150.716, 97.875), (150.625, 95.877), (150.534, 93.879), (150.444, 91.881), (150.353, 89.883), (150.262, 87.885), (150.171, 85.887), (150.08, 83.889), (149.99, 81.891), (149.899, 79.893), (149.808, 77.895), (149.712, 75.788), (149.712, 75.788)]
p3_rightmogo = [(157.788, 39.758), (157.819, 41.757), (157.85, 43.757), (157.882, 45.757), (157.913, 47.757), (157.944, 49.756), (157.975, 51.756), (158.007, 53.756), (158.038, 55.756), (158.069, 57.755), (158.1, 59.755), (158.132, 61.755), (158.163, 63.755), (158.194, 65.754), (158.225, 67.754), (158.257, 69.754), (158.288, 71.754), (158.319, 73.753), (158.35, 75.753), (158.382, 77.753), (158.413, 79.753), (158.444, 81.752), (158.475, 83.752), (158.507, 85.752), (158.538, 87.752), (158.569, 89.751), (158.6, 91.751), (158.632, 93.751), (158.663, 95.751), (158.694, 97.75), (158.725, 99.75), (158.757, 101.75), (158.788, 103.75), (158.819, 105.75), (158.85, 107.749), (158.881, 109.749), (158.913, 111.749), (158.944, 113.749), (158.975, 115.748), (159.006, 117.748), (159.038, 119.748), (159.069, 121.748), (159.1, 123.747), (159.131, 125.747), (159.163, 127.747), (159.194, 129.747), (159.225, 131.746), (159.256, 133.746), (159.288, 135.746), (159.319, 137.746), (159.35, 139.745), (159.381, 141.745), (159.413, 143.745), (159.444, 145.745), (159.475, 147.744), (159.506, 149.744), (159.538, 151.744), (159.569, 153.744), (159.6, 155.743), (159.631, 157.743), (159.652, 159.03), (159.652, 159.03)]
p1_5thmogo = [(164.0, -131.076), (163.293, -129.205), (162.587, -127.334), (161.88, -125.463), (161.174, -123.592), (160.467, -121.721), (159.76, -119.85), (159.054, -117.979), (158.347, -116.108), (157.641, -114.237), (156.934, -112.366), (156.227, -110.495), (155.521, -108.624), (154.814, -106.753), (154.107, -104.882), (153.401, -103.01), (152.694, -101.139), (151.988, -99.268), (151.281, -97.397), (150.574, -95.526), (149.868, -93.655), (149.161, -91.784), (148.455, -89.913), (147.748, -88.042), (147.041, -86.171), (146.335, -84.3), (145.628, -82.429), (144.922, -80.558), (144.215, -78.687), (143.508, -76.816), (142.802, -74.945), (142.095, -73.074), (141.389, -71.203), (140.682, -69.332), (139.975, -67.461), (139.269, -65.59), (138.562, -63.719), (137.856, -61.848), (137.149, -59.977), (136.442, -58.106), (135.736, -56.235), (135.029, -54.364), (134.322, -52.493), (133.616, -50.622), (132.909, -48.751), (132.203, -46.88), (131.496, -45.009), (130.789, -43.138), (130.083, -41.267), (129.376, -39.396), (128.67, -37.525), (127.963, -35.654), (127.256, -33.783), (126.55, -31.912), (125.843, -30.041), (125.137, -28.17), (124.43, -26.299), (123.723, -24.428), (123.017, -22.557), (122.31, -20.686), (121.604, -18.815), (120.897, -16.944), (119.894, -14.288), (119.894, -14.288)]
p2_5thmogo = [(116.788, -3.106), (115.463, -1.608), (114.138, -0.11), (112.812, 1.388), (111.487, 2.886), (110.162, 4.384), (108.837, 5.882), (107.512, 7.38), (106.187, 8.878), (104.862, 10.376), (103.536, 11.874), (102.211, 13.372), (100.886, 14.87), (99.561, 16.368), (98.236, 17.866), (96.911, 19.364), (95.586, 20.862), (94.26, 22.36), (92.935, 23.858), (91.61, 25.356), (90.285, 26.854), (88.96, 28.352), (87.635, 29.85), (86.309, 31.348), (84.984, 32.846), (83.659, 34.344), (82.334, 35.842), (81.009, 37.34), (79.684, 38.838), (78.359, 40.336), (77.033, 41.834), (75.708, 43.332), (74.383, 44.83), (73.058, 46.328), (71.733, 47.826), (70.408, 49.324), (69.083, 50.822), (67.757, 52.32), (66.432, 53.818), (65.107, 55.316), (63.782, 56.814), (62.457, 58.312), (61.132, 59.81), (59.807, 61.308), (59.598, 63.243), (59.554, 65.242), (59.51, 67.242), (59.466, 69.241), (59.422, 71.241), (59.378, 73.24), (59.334, 75.24), (59.29, 77.239), (59.246, 79.239), (59.203, 81.238), (59.159, 83.238), (59.115, 85.237), (59.071, 87.237), (59.027, 89.236), (58.983, 91.236), (58.939, 93.236), (58.895, 95.235), (58.851, 97.235), (58.807, 99.234), (58.763, 101.234), (58.719, 103.233), (58.675, 105.233), (58.631, 107.232), (58.587, 109.232), (58.543, 111.231), (58.499, 113.231), (58.455, 115.23), (58.412, 117.23), (59.425, 118.642), (61.145, 119.663), (62.865, 120.684), (64.585, 121.704), (66.305, 122.725), (68.025, 123.745), (69.745, 124.766), (71.465, 125.787), (73.185, 126.807), (74.905, 127.828), (76.625, 128.849), (78.345, 129.869), (80.065, 130.89), (81.785, 131.911), (83.505, 132.931), (85.225, 133.952), (86.945, 134.973), (88.665, 135.993), (90.385, 137.014), (92.105, 138.034), (93.825, 139.055), (95.545, 140.076), (97.265, 141.096), (98.985, 142.117), (100.705, 143.138), (102.424, 144.158), (104.144, 145.179), (105.864, 146.2), (107.584, 147.22), (109.304, 148.241), (111.024, 149.262), (112.744, 150.282), (114.464, 151.303), (115.987, 150.567), (117.438, 149.19), (118.888, 147.813), (120.339, 146.437), (121.789, 145.06), (123.24, 143.683), (124.691, 142.306), (126.141, 140.929), (127.592, 139.552), (129.042, 138.175), (130.493, 136.799), (131.944, 135.422), (133.394, 134.045), (134.845, 132.668), (136.295, 131.291), (137.746, 129.914), (139.197, 128.537), (140.647, 127.161), (142.098, 125.784), (143.549, 124.407), (144.999, 123.03), (146.45, 121.653), (147.9, 120.276), (149.351, 118.9), (150.802, 117.523), (151.533, 115.856), (151.443, 113.858), (151.352, 111.86), (151.261, 109.862), (151.17, 107.864), (151.079, 105.866), (150.989, 103.869), (150.898, 101.871), (150.807, 99.873), (150.716, 97.875), (150.625, 95.877), (150.534, 93.879), (150.444, 91.881), (150.353, 89.883), (150.262, 87.885), (150.171, 85.887), (150.08, 83.889), (149.99, 81.891), (149.899, 79.893), (149.808, 77.895), (149.712, 75.788), (149.712, 75.788)]
toprightmogo1 = [(152.818, -97.53), (152.96, -99.525), (153.096, -101.521), (153.223, -103.517), (153.337, -105.513), (153.441, -107.511), (153.535, -109.508), (153.617, -111.507), (153.682, -113.506), (153.733, -115.505), (153.769, -117.505), (153.788, -119.505), (153.789, -121.505), (153.769, -123.504), (153.727, -125.504), (153.658, -127.503), (153.563, -129.5), (153.436, -131.496), (153.273, -133.49), (153.072, -135.48), (152.826, -137.464), (152.531, -139.442), (152.181, -141.411), (151.755, -143.365), (151.256, -145.302), (150.658, -147.21), (149.953, -149.081), (149.113, -150.896), (148.114, -152.627), (146.936, -154.242), (145.552, -155.683), (143.969, -156.902), (142.214, -157.856), (140.326, -158.508), (138.364, -158.886), (136.37, -159.024), (134.372, -158.958), (132.385, -158.729), (130.418, -158.369), (128.473, -157.907), (126.548, -157.363), (124.644, -156.752), (122.759, -156.084), (120.89, -155.373), (119.036, -154.621), (117.196, -153.839), (115.366, -153.031), (113.548, -152.198), (111.737, -151.348), (109.934, -150.483), (108.138, -149.604), (106.347, -148.714), (104.56, -147.815), (102.777, -146.908), (100.998, -145.996), (99.22, -145.079), (97.444, -144.159), (95.67, -143.237), (93.896, -142.313), (92.123, -141.388), (90.349, -140.464), (88.575, -139.541), (86.8, -138.62), (85.023, -137.701), (83.245, -136.785), (81.465, -135.872), (79.684, -134.964), (77.899, -134.06), (76.113, -133.162), (74.323, -132.268), (72.531, -131.381), (70.736, -130.5), (68.937, -129.625), (67.135, -128.757), (65.33, -127.896), (63.521, -127.044), (61.707, -126.2), (59.89, -125.364), (58.07, -124.537), (56.245, -123.718), (54.416, -122.908), (52.583, -122.108), (50.318, -121.136), (50.318, -121.136)]
toprightmogo2 = [(62.121, -119.894), (63.942, -120.72), (65.764, -121.547), (67.585, -122.373), (69.406, -123.2), (71.227, -124.026), (73.049, -124.853), (74.87, -125.679), (76.691, -126.506), (78.513, -127.332), (80.334, -128.158), (82.155, -128.985), (83.976, -129.811), (85.798, -130.638), (87.619, -131.464), (89.44, -132.291), (91.261, -133.117), (93.083, -133.944), (94.904, -134.77), (96.725, -135.597), (98.546, -136.423), (100.368, -137.249), (102.189, -138.076), (104.01, -138.902), (105.831, -139.729), (107.653, -140.555), (109.474, -141.382), (111.295, -142.208), (113.116, -143.035), (114.938, -143.861), (116.759, -144.688), (118.58, -145.514), (120.401, -146.34), (122.223, -147.167), (124.044, -147.993), (125.865, -148.82), (127.686, -149.646), (129.508, -150.473), (131.329, -151.299), (133.15, -152.126), (134.971, -152.952), (136.045, -153.439), (136.045, -153.439)]
topleftmogo2 = [(x, -y) for x, y in toprightmogo2]
lastmogo = [(154.274, 147.604), (153.649, 145.704), (153.081, 143.787), (152.564, 141.855), (152.091, 139.911), (151.657, 137.959), (151.256, 136.0), (150.887, 134.034), (150.541, 132.064), (150.216, 130.091), (149.906, 128.115), (149.609, 126.137), (149.321, 124.158), (149.037, 122.178), (148.753, 120.199), (148.467, 118.219), (148.173, 116.241), (147.868, 114.264), (147.547, 112.29), (147.205, 110.32), (146.837, 108.354), (146.436, 106.394), (145.997, 104.443), (145.511, 102.503), (144.971, 100.578), (144.367, 98.671), (143.688, 96.79), (142.921, 94.943), (142.051, 93.143), (141.066, 91.403), (139.955, 89.74), (138.699, 88.185), (137.298, 86.759), (135.752, 85.493), (134.071, 84.411), (132.281, 83.522), (130.401, 82.844), (128.462, 82.358), (126.486, 82.051), (124.492, 81.906), (122.493, 81.901), (120.496, 82.017), (118.51, 82.246), (116.535, 82.563), (114.576, 82.961), (112.631, 83.427), (110.703, 83.958), (108.789, 84.539), (106.89, 85.167), (105.008, 85.842), (103.139, 86.554), (101.283, 87.3), (99.44, 88.077), (97.609, 88.882), (95.79, 89.713), (93.982, 90.567), (91.023, 92.02), (91.023, 92.02)]
passivehang = [(88.148, 100.166), (86.801, 98.687), (85.459, 97.205), (84.12, 95.719), (82.785, 94.23), (81.454, 92.737), (80.127, 91.241), (78.802, 89.742), (77.481, 88.241), (76.163, 86.737), (74.847, 85.23), (73.534, 83.722), (72.224, 82.211), (70.916, 80.698), (69.61, 79.183), (68.307, 77.666), (67.005, 76.148), (65.705, 74.628), (64.406, 73.107), (63.11, 71.584), (61.814, 70.06), (60.52, 68.535), (59.227, 67.009), (57.936, 65.483), (56.645, 63.955), (55.355, 62.427), (54.065, 60.898), (52.777, 59.368), (51.489, 57.838), (50.201, 56.308), (48.914, 54.777), (47.626, 53.247), (46.339, 51.716), (45.052, 50.185), (43.765, 48.654), (42.478, 47.123), (41.19, 45.593), (39.902, 44.063), (38.614, 42.533), (37.325, 41.004), (36.035, 39.476), (34.744, 37.948), (33.453, 36.421), (32.161, 34.894), (30.867, 33.369), (29.572, 31.844), (28.276, 30.321), (26.979, 28.799), (25.68, 27.278), (24.379, 25.759), (23.077, 24.241), (21.773, 22.724), (20.467, 21.21), (19.159, 19.697), (17.849, 18.186), (16.537, 16.676), (15.222, 15.169), (13.905, 13.664), (12.585, 12.162), (11.262, 10.662), (9.937, 9.164), (8.537, 7.589), (8.537, 7.589)]
passivehangreverse = passivehang[::-1] 

# Wall stakes test paths
wallStakeTestp1 = [(-119.221, 68.281), (-117.538, 67.201), (-115.841, 66.142), (-114.13, 65.107), (-112.404, 64.096), (-110.662, 63.113), (-108.904, 62.161), (-107.129, 61.238), (-105.337, 60.351), (-103.527, 59.501), (-101.698, 58.69), (-99.851, 57.923), (-97.985, 57.205), (-96.1, 56.536), (-94.196, 55.924), (-92.273, 55.376), (-90.332, 54.894), (-88.374, 54.485), (-86.402, 54.157), (-84.417, 53.915), (-82.422, 53.767), (-80.423, 53.723), (-78.424, 53.785), (-76.433, 53.962), (-74.454, 54.255), (-72.499, 54.673), (-70.573, 55.21), (-68.684, 55.867), (-66.839, 56.637), (-65.041, 57.514), (-63.295, 58.488), (-61.6, 59.549), (-59.954, 60.685), (-58.351, 61.881), (-56.785, 63.125), (-55.244, 64.4), (-53.714, 65.687), (-52.173, 66.962), (-50.595, 68.19), (-48.939, 69.311), (-47.159, 70.217), (-45.56, 71.417), (-43.967, 72.626), (-42.374, 73.835), (-40.78, 75.043), (-39.187, 76.252), (-37.594, 77.461), (-36.0, 78.67), (-34.407, 79.879), (-32.814, 81.088), (-31.22, 82.297), (-29.627, 83.506), (-28.034, 84.714), (-26.44, 85.923), (-24.847, 87.132), (-23.254, 88.341), (-21.66, 89.55), (-20.067, 90.759), (-18.474, 91.968), (-16.881, 93.176), (-15.287, 94.385), (-13.694, 95.594), (-12.101, 96.803), (-10.507, 98.012), (-8.914, 99.221), (-7.321, 100.43), (-5.727, 101.639), (-4.134, 102.847), (-2.541, 104.056), (-1.425, 104.903), (-1.425, 104.903)]
wallStakeTestp2 = [(-1.425, 104.903), (-1.425, 106.903), (-1.425, 108.903), (-1.425, 110.903), (-1.425, 112.903), (-1.425, 114.903), (-1.425, 116.903), (-1.425, 118.903), (-1.425, 120.903), (-1.425, 122.903), (-1.425, 124.903), (-1.424, 126.903), (-1.424, 128.903), (-1.424, 130.903), (-1.424, 132.903), (-1.424, 134.903), (-1.424, 136.903), (-1.424, 138.903), (-1.424, 140.903), (-1.424, 142.903), (-1.424, 144.903), (-1.424, 146.903), (-1.424, 148.903), (-1.424, 150.903), (-1.424, 152.903), (-1.424, 154.903), (-1.424, 156.903), (-1.423, 158.903), (-1.423, 160.903), (-1.423, 162.903), (-1.423, 164.903), (-1.423, 166.903), (-1.423, 168.903), (-1.423, 170.903), (-1.423, 172.903), (-1.423, 174.903), (-1.423, 176.911), (-1.423, 176.911)]
wallStakeTestp2part2 = [(-19.446, 95.807), (-17.971, 97.157), (-16.506, 98.519), (-15.055, 99.896), (-13.623, 101.292), (-12.216, 102.713), (-10.837, 104.162), (-9.494, 105.644), (-8.193, 107.163), (-6.942, 108.723), (-5.747, 110.326), (-4.614, 111.974), (-3.549, 113.667), (-2.557, 115.403), (-1.638, 117.18), (-0.795, 118.993), (-0.028, 120.84), (0.668, 122.715), (1.296, 124.614), (1.858, 126.533), (2.361, 128.469), (2.81, 130.418), (3.206, 132.378), (3.557, 134.347), (3.867, 136.322), (4.139, 138.304), (4.377, 140.29), (4.584, 142.279), (4.763, 144.271), (4.916, 146.265), (5.046, 148.261), (5.155, 150.258), (5.245, 152.256), (5.317, 154.254), (5.373, 156.254), (5.415, 158.253), (5.443, 160.253), (5.459, 162.253), (5.463, 164.253), (5.457, 166.253), (5.441, 168.253), (5.416, 170.253), (5.383, 172.252), (5.342, 174.252), (5.294, 176.251), (5.24, 178.251), (5.179, 180.25), (5.112, 182.249), (5.04, 184.247), (4.963, 186.246), (4.845, 189.104), (4.845, 189.104)]
wallStakeTestp2part3 = [(-1.423, 176.911), (-1.323, 174.914), (-1.223, 172.916), (-1.122, 170.919), (-1.022, 168.921), (-0.922, 166.924), (-0.822, 164.926), (-0.722, 162.929), (-0.622, 160.931), (-0.521, 158.934), (-0.421, 156.936), (-0.321, 154.939), (-0.221, 152.941), (-0.121, 150.944), (-0.067, 149.867), (-0.067, 149.867)]
wallStakeTestp3 = [(-1.423, 176.911), (-1.323, 174.914), (-1.223, 172.916), (-1.122, 170.919), (-1.022, 168.921), (-0.922, 166.924), (-0.822, 164.926), (-0.722, 162.929), (-0.622, 160.931), (-0.521, 158.934), (-0.421, 156.936), (-0.321, 154.939), (-0.221, 152.941), (-0.121, 150.944), (-0.067, 149.867), (-0.067, 149.867)]
wallStakeTestp4 = [(-0.067, 149.867), (-0.039, 147.867), (-0.011, 145.867), (0.017, 143.867), (0.045, 141.868), (0.072, 139.868), (0.1, 137.868), (0.128, 135.868), (0.156, 133.868), (0.184, 131.869), (0.212, 129.869), (0.239, 127.869), (0.267, 125.869), (0.295, 123.869), (0.323, 121.87), (0.351, 119.87), (0.378, 117.87), (0.406, 115.87), (0.434, 113.87), (0.462, 111.871), (0.474, 110.985), (0.474, 110.985)]

rightwallStakeTestp1 = [(x, -y) for (x, y) in wallStakeTestp1]
rightwallStakeTestp2 = [(x, -y) for (x, y) in wallStakeTestp2]
rightwallStakeTestp2part2 = [(x, -y) for (x, y) in wallStakeTestp2part2]
rightwallStakeTestp2part3 = [(x, -y) for (x, y) in wallStakeTestp2part3]
rightwallStakeTestp3 = [(x, -y) for (x, y) in wallStakeTestp3]
rightwallStakeTestp4 = [(x, -y) for (x, y) in wallStakeTestp4]


















#SKILLS NEW STUFF
p1v2 = [(-159.385, 0.0), (-157.385, 0.0), (-155.385, 0.0), (-153.385, 0.0), (-151.385, 0.0), (-149.385, 0.0), (-147.385, 0.0), (-145.385, 0.0), (-143.385, 0.0), (-141.385, 0.0), (-139.385, 0.0), (-137.385, 0.0), (-135.385, 0.0), (-133.385, 0.0), (-131.385, 0.0)]
mogo_in_possession_1v2 = [(-119.894, 0.0), (-119.894, 2.0), (-119.894, 4.0), (-119.894, 6.0), (-119.894, 8.0), (-119.894, 10.0), (-119.894, 12.0), (-119.894, 14.0), (-119.894, 16.0), (-119.894, 18.0), (-119.894, 20.0), (-119.894, 22.0), (-119.894, 24.0), (-119.894, 26.0), (-119.894, 28.0), (-119.894, 30.0), (-119.894, 32.0), (-119.894, 34.0), (-119.894, 36.0), (-119.894, 38.0), (-119.894, 40.0), (-119.894, 42.0), (-119.894, 44.0), (-119.894, 46.0), (-119.894, 48.0), (-119.894, 50.0), (-119.894, 52.0), (-119.894, 54.0), (-119.894, 56.0), (-119.894, 58.0), (-119.894, 60.0), (-119.894, 62.0), (-119.894, 64.0), (-119.894, 66.0), (-119.894, 68.0), (-119.894, 70.0)]
p3v2 = [(-120.515, 61.5), (-118.564, 61.061), (-116.609, 60.638), (-114.65, 60.238), (-112.684, 59.872), (-110.714, 59.525), (-108.739, 59.207), (-106.76, 58.924), (-104.777, 58.663), (-102.79, 58.433), (-100.799, 58.242), (-98.806, 58.079), (-96.811, 57.944), (-94.813, 57.852), (-92.814, 57.796), (-90.814, 57.773), (-88.814, 57.784), (-86.815, 57.837), (-84.817, 57.935), (-82.822, 58.07), (-80.83, 58.244), (-78.841, 58.459), (-76.858, 58.715), (-74.881, 59.021), (-72.912, 59.37), (-70.951, 59.763), (-69.0, 60.199), (-67.058, 60.679), (-65.128, 61.203), (-63.211, 61.772), (-61.307, 62.384), (-59.418, 63.041), (-57.544, 63.74), (-55.687, 64.482), (-53.848, 65.267), (-52.026, 66.093), (-50.223, 66.959), (-48.439, 67.863), (-46.675, 68.804), (-44.929, 69.781), (-43.204, 70.792), (-41.498, 71.836), (-39.812, 72.911), (-38.145, 74.016), (-36.497, 75.149), (-34.867, 76.309), (-33.256, 77.494), (-31.662, 78.702), (-30.085, 79.932), (-28.524, 81.182), (-26.978, 82.451), (-25.446, 83.736), (-23.926, 85.037), (-22.419, 86.351), (-20.921, 87.677), (-19.434, 89.014), (-17.954, 90.359), (-16.481, 91.712), (-15.014, 93.071), (-13.55, 94.434), (-12.089, 95.8), (-10.629, 97.167), (-9.168, 98.533), (-7.705, 99.896), (-6.237, 101.255), (-4.764, 102.608), (-3.283, 103.952), (-1.793, 105.286), (-0.292, 106.607), (1.222, 107.914), (2.751, 109.203), (4.296, 110.473), (5.862, 111.717), (7.449, 112.935), (9.057, 114.123), (10.689, 115.279), (12.346, 116.399), (14.032, 117.476), (15.746, 118.505), (17.489, 119.485), (19.261, 120.413), (21.062, 121.284), (22.894, 122.084), (24.755, 122.817), (26.641, 123.481), (28.552, 124.072), (30.486, 124.58), (32.44, 125.004), (34.41, 125.348), (36.392, 125.611), (38.384, 125.791), (40.381, 125.89), (42.381, 125.901), (44.38, 125.835), (46.375, 125.693), (48.363, 125.479), (50.342, 125.195), (52.311, 124.846), (54.268, 124.435), (56.212, 123.965), (59.636, 123.0), (59.636, 123.0)]
p4v2 = [(60.879, 119.273), (59.327, 120.535), (57.774, 121.795), (56.21, 123.041), (54.642, 124.282), (53.064, 125.512), (51.478, 126.73), (49.887, 127.942), (48.282, 129.135), (46.671, 130.32), (45.049, 131.491), (43.416, 132.645), (41.774, 133.786), (40.12, 134.91), (38.451, 136.013), (36.771, 137.098), (35.079, 138.165), (33.371, 139.204), (31.646, 140.217), (29.907, 141.204), (28.151, 142.161), (26.377, 143.086), (24.586, 143.974), (22.774, 144.821), (20.942, 145.623), (19.088, 146.374), (17.213, 147.069), (15.316, 147.703), (13.398, 148.269), (11.46, 148.762), (9.504, 149.176), (7.531, 149.505), (5.544, 149.729), (3.548, 149.855), (1.549, 149.882), (-0.449, 149.787), (-2.438, 149.59), (-4.414, 149.281), (-6.371, 148.87), (-8.305, 148.361), (-10.212, 147.761), (-12.094, 147.085), (-13.948, 146.333), (-15.777, 145.526), (-17.582, 144.663), (-19.366, 143.761), (-21.134, 142.825), (-22.886, 141.861), (-24.628, 140.878), (-26.363, 139.882), (-28.092, 138.878), (-29.819, 137.87), (-31.548, 136.863), (-33.279, 135.862), (-35.015, 134.869), (-36.758, 133.888), (-38.509, 132.922), (-40.269, 131.973), (-42.04, 131.043), (-43.822, 130.134), (-45.615, 129.249), (-47.42, 128.388), (-49.238, 127.553), (-51.068, 126.746), (-52.91, 125.968), (-54.764, 125.219), (-56.63, 124.499), (-58.508, 123.81), (-60.396, 123.152), (-62.295, 122.524), (-64.204, 121.926), (-66.121, 121.359), (-68.048, 120.821), (-69.983, 120.317), (-71.927, 119.845), (-73.877, 119.402), (-75.833, 118.987), (-77.795, 118.598), (-79.763, 118.243), (-81.736, 117.918), (-83.714, 117.616), (-85.694, 117.338), (-87.679, 117.096), (-89.667, 116.876), (-91.657, 116.677), (-93.65, 116.508), (-95.645, 116.364), (-97.641, 116.237), (-99.638, 116.14), (-101.637, 116.064), (-103.636, 116.002), (-105.636, 115.974), (-107.636, 115.958), (-109.636, 115.965), (-111.635, 115.993), (-113.635, 116.033), (-115.634, 116.102), (-117.632, 116.179), (-119.629, 116.283), (-121.626, 116.396), (-123.622, 116.532), (-125.616, 116.679), (-127.609, 116.845), (-129.601, 117.025), (-131.591, 117.22), (-133.58, 117.43), (-135.568, 117.654), (-137.554, 117.891), (-139.538, 118.144), (-141.52, 118.405), (-143.501, 118.685), (-145.48, 118.97), (-147.457, 119.276), (-149.433, 119.583), (-151.405, 119.914), (-154.018, 120.355), (-154.018, 120.355)]
p5v2 = [(-162.758, 121.136), (-160.801, 121.339), (-158.851, 121.783), (-156.892, 122.189), (-154.922, 122.53), (-152.94, 122.798), (-150.949, 122.987), (-148.952, 123.095), (-146.952, 123.117), (-144.954, 123.055), (-142.959, 122.908), (-140.973, 122.675), (-138.999, 122.357), (-137.04, 121.955), (-135.099, 121.47), (-133.181, 120.904), (-131.288, 120.261), (-129.422, 119.542), (-127.585, 118.75), (-125.78, 117.89), (-124.007, 116.965), (-122.269, 115.975), (-120.566, 114.927), (-118.898, 113.823), (-117.266, 112.668), (-115.67, 111.463), (-114.11, 110.21), (-112.586, 108.916), (-111.096, 107.581), (-109.641, 106.21), (-108.221, 104.802), (-106.832, 103.362), (-105.477, 101.891), (-104.364, 100.636), (-104.364, 100.636)]
mogo_in_bottom_left_cornerv2 = [(-111.818, 111.197), (-113.253, 112.59), (-114.689, 113.983), (-116.124, 115.376), (-117.559, 116.769), (-118.994, 118.162), (-120.429, 119.555), (-121.864, 120.948), (-123.299, 122.341), (-124.735, 123.734), (-126.17, 125.126), (-127.605, 126.519), (-129.04, 127.912), (-130.475, 129.305), (-131.91, 130.698), (-133.346, 132.091), (-134.781, 133.484), (-136.216, 134.877), (-137.651, 136.27), (-139.086, 137.663), (-140.521, 139.056), (-141.957, 140.449), (-143.392, 141.842), (-144.827, 143.235), (-146.262, 144.628), (-147.697, 146.021), (-149.132, 147.414), (-150.568, 148.807), (-152.003, 150.2), (-153.438, 151.593), (-154.061, 152.197), (-154.061, 152.197)]
p7v2 = [(-157.167, 144.742), (-156.38, 142.903), (-155.594, 141.064), (-154.808, 139.225), (-154.022, 137.387), (-153.236, 135.548), (-152.449, 133.709), (-151.663, 131.87), (-150.877, 130.031), (-150.091, 128.192), (-149.304, 126.353), (-148.518, 124.514), (-147.732, 122.675), (-146.946, 120.836), (-146.159, 118.997), (-145.373, 117.158), (-144.587, 115.319), (-143.801, 113.48), (-143.015, 111.641), (-142.228, 109.802), (-141.442, 107.963), (-140.656, 106.124), (-139.87, 104.285), (-139.083, 102.446), (-138.297, 100.607), (-137.511, 98.768), (-136.725, 96.929), (-135.938, 95.09), (-135.152, 93.251), (-134.366, 91.412), (-133.58, 89.573), (-132.794, 87.734), (-132.007, 85.895), (-131.221, 84.056), (-130.435, 82.217), (-129.649, 80.378), (-128.862, 78.539), (-128.076, 76.7), (-127.29, 74.861), (-126.504, 73.022), (-125.717, 71.183), (-124.931, 69.344), (-124.145, 67.505), (-123.359, 65.666), (-122.573, 63.827), (-121.786, 61.988), (-121.0, 60.149), (-120.515, 59.015), (-120.515, 59.015)]
p8v2 = [(-119.273, 60.258), (-119.273, 58.258), (-119.273, 56.258), (-119.273, 54.258), (-119.273, 52.258), (-119.273, 50.258), (-119.273, 48.258), (-119.273, 46.258), (-119.273, 44.258), (-119.273, 42.258), (-119.273, 40.258), (-119.273, 38.258), (-119.273, 36.258), (-119.273, 34.258), (-119.273, 32.258), (-119.273, 30.258), (-119.273, 28.258), (-119.273, 26.258), (-119.273, 24.258), (-119.273, 22.258), (-119.273, 20.258), (-119.273, 18.258), (-119.273, 16.258), (-119.273, 14.258), (-119.273, 12.258), (-119.273, 10.258), (-119.273, 8.258), (-119.273, 6.258), (-119.273, 4.258), (-119.273, 2.258), (-119.273, 0.258), (-119.273, -1.742), (-119.273, -3.742), (-119.273, -5.742), (-119.273, -7.742), (-119.273, -9.742), (-119.273, -11.742), (-119.273, -13.742), (-119.273, -15.742), (-119.273, -17.394), (-119.273, -17.394)]
#mogo_in_possession_2v2 = [(-119.273, -29.197), (-119.326, -31.196), (-119.379, -33.196), (-119.433, -35.195), (-119.486, -37.194), (-119.539, -39.193), (-119.593, -41.193), (-119.646, -43.192), (-119.699, -45.191), (-119.753, -47.191), (-119.806, -49.19), (-119.859, -51.189), (-119.912, -53.188), (-119.966, -55.188), (-120.019, -57.187), (-120.072, -59.186), (-120.126, -61.186), (-120.179, -63.185), (-120.232, -65.184), (-120.286, -67.183), (-120.339, -69.183), (-120.392, -71.182), (-120.446, -73.181), (-120.499, -75.181), (-120.515, -75.788), (-120.515, -75.788)]




# pathfile: mogo_in_possession_2v2.txt
mogo_in_possession_2v2 = [(-119.273, -29.197, 120, 0), (-119.326, -31.196, 120), (-119.379, -33.196, 120), (-119.433, -35.195, 120), (-119.486, -37.194, 120), (-119.539, -39.193, 120), (-119.593, -41.193, 120), (-119.646, -43.192, 120), (-119.699, -45.191, 120), (-119.753, -47.191, 120), (-119.806, -49.19, 120), (-119.859, -51.189, 120), (-119.912, -53.188, 120), (-119.966, -55.188, 120), (-120.019, -57.187, 120), (-120.072, -59.186, 120), (-120.126, -61.186, 120), (-120.179, -63.185, 120), (-120.232, -65.184, 120), (-120.286, -67.183, 120), (-120.339, -69.183, 120), (-120.392, -71.182, 120), (-120.446, -73.181, 120), (-120.499, -75.181, 120), (-120.515, -75.788, 120, 0), (-120.515, -75.788, 0, 0)]












def autonomous_test():
    global lookahead, tolerance, increasing_x, test_square, intake_state, high_score_target_angle, test_circle, gyro, eject_object, forward_velocity, turn_velocity_k
    #walk_path(increasing_x, lookahead, tolerance, 1)
   
    #mogo_p.set(True)
    #wait(1, SECONDS)
    #high_score_target_angle = HIGH_SCORE_TARGET_ANGLE_WAIT
    #adjust_high_scoring_motor_position()
    #intake_state = IntakeState.RUNNING  
    #set_intake_motor_state(REVERSE)
    #gyro.set_heading(180, DEGREES)
    # Reverse the test_circle path
    # reversed_test_circle = test_circle[::-1]


    #walk_path(reversed_test_circle, lookahead, tolerance, 1)
    lookahead = 50
    forward_velocity = 50
    turn_velocity_k = 50
    wall_score_on = False

    #walk_path(straight_line_test, lookahead, tolerance, 1, True)

    set_high_score_angle(HIGH_SCORE_TARGET_ANGLE_WAIT)
    adjust_high_scoring_motor_position()
    intake_state = IntakeState.RUNNING
    wait(100, MSEC)
    set_intake_motor_state(REVERSE)
    wait(1000, MSEC)
    
    walk_path(p1v2, lookahead, tolerance, 1)
    pidTurnToAngle(90)
    forward_velocity = 40
    turn_velocity_k = 40
    walk_path(mogo_in_possession_1v2, lookahead, tolerance, -1)
    mogo_p.set(True)
    forward_velocity = 50
    turn_velocity_k = 50
    walk_path(p3v2, lookahead, tolerance, 1)
    forward_velocity = 35
    turn_velocity_k = 35
    walk_path(p4v2, lookahead, tolerance, 1)
    walk_path(p5v2, lookahead, tolerance, 1)
    walk_path(mogo_in_bottom_left_cornerv2, lookahead, tolerance, -1)
    forward_velocity = 55
    turn_velocity_k = 55
    mogo_p.set(False)
    walk_path(p7v2, lookahead, tolerance, 1)
    walk_path(p8v2, lookahead, tolerance, 1)
    pidTurnToAngle(270)
    walk_path(mogo_in_possession_2v2, lookahead, tolerance, 1)
    mogo_p.set(True)

    print("Done")


    


testc1 = [(-119.273, 52.803), (-119.287, 50.803), (-119.302, 48.803), (-119.316, 46.803), (-119.33, 44.803), (-119.345, 42.803), (-119.359, 40.803), (-119.373, 38.803), (-119.388, 36.803), (-119.402, 34.803), (-119.417, 32.804), (-119.431, 30.804), (-119.445, 28.804), (-119.46, 26.804), (-119.474, 24.804), (-119.489, 22.804), (-119.503, 20.804), (-119.517, 18.804), (-119.532, 16.804), (-119.546, 14.804), (-119.56, 12.804), (-119.575, 10.804), (-119.589, 8.804), (-119.604, 6.804), (-119.618, 4.804), (-119.632, 2.804), (-119.647, 0.804), (-119.661, -1.196), (-119.676, -3.196), (-119.69, -5.195), (-119.704, -7.195), (-119.719, -9.195), (-119.733, -11.195), (-119.748, -13.195), (-119.762, -15.195), (-119.776, -17.195), (-119.791, -19.195), (-119.805, -21.195), (-119.819, -23.195), (-119.834, -25.195), (-119.848, -27.195), (-119.863, -29.195), (-119.877, -31.195), (-119.891, -33.195), (-119.906, -35.195), (-119.92, -37.195), (-119.935, -39.195), (-119.949, -41.195), (-119.963, -43.194), (-119.978, -45.194), (-119.992, -47.194), (-120.007, -49.194), (-120.021, -51.194), (-120.035, -53.194), (-120.05, -55.194), (-120.064, -57.194), (-120.078, -59.194), (-120.093, -61.194), (-120.107, -63.194), (-120.122, -65.194), (-120.136, -67.194), (-120.15, -69.194), (-120.165, -71.194), (-120.179, -73.194), (-120.194, -75.194), (-120.208, -77.194), (-120.222, -79.194), (-120.237, -81.194), (-120.251, -83.193), (-120.266, -85.193), (-120.28, -87.193), (-120.294, -89.193), (-120.309, -91.193), (-120.323, -93.193), (-120.337, -95.193), (-120.352, -97.193), (-120.366, -99.193), (-120.381, -101.193), (-120.395, -103.193), (-120.409, -105.193), (-120.424, -107.193), (-120.438, -109.193), (-120.453, -111.193), (-120.467, -113.193), (-120.481, -115.193), (-120.496, -117.193), (-120.51, -119.193), (-120.498, -118.595), (-120.471, -116.596), (-120.444, -114.596), (-120.417, -112.596), (-120.39, -110.596), (-120.362, -108.596), (-120.335, -106.597), (-120.308, -104.597), (-120.281, -102.597), (-120.254, -100.597), (-120.227, -98.597), (-120.2, -96.598), (-120.173, -94.598), (-120.146, -92.598), (-120.119, -90.598), (-120.092, -88.598), (-120.065, -86.598), (-120.038, -84.599), (-120.011, -82.599), (-119.984, -80.599), (-119.957, -78.599), (-119.93, -76.599), (-119.903, -74.6), (-119.876, -72.6), (-119.849, -70.6), (-119.822, -68.6), (-119.795, -66.6), (-119.768, -64.6), (-119.741, -62.601), (-119.714, -60.601), (-119.687, -58.601), (-119.66, -56.601), (-119.633, -54.601), (-119.606, -52.602), (-119.579, -50.602), (-119.552, -48.602), (-119.525, -46.602), (-119.498, -44.602), (-119.471, -42.602), (-119.444, -40.603), (-119.417, -38.603), (-119.39, -36.603), (-119.363, -34.603), (-119.336, -32.603), (-119.309, -30.604), (-119.273, -27.955), (-119.273, -27.955)]


"""def consistency_test():
    global lookahead, tolerance, increasing_x, test_square, intake_state, high_score_target_angle, test_circle, gyro, eject_object, forward_velocity, turn_velocity_k
    lookahead = 50
    forward_velocity = 45
    forward_velocity = 45
    walk_path(alliance_stake, 5, tolerance, 1)
    print("alliance done with turning")
    walk_path(grabbing_mogo, lookahead, tolerance, -1)
    walk_path(testc1, lookahead, tolerance, 1)"""



def unscoring():
    print("Hi")

# Create a Competition object
#competition = Competition(drivercontrol, autonomous)
def main():
    # Any initialization code before the match starts
    print("Running main.py")
    wait(3, SECONDS)
    autonomous_test()
    #consistency_test()

main()