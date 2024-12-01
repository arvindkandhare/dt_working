# Input data as a multiline string
data = """
-61.184,58.812,99,0
-60.376,74.03,99
-60.46,89.264,99
-61.149,104.481,99
-60.235,119.522,99,0
-60.235,119.522,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)