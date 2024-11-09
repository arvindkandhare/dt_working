# ---------------------------------------------------------------------------- #
#                                                                              #
# 	Module:       main.py                                                      #
# 	Author:       aarohkandy                                                     #
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
intake = Motor(Ports.PORT18, GearSetting.RATIO_18_1, False)
mogo_p = DigitalOut(brain.three_wire_port.c)
intake_p = DigitalOut(brain.three_wire_port.b)
controller_1 = Controller(PRIMARY)
High_scoring = Motor(Ports.PORT20, GearSetting.RATIO_36_1, False)

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
STALL_THRESHOLD = 0  # Velocity threshold for detecting a stall
STALL_COUNT = 10  # Count threshold for detecting a stall
RETRY_LIMIT = 3      # Maximum number of retry attempts
REVERSE_TIME = 2   # Time in milliseconds to reverse
RETRY_INTERVAL = 500 # Interval between retry attempts in milliseconds
current_direction = FORWARD  # Assuming FORWARD is a predefined constant
REVERSE_TIME = 1500  # Time to reverse in milliseconds

# Variables to handle intake stall recovery
intake_stalled = False
retry_count = 0
last_retry_time = 0
consecutive_stall_count = 0

# Main control loop
while True:
    # Display joystick positions
    brain.screen.clear_screen()
    brain.screen.set_cursor(1, 1)
    brain.screen.print(str(int(controller_1.axis3.position())) + " " + str(int(controller_1.axis2.position())))
    wait(0.1, SECONDS)

    # Set motor velocities based on joystick positions for the drive motors
    l1.set_velocity(int(controller_1.axis3.position()), PERCENT)
    l2.set_velocity(int(controller_1.axis3.position()), PERCENT)
    l3.set_velocity(int(controller_1.axis3.position()), PERCENT)
    r1.set_velocity(int(controller_1.axis2.position()), PERCENT)
    r2.set_velocity(int(controller_1.axis2.position()), PERCENT)
    r3.set_velocity(int(controller_1.axis2.position()), PERCENT)

    # Toggle for High_scoring motor with buttonL1
    if controller_1.buttonL1.pressing():
        wait(100, MSEC)  # Debounce delay
        if not high_scoring_running:
            High_scoring.spin(FORWARD)
        else:
            High_scoring.stop()
        high_scoring_running = not high_scoring_running
        # Wait until the button is released to register the next press
        while controller_1.buttonL1.pressing():
            wait(10, MSEC)

    # Toggle for High_scoring motor in the opposite direction with buttonL2
    if controller_1.buttonL2.pressing():
        wait(100, MSEC)  # Debounce delay
        if not high_scoring_running:
            High_scoring.spin(REVERSE)
        else:
            High_scoring.stop()
        high_scoring_running = not high_scoring_running
        # Wait until the button is released to register the next press
        while controller_1.buttonL2.pressing():
            wait(10, MSEC)

    # Toggle for intake motor with buttonR1
    if controller_1.buttonR1.pressing():
        wait(100, MSEC)  # Debounce delay
        if not intake_running:
            current_direction = FORWARD
            intake.spin(FORWARD)
        else:
            intake.stop()
        intake_running = not intake_running
        # Wait until the button is released to register the next press
        while controller_1.buttonR1.pressing():
            wait(10, MSEC)

    # Toggle for intake motor in the opposite direction with buttonR2
    if controller_1.buttonR2.pressing():
        wait(100, MSEC)  # Debounce delay
        if not intake_running:
            intake.spin(REVERSE)
            current_direction = REVERSE
        else:
            intake.stop()
        intake_running = not intake_running
        # Wait until the button is released to register the next press
        while controller_1.buttonR2.pressing():
            wait(10, MSEC)

    # Stall detection and handling for intake motor without blocking
    current_time = time.ticks_ms()
    if intake_running:
        if abs(intake.velocity(PERCENT)) <= STALL_THRESHOLD:
            consecutive_stall_count += 1
        else:
            consecutive_stall_count = 0

        if consecutive_stall_count >= STALL_COUNT and not intake_stalled:
            # Enter stalled state
            intake_stalled = True
            consecutive_stall_count = 0
            retry_count = 0
            last_retry_time = current_time  # Start timing for retry attempts
    else:
        intake_stalled = False
        consecutive_stall_count = 0
        
    if intake_stalled:
        # Check if it's time for another retry attempt
        if retry_count < RETRY_LIMIT and current_time - last_retry_time > RETRY_INTERVAL:
            # Reverse briefly to attempt clearing the blockage
            print("Spinning in opposite direction")
            if current_direction == FORWARD:
                intake.spin(REVERSE)
            else:
                intake.spin(FORWARD)
            wait(REVERSE_TIME, MSEC)  # Brief reverse time
            retry_count += 1
            last_retry_time = current_time  # Update last retry time
            print("Spinning back")
            intake.spin(current_direction)
            intake_stalled = False
       
    # Handle digital outputs based on other buttons
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

