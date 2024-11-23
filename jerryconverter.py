# Input data as a multiline string
data = """
62.345,117.716,120,0
54.091,99.15,120
46.169,80.438,120
38.288,61.709,120
30.311,43.02,120
25.572,34.448,120,0
25.572,34.448,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)