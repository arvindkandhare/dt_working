#region VEXcode Generated Robot Configuration
from vex import *

# Brain should be defined by default
brain=Brain()



# wait for rotation sensor to fully initialize
wait(30, MSEC)

def play_vexcode_sound(sound_name):
    # Helper to make playing sounds from the V5 in VEXcode easier and
    # keeps the code cleaner by making it clear what is happening.
    print("VEXPlaySound:" + sound_name)
    wait(5, MSEC)

# add a small delay to make sure we don't print in the middle of the REPL header
wait(200, MSEC)
# clear the console to make sure we don't have the REPL in the console
print("\033[2J")

#endregion VEXcode Generated Robot Configuration

# ------------------------------------------
# 
# 	Project:      VEXcode Project
#	Author:       VEX
#	Created:
#	Description:  VEXcode V5 Python Project
# 
# ------------------------------------------

# Library imports
from vex import *

# Begin project code

#INITIALIZING
Mogo = DigitalOut(brain.three_wire_port.a)
IntakePiston = DigitalOut(brain.three_wire_port.b)
controller_1 = Controller(PRIMARY)
# i added a comment!
left_motor_a = Motor(Ports.PORT1, GearSetting.RATIO_6_1, True)
left_motor_b = Motor(Ports.PORT2, GearSetting.RATIO_6_1, True)
left_motor_c = Motor(Ports.PORT3, GearSetting.RATIO_6_1, True)

right_motor_a = Motor(Ports.PORT11, GearSetting.RATIO_6_1, False)
right_motor_b = Motor(Ports.PORT12, GearSetting.RATIO_6_1, False)
right_motor_c = Motor(Ports.PORT13, GearSetting.RATIO_6_1, False)

left_drive_smart = MotorGroup(left_motor_a, left_motor_b, left_motor_c)
right_drive_smart = MotorGroup(right_motor_a, right_motor_b, right_motor_c)

drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 219.44, 295, 40, MM, 1)

Intake = Motor(Ports.PORT10, GearSetting.RATIO_6_1, False)
IntakeSmall = Motor(Ports.PORT9, GearSetting.RATIO_6_1, True)

#gyro start
gyro = Inertial(Ports.PORT19)
gyro.set_rotation(0, DEGREES)
gyro.set_heading(0, DEGREES)

gyro.calibrate()

#list definitions 
pos_list = [(0,0), (0,10), (0,20), (0,30), (0,40), (0,50), (0,60), (0,70), (0,80), (0,90), (0,100)]
passed_through_list = []


wheel_circumference = 8.6393798
feet_to_unit = 2.5
gear_ratio = 3/4
tolerance = 1
lookahead = 3
current_x = pos_list[0][0]
current_y = pos_list[0][0]
previous_right_encoder = 0
previous_left_encoder = 0
forward_velocity = 35
turn_velocity_k = forward_velocity/100

def leftEncoder():
    return (left_motor_a.position(DEGREES) + left_motor_b.position(DEGREES) + left_motor_c.position(DEGREES)) / 3

def rightEncoder():
    return (right_motor_a.position(DEGREES) + right_motor_b.position(DEGREES) + right_motor_c.position(DEGREES)) / 3

def update_position():
    global current_x, current_y, current_angle, previous_left_encoder, previous_right_encoder
    
    # Calculate the distance traveled by each wheel
    left_encoder = ((leftEncoder() / 360) * wheel_circumference * gear_ratio) * feet_to_unit
    right_encoder = ((rightEncoder() / 360) * wheel_circumference * gear_ratio) * feet_to_unit
    delta_left = left_encoder - previous_left_encoder
    delta_right = right_encoder - previous_right_encoder
    
    # Update previous encoder values
    previous_left_encoder = left_encoder 
    previous_right_encoder = right_encoder 
    
    current_angle = math.radians(gyro.heading(DEGREES))
    
    # Calculate the robot's linear change
    delta_d = (delta_left + delta_right) / 2
    
    current_x += delta_d * math.cos(current_angle)
    current_y += delta_d * math.sin(current_angle)

    return current_x, current_y


def calculate_lookahead_point(pos_list, current_x, current_y):
    if len(pos_list) == 0:
        return "done"
    dx = pos_list[0][0] - current_x
    dy = pos_list[0][1] - current_y
    while math.sqrt((dx**2 + dy**2)) < lookahead:
        pos_list.pop(0)
        dx = pos_list[0][0] - current_x
        dy = pos_list[0][1] - current_y
    return pos_list

def calculate_drive_speeds(pos_list, current_x, current_y, forward_velocity, turn_velocity_k):
    current_angle = math.radians(gyro.heading(DEGREES))
    dx = pos_list[0][0] - current_x
    dy = pos_list[0][1] - current_y

    point_angle_diff = math.atan2(dy, dx) - current_angle

    if point_angle_diff > math.pi:
        point_angle_diff = point_angle_diff - 2*math.pi

    if point_angle_diff < math.pi:
        point_angle_diff = point_angle_diff + 2*math.pi

    left_velocity = forward_velocity - turn_velocity_k
    right_velocity = forward_velocity + turn_velocity_k

    return max(min(left_velocity, 100), -100), max(min(right_velocity, 100), -100)





while True:
    left_drive_smart.spin(FORWARD)
    right_drive_smart.spin(FORWARD)


    current_x, current_y = update_position()
    pos_list = calculate_lookahead_point(pos_list, current_x, current_y)
    if pos_list == "done":
        break
    left_velocity, right_velocity = calculate_drive_speeds(pos_list, current_x, current_y, forward_velocity, turn_velocity_k)

    left_drive_smart.set_velocity(left_velocity, PERCENT)
    right_drive_smart.set_velocity(right_velocity, PERCENT)


    print(str(current_x))
    print(str(current_y))