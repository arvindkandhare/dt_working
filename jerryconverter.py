# Input data as a multiline string
data = """
-57.389,70.195,120,0
-57.595,85.434,120
-58.117,100.664,120
-58.991,115.879,120
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