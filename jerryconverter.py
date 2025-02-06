# Input data as a multiline string
data = """#PATH-POINTS-START Path
-163.631,152.248,120,0
-161.632,152.291,120
-159.632,152.332,120
-157.632,152.373,120
-155.633,152.413,120
-153.633,152.451,120
-151.634,152.488,120
-149.634,152.523,120
-147.634,152.557,120
-145.634,152.588,120
-143.635,152.616,120
-141.635,152.641,120
-139.635,152.662,120
-137.635,152.677,120
-135.635,152.687,120
-133.635,152.69,120
-131.635,152.685,120
-129.635,152.673,120
-127.635,152.655,120
-125.635,152.636,120
-123.635,152.617,120
-121.635,152.602,120
-119.635,152.59,120
-117.635,152.584,120
-115.635,152.581,120
-113.635,152.581,120
-111.635,152.585,120
-109.635,152.592,120
-107.635,152.601,120
-105.635,152.613,120
-103.635,152.626,120
-101.635,152.641,120
-99.636,152.658,120
-97.636,152.676,120
-95.636,152.695,120
-92.961,152.722,120,0
-92.961,152.722,0,0
#PATH.JERRYIO-DATA {"appVersion":"0.8.3","format":"path.jerryio v0.1","gc":{"robotWidth":18,"robotHeight":18,"robotIsHolonomic":false,"showRobot":true,"uol":2.54,"pointDensity":0.7874015748031495,"controlMagnetDistance":1.968503937007874,"fieldImage":{"displayName":"V5RC 2025 - High Stakes","signature":"V5RC 2025 - High Stakes","origin":{"__type":"built-in"}},"coordinateSystem":"VEX Gaming Positioning System"},"paths":[{"segments":[{"controls":[{"uid":"S4RBHOXvDi","x":-64.42169503876282,"y":59.940185818674976,"lock":false,"visible":true,"heading":0,"__type":"end-point"},{"uid":"q2CbNQSFHu","x":-47.055846810922404,"y":60.31364492034897,"lock":false,"visible":true,"__type":"control"},{"uid":"sBLIaqB4pa","x":-54.15156974272817,"y":59.940185818674976,"lock":false,"visible":true,"__type":"control"},{"uid":"o4NjkXRcwz","x":-36.59899196405077,"y":60.12691536951197,"lock":false,"visible":true,"heading":0,"__type":"end-point"}],"speedProfiles":[],"lookaheadKeyframes":[],"uid":"kzJOyvZM1j"}],"pc":{"speedLimit":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":600,"label":"600"},"step":1,"from":40,"to":120},"bentRateApplicableRange":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":1,"label":"1"},"step":0.001,"from":0,"to":0.1}},"name":"Path","uid":"u6QrL3Tg8M","lock":false,"visible":true}]}"""
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