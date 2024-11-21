# Input data as a multiline string
data = """
-69.531,148.924,120,0
-57.392,152.459,120
-44.93,151.127,120
-34.453,144.166,120
-27.05,133.892,120
-21.979,122.263,120
-18.617,110.025,120
-16.793,97.468,120
-16.696,94.821,120,0
-16.696,94.821,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)