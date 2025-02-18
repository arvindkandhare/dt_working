# Input data as a multiline string
data = """#PATH-POINTS-START Path
156.991,-87.744,120,0
156.963,-89.744,120
156.955,-91.744,120
156.979,-93.744,120
157.062,-95.742,120
157.279,-97.729,120
157.949,-99.6,120
158.778,-101.413,120
159.228,-103.361,120
159.522,-105.339,120
159.739,-107.327,120
159.909,-109.32,120
160.048,-111.315,120
160.163,-113.312,120
160.261,-115.309,120
160.344,-117.307,120
160.416,-119.306,120
160.478,-121.305,120
160.532,-123.304,120
160.578,-125.304,120
160.618,-127.303,120
160.653,-129.303,120
160.682,-131.303,120
160.707,-133.303,120
160.728,-135.303,120
160.745,-137.303,120
160.759,-139.303,120
160.769,-141.303,120
160.777,-143.303,120
160.782,-145.303,120
160.785,-148.454,120,0
160.785,-148.454,0,0
#PATH.JERRYIO-DATA {"appVersion":"0.8.3","format":"path.jerryio v0.1","gc":{"robotWidth":30,"robotHeight":30,"robotIsHolonomic":false,"showRobot":true,"uol":1,"pointDensity":2,"controlMagnetDistance":5,"fieldImage":{"displayName":"V5RC 2025 - High Stakes (Skills)","signature":"V5RC 2025 - High Stakes (Skills)","origin":{"__type":"built-in"}},"coordinateSystem":"VEX Gaming Positioning System"},"paths":[{"segments":[{"controls":[{"uid":"3iDTTyeuiF","x":156.9910025706941,"y":-87.74421593830334,"lock":false,"visible":true,"heading":0,"__type":"end-point"},{"uid":"yctyyUOXQa","x":156.51670951156814,"y":-113.83033419023137,"lock":false,"visible":true,"__type":"control"},{"uid":"2ty0AVuRWI","x":160.78534704370182,"y":-77.30976863753213,"lock":false,"visible":true,"__type":"control"},{"uid":"N9XmGyEgrz","x":160.78534704370182,"y":-148.45372750642673,"lock":false,"visible":true,"heading":0,"__type":"end-point"}],"speedProfiles":[],"lookaheadKeyframes":[],"uid":"wDVUz3OE5d"}],"pc":{"speedLimit":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":600,"label":"600"},"step":1,"from":40,"to":120},"bentRateApplicableRange":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":1,"label":"1"},"step":0.001,"from":0,"to":0.1}},"name":"Path","uid":"HATkMGn2w5","lock":false,"visible":true}]}""" 
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