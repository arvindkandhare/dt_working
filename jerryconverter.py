# Input data as a multiline string
data = """
58.984,75.725,120,0
58.984,96.045,120
58.984,101.595,120
58.984,118.947,120,0
58.984,118.947,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)