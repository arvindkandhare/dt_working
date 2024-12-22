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
intake1 = Motor(Ports.PORT1)
intake2 = Motor(Ports.PORT13)
mogo_p = DigitalOut(brain.three_wire_port.a)
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

# Global variables
retry_count = 0
consecutive_stall_count = 0
high_scoring_running = False
high_score_stall = False  # Set this accordingly in your main code if needed

# Function to set the state of the high scoring motor
def set_high_scoring_motor_state(state, direction=FORWARD, angle=0):
    global high_scoring_running
    if state:
        High_scoring.set_velocity(95, PERCENT)
        High_scoring.spin(direction)
    else:
        High_scoring.stop()
    high_scoring_running = state

# Function to set the state of the intake motor
def set_intake_motor_state(direction=FORWARD):
    global intake_state, current_direction
    if intake_state == IntakeState.RUNNING or intake_state == IntakeState.FIXINGSTALL:
        intake1.set_velocity(95, PERCENT)
        intake2.set_velocity(95, PERCENT)
        intake1.spin(direction)
        intake2.spin(REVERSE if direction == FORWARD else FORWARD)
        current_direction = direction
    else:
        intake1.stop()
        intake2.stop()

# Stall detection and handling for the intake motor
def stall_detection_and_handling():
    global intake_state, consecutive_stall_count, retry_count, high_score_stall
    global current_direction
    if intake_state == IntakeState.RUNNING or intake_state == IntakeState.STALLED:
        current_velocity = intake1.velocity(PERCENT)
        if abs(current_velocity) <= STALL_THRESHOLD:
            #print("Stalled" + str(consecutive_stall_count))
            consecutive_stall_count += 1
        else:
            consecutive_stall_count = 0

        if consecutive_stall_count >= STALL_COUNT:
            #print("Unstaling")
            intake_state = IntakeState.FIXINGSTALL
            # Start in opposite direction
            current_direction = REVERSE if current_direction == FORWARD else FORWARD
            set_intake_motor_state(current_direction)
            if high_scoring_running:
                high_score_stall = True
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
                current_direction = REVERSE if current_direction == FORWARD else FORWARD
                set_intake_motor_state(current_direction)
        else:
            print("Retrying")
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
lookahead = 5
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
        if len(points_list) == 0:
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
    set_high_scoring_motor_state(True, FORWARD)
    wait(1, SECONDS)
    set_high_scoring_motor_state(False)

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
    if controller_1.buttonUp.pressing():
        reverse_drive = not reverse_drive
        while controller_1.buttonUp.pressing():
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
    global high_scoring_running
    if controller_1.buttonL1.pressing():
        wait(100, MSEC)  # Debounce delay
        high_scoring_running = not high_scoring_running
        set_high_scoring_motor_state(high_scoring_running, FORWARD)
        while controller_1.buttonL1.pressing():
            wait(1000, MSEC)

    if controller_1.buttonL2.pressing():
        wait(100, MSEC)  # Debounce delay
        high_scoring_running = not high_scoring_running
        set_high_scoring_motor_state(high_scoring_running, REVERSE)
        while controller_1.buttonL2.pressing():
            wait(1000, MSEC)

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
    if controller_1.buttonA.pressing():
        print("Mogo 1")
        mogo_p.set(False)
    if controller_1.buttonY.pressing():
        print("Mogo 2")
        mogo_p.set(True)
    if controller_1.buttonX.pressing():
        intake_p.set(False)
    if controller_1.buttonB.pressing():
        intake_p.set(True)
    if controller_1.buttonLeft.pressing():
        donker.set(True)
    if controller_1.buttonRight.pressing():
        donker.set(False)


# Function to toggle high scoring mode
def toggle_high_scoring_mode():
    global high_scoring_mode
    if controller_1.buttonDown.pressing():
        wait(100, MSEC)  # Debounce delay
        high_scoring_mode = not high_scoring_mode
        while controller_1.buttonDown.pressing():
            wait(10, MSEC)

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
        intake1.set_velocity(100, PERCENT)
        intake2.set_velocity(100, PERCENT)   
# Driver control function
def drivercontrol():
    # Main control loop for driver control
    while True:
        set_drive_motor_velocities()
        toggle_high_scoring_motor()
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
    global lookahead, tolerance, increasing_x
    walk_path(increasing_x, lookahead, tolerance, 1)


# Create a Competition object
#competition = Competition(drivercontrol, autonomous)

def main():
    # Any initialization code before the match starts
    print("Running main.py")
    #wait(3, SECONDS)
    #mogo_p.set(False)
    #intake_p.set(True)
    #autonomous_test()
    drivercontrol()
    #intake_p.set(True)
    #drivercontrol()


main()