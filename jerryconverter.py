# Input data as a multiline string
data = """
-151.774,126.162,271,0
-132.813,121.614,271
-116.614,109.405,271
-101.657,95.657,271
-87.22,81.358,271
-72.93,66.912,271
-62.038,56.275,271,0
-62.038,56.275,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)