# Input data as a multiline string
data = """
-66.948,66.505,120,315
-65.755,81.698,120
-63.714,96.795,120
-60.605,111.714,120
-59.156,118.226,120,0
-59.156,118.226,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)