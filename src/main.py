# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       aarohkandy                                                   #
# 	Created:      11/9/2024, 5:27:20 AM                                        #
# 	Description:  V5 project                                                   #
#                                                                              #
# ---------------------------------------------------------------------------- #

#region VEXcode Generated Robot Configuration
from vex import *
import urandom
import time

# Brain should be defined by default
brain = Brain()

# Robot configuration code
r1 = Motor(Ports.PORT1, GearSetting.RATIO_18_1, False)
r2 = Motor(Ports.PORT2, GearSetting.RATIO_18_1, False)
r3 = Motor(Ports.PORT3, GearSetting.RATIO_18_1, False)
l1 = Motor(Ports.PORT11, GearSetting.RATIO_18_1, True)
l2 = Motor(Ports.PORT12, GearSetting.RATIO_18_1, True)
l3 = Motor(Ports.PORT13, GearSetting.RATIO_18_1, True)
l1.spin(FORWARD)
l2.spin(FORWARD)
l3.spin(FORWARD)
r1.spin(FORWARD)
r2.spin(FORWARD)
r3.spin(FORWARD)
# Create MotorGroups for each side (with three motors each)
left_drive_smart = MotorGroup(l1, l2, l3)
right_drive_smart = MotorGroup(r1, r2, r3)

# Create DriveTrain with updated MotorGroups
drivetrain = DriveTrain(left_drive_smart, right_drive_smart, 219.44, 295, 40, MM, 1)

intake = Motor(Ports.PORT18, GearSetting.RATIO_18_1, False)
mogo_p = DigitalOut(brain.three_wire_port.c)
intake_p = DigitalOut(brain.three_wire_port.b)
controller_1 = Controller(PRIMARY)
High_scoring = Motor(Ports.PORT20, GearSetting.RATIO_36_1, False)
High_scoring.set_max_torque(100, PERCENT)
High_scoring.set_velocity(100, PERCENT)

intake.set_max_torque(100, PERCENT)
intake.set_velocity(100, PERCENT)

# Wait for rotation sensor to fully initialize
wait(30, MSEC)

# Make random actually random
def initializeRandomSeed():
    wait(100, MSEC)
    random = brain.battery.voltage(MV) + brain.battery.current(CurrentUnits.AMP) * 100 + brain.timer.system_high_res()
    urandom.seed(int(random))

# Set random seed
initializeRandomSeed()

# Define toggle states and stall management variables
intake_running = False
high_scoring_running = False
STALL_THRESHOLD = 10  # Velocity threshold for detecting a stall
STALL_COUNT = 3  # Count threshold for detecting a stall
RETRY_LIMIT = 3  # Maximum number of retry attempts
REVERSE_TIME = 1500  # Time in milliseconds to reverse
RETRY_INTERVAL = 500  # Interval between retry attempts in milliseconds
current_direction = FORWARD  # Assuming FORWARD is a predefined constant

# Variables to handle intake stall recovery
intake_stalled = False
retry_count = 0
last_retry_time = 0
consecutive_stall_count = 0
reverse_drive = False

def display_joystick_positions():
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print(str(int(controller_1.axis3.position())) + " " + str(int(controller_1.axis2.position())))
    wait(0.1, SECONDS)

def set_drive_motor_velocities():
    global reverse_drive
    if controller_1.buttonUp.pressing():
        reverse_drive = not reverse_drive
        while controller_1.buttonUp.pressing():
            wait(10, MSEC)

    if reverse_drive:
        # Reverse the direction of both joystick inputs
        left_joystick_y = -controller_1.axis2.position()  # Left joystick maps to right motors
        right_joystick_y = -controller_1.axis3.position() # Right joystick maps to left motors
    else:
        # Normal control
        left_joystick_y = controller_1.axis3.position()
        right_joystick_y = controller_1.axis2.position()

        # Set velocities for the left and right drive motors
        left_drive_smart.set_velocity(left_joystick_y, PERCENT)
        if abs(left_joystick_y) < 5:
            left_drive_smart.stop()  # Stop the left side if joystick is in deadband
        else:
            left_drive_smart.spin(FORWARD)  # Spin in the FORWARD direction

        right_drive_smart.set_velocity(right_joystick_y, PERCENT)
        if abs(right_joystick_y) < 5:
            right_drive_smart.stop()  # Stop the right side if joystick is in deadband
        else:
           right_drive_smart.spin(FORWARD)  # Spin in the FORWARD direction
   
def toggle_high_scoring_motor():
    global high_scoring_running
    if controller_1.buttonL1.pressing():
        wait(100, MSEC)  # Debounce delay
        if not high_scoring_running:
            High_scoring.spin(FORWARD)
        else:
            High_scoring.stop()
        high_scoring_running = not high_scoring_running
        while controller_1.buttonL1.pressing():
            wait(10, MSEC)

    if controller_1.buttonL2.pressing():
        wait(100, MSEC)  # Debounce delay
        if not high_scoring_running:
            High_scoring.spin(REVERSE)
        else:
            High_scoring.stop()
        high_scoring_running = not high_scoring_running
        while controller_1.buttonL2.pressing():
            wait(10, MSEC)

def toggle_intake_motor():
    global intake_running, current_direction
    if controller_1.buttonR1.pressing():
        wait(100, MSEC)  # Debounce delay
        if not intake_running:
            intake.spin(FORWARD)
            current_direction = FORWARD
        else:
            intake.stop()
        intake_running = not intake_running
        while controller_1.buttonR1.pressing():
            wait(10, MSEC)

    if controller_1.buttonR2.pressing():
        wait(100, MSEC)  # Debounce delay
        if not intake_running:
            intake.spin(REVERSE)
            current_direction = REVERSE
        else:
            intake.stop()
        intake_running = not intake_running
        while controller_1.buttonR2.pressing():
            wait(10, MSEC)

def stall_detection_and_handling():
    global consecutive_stall_count, intake_stalled, retry_count, last_retry_time
    current_time = time.ticks_ms()
    if intake_running:
        current_velocity = intake.velocity(PERCENT)
        if abs(current_velocity) <= STALL_THRESHOLD:
            consecutive_stall_count += 1
        else:
            consecutive_stall_count = 0

        if consecutive_stall_count >= STALL_COUNT and not intake_stalled:
            intake_stalled = True
            consecutive_stall_count = 0
            retry_count = 0
            last_retry_time = current_time
    else:
        intake_stalled = False
        consecutive_stall_count = 0

def retry_mechanism():
    global intake_stalled, retry_count, last_retry_time, current_direction
    current_time = time.ticks_ms()
    if intake_stalled:
        if retry_count < RETRY_LIMIT and current_time - last_retry_time > RETRY_INTERVAL:
            print("Spinning in opposite direction")
            if current_direction == FORWARD:
                intake.spin(REVERSE)
            else:
                intake.spin(FORWARD)
            wait(REVERSE_TIME, MSEC)
            retry_count += 1
            last_retry_time = current_time
            print("Spinning back")
            intake.spin(current_direction)
            intake_stalled = False

def handle_digital_outputs():
    if controller_1.buttonA.pressing():
        mogo_p.set(False)
        for i in range(5):
            brain.screen.print("button")
    if controller_1.buttonY.pressing():
        mogo_p.set(True)
        for i in range(5):
            brain.screen.print("button")
    if controller_1.buttonX.pressing():
        intake_p.set(False)
        for i in range(5):
            print("button")
    if controller_1.buttonB.pressing():
        intake_p.set(True)
        for i in range(5):
            print("button")

# Main control loop
while True:
    display_joystick_positions()
    set_drive_motor_velocities()
    toggle_high_scoring_motor()
    toggle_intake_motor()
    stall_detection_and_handling()
    retry_mechanism()
    handle_digital_outputs()
    wait(10, MSEC)  # Main loop delay