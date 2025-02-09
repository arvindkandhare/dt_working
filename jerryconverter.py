# Input data as a multiline string
data = """#PATH-POINTS-START Path
-56.005,109.686,120,0
-55.184,107.862,120
-54.405,106.02,120
-53.654,104.166,120
-52.925,102.304,120
-52.214,100.434,120
-51.518,98.56,120
-50.834,96.68,120
-50.16,94.797,120
-49.496,92.911,120
-48.841,91.021,120
-48.194,89.129,120
-47.553,87.234,120
-46.92,85.337,120
-46.293,83.438,120
-45.672,81.537,120
-45.056,79.634,120
-44.446,77.729,120
-43.841,75.823,120
-43.241,73.915,120
-42.647,72.005,120
-42.056,70.094,120
-41.471,68.182,120
-40.89,66.268,120
-40.313,64.353,120
-39.741,62.437,120
-39.174,60.519,120
-38.61,58.6,120
-38.051,56.68,120
-37.496,54.758,120
-36.915,52.728,120,0
-36.915,52.728,0,0
#PATH.JERRYIO-DATA {"appVersion":"0.8.3","format":"path.jerryio v0.1","gc":{"robotWidth":30,"robotHeight":30,"robotIsHolonomic":false,"showRobot":true,"uol":1,"pointDensity":2,"controlMagnetDistance":5,"fieldImage":{"displayName":"V5RC 2025 - High Stakes","signature":"V5RC 2025 - High Stakes","origin":{"__type":"built-in"}},"coordinateSystem":"VEX Gaming Positioning System"},"paths":[{"segments":[{"controls":[{"uid":"YAiQ8x1RS8","x":-56.00515463917526,"y":109.68556701030927,"lock":false,"visible":true,"heading":0,"__type":"end-point"},{"uid":"1Dzybna6j0","x":-51.77835051546392,"y":100.668385417191,"lock":false,"visible":true,"__type":"control"},{"uid":"n1dGuczOwY","x":-44.10090048215636,"y":77.9479081230927,"lock":false,"visible":true,"__type":"control"},{"uid":"zJR0uk1jrr","x":-36.91533347184709,"y":52.72797631414919,"lock":false,"visible":true,"heading":0,"__type":"end-point"}],"speedProfiles":[],"lookaheadKeyframes":[],"uid":"uIberXHs69"}],"pc":{"speedLimit":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":600,"label":"600"},"step":1,"from":40,"to":120},"bentRateApplicableRange":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":1,"label":"1"},"step":0.001,"from":0,"to":0.1}},"name":"Path","uid":"HWeeaR6MZT","lock":false,"visible":true}]}"""
# Split data into lines and process each line
coordinates = []
for line in data.strip().splitlines():
    # Skip lines that don't contain coordinates
    if line.startswith('#'):
        continue
    parts = line.split(',')
    # Take only the first two elements as coordinates and convert them to floats
    coordinates.append((float(parts[0]), float(parts[1])))

 

# Print or use the coordinates as needed
print(coordinates)