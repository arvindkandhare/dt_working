import re
import json

def convert_jerryio_to_list(jerryio_file):
    with open(jerryio_file, 'r') as f:
        lines = f.readlines()

    path_points = []
    path_points_section = False

    for line in lines:
        if line.startswith("#PATH-POINTS-START"):
            path_points_section = True
            continue
        if line.startswith("#PATH.JERRYIO-DATA"):
            path_points_section = False
            continue
        if path_points_section:
            components = line.strip().split(',')
            point = tuple(float(c) if i < 2 else int(c) for i, c in enumerate(components))
            path_points.append(point)

    return path_points

def process_main_file(main_file_path, target_path):
    pattern = re.compile(r'# pathfile:\s*(.+\.txt)')
    new_lines = []
    with open(main_file_path, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        match = pattern.search(line)
        if match:
            path_filename = match.group(1)
            path_data = convert_jerryio_to_list(path_filename)
            if i+1 < len(lines) and '=' in lines[i+1]:
                var_line = lines[i+1].split('=')[0].strip()
                new_lines.append(line)
                new_lines.append(f"{var_line} = {path_data}\n")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(target_path, 'w') as f:
        f.writelines(new_lines)

# Usage
process_main_file('main.py', 'main_temp.py')