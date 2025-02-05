# Input data as a multiline string
data = """
118.099,93.436,120,0
119.23,95.085,120
120.36,96.735,120
121.491,98.385,120
122.622,100.035,120
123.752,101.684,120
124.883,103.334,120
126.014,104.984,120
127.145,106.633,120
128.275,108.283,120
129.406,109.933,120
130.537,111.582,120
131.667,113.232,120
132.798,114.882,120
133.929,116.532,120
135.059,118.181,120
136.19,119.831,120
137.321,121.481,120
138.452,123.13,120
139.582,124.78,120
140.713,126.43,120
141.844,128.08,120
142.974,129.729,120
144.105,131.379,120
145.236,133.029,120
146.366,134.678,120
147.031,135.648,120,0
147.031,135.648,0,0
"""

 

# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)