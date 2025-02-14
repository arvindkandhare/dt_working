# Input data as a multiline string
data = """#PATH-POINTS-START Path
-153.64,159.243,120,315
-138.42,158.797,120
-123.401,156.256,120
-108.753,152.083,120
-94.615,146.427,120
-81.225,139.181,120
-69.076,130.011,120
-59.156,118.226,120,0
-59.156,118.226,0,0
#PATH.JERRYIO-DATA {"appVersion":"0.8.3","format":"path.jerryio v0.1","gc":{"robotWidth":18,"robotHeight":18,"robotIsHolonomic":false,"showRobot":true,"uol":2.54,"pointDensity":6,"controlMagnetDistance":1.968503937007874,"fieldImage":{"displayName":"V5RC 2025 - High Stakes","signature":"V5RC 2025 - High Stakes","origin":{"__type":"built-in"}},"coordinateSystem":"VEX Gaming Positioning System"},"paths":[{"segments":[{"controls":[{"uid":"mezLrbLC4F","x":-60.488,"y":62.694,"lock":false,"visible":true,"heading":315,"__type":"end-point"},{"uid":"d8FTV1MJlU","x":-48.506040250811715,"y":63.421647627936316,"lock":false,"visible":true,"__type":"control"},{"uid":"hyz60WRyBC","x":-29.588684552995147,"y":56.87333219407674,"lock":false,"visible":true,"__type":"control"},{"uid":"r8jyCCnZnI","x":-23.289925613116882,"y":46.54581821267344,"lock":false,"visible":true,"heading":0,"__type":"end-point"}],"speedProfiles":[],"lookaheadKeyframes":[],"uid":"B0kX7FPQ7z"}],"pc":{"speedLimit":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":600,"label":"600"},"step":1,"from":40,"to":120},"bentRateApplicableRange":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":1,"label":"1"},"step":0.001,"from":0,"to":0.1}},"name":"Path","uid":"xQ7Elwl6qZ","lock":false,"visible":true}]}"""
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