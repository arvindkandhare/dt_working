#region VEXcode Generated Robot Configuration
from vex import *
import urandom

# Brain should be defined by default
brain=Brain()

# Robot configuration code


# wait for rotation sensor to fully initialize
wait(30, MSEC)


# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))
      
# Set random seed 
initializeRandomSeed()


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
pos_list = []
passed_through_list = []


wheel_circumference = 8.6393798
feet_to_unit = 2.5
gear_ratio = 3/4
tolerance = 1


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

while True:
    update_position()
    print(str(current_x)
    print(str(current_y)