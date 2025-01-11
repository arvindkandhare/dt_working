# Input data as a multiline string
data = """
-46.656,157.218,120,0
-35.059,162.138,120
-23.127,159.273,120
-15.844,149.022,120
-12.243,136.872,120
-10.991,124.25,120
-11.275,111.563,120
-13.306,99.038,120
-16.969,86.899,120
-22.725,76.331,120,0
-22.725,76.331,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)