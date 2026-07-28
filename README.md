# dt_working

VEX V5 drivetrain control and autonomous-path tooling (VEXcode Python).

## What's here
- **`main.py`** — drivetrain and mechanism control for a competition robot: a six-motor tank drive (three `RATIO_6_1` motors per side in `MotorGroup`s), plus high-scoring and dual-intake motors, driven from the primary controller.
- **`jerryconverter.py`** — converts [Jerry.io](https://path.jerryio.com/) path exports into motion commands the robot can run during autonomous.
- **`*.jerryio.txt`** — saved autonomous paths (e.g. `red_left_mogo`, `red_left_firststack`).

## Use
Open in VEXcode / PROS Python, adjust the port and gear-ratio constants at the top of `main.py` to match your robot, and download to the V5 brain. Regenerate autonomous routines by exporting a path from Jerry.io and running it through `jerryconverter.py`.
