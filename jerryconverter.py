# Input data as a multiline string
data = """#PATH-POINTS-START Path
-171.42,159.243,120,0
-169.42,159.268,120
-167.42,159.293,120
-165.42,159.318,120
-163.42,159.342,120
-161.42,159.365,120
-159.42,159.387,120
-157.42,159.408,120
-155.421,159.428,120
-153.421,159.446,120
-151.421,159.463,120
-149.421,159.479,120
-147.421,159.492,120
-145.421,159.503,120
-143.421,159.511,120
-141.421,159.516,120
-139.421,159.516,120
-137.421,159.513,120
-135.421,159.505,120
-133.421,159.493,120
-131.421,159.476,120
-129.421,159.455,120
-127.421,159.433,120
-125.421,159.41,120
-123.422,159.387,120
-121.422,159.366,120
-119.422,159.346,120
-117.422,159.329,120
-115.422,159.313,120
-113.422,159.299,120
-111.422,159.287,120
-109.422,159.277,120
-107.422,159.269,120
-105.422,159.261,120
-103.422,159.256,120
-101.422,159.251,120
-99.422,159.247,120
-97.422,159.245,120
-95.422,159.243,120
-92.961,159.243,120,0
-92.961,159.243,0,0
#PATH.JERRYIO-DATA {"appVersion":"0.8.3","format":"path.jerryio v0.1","gc":{"robotWidth":18,"robotHeight":18,"robotIsHolonomic":false,"showRobot":true,"uol":2.54,"pointDensity":0.7874015748031495,"controlMagnetDistance":1.968503937007874,"fieldImage":{"displayName":"V5RC 2025 - High Stakes","signature":"V5RC 2025 - High Stakes","origin":{"__type":"built-in"}},"coordinateSystem":"VEX Gaming Positioning System"},"paths":[{"segments":[{"controls":[{"uid":"S4RBHOXvDi","x":-67.488,"y":62.694,"lock":false,"visible":true,"heading":0,"__type":"end-point"},{"uid":"q2CbNQSFHu","x":-48.74857045206578,"y":62.9365872254282,"lock":false,"visible":true,"__type":"control"},{"uid":"sBLIaqB4pa","x":-54.32676508090912,"y":62.69405702417414,"lock":false,"visible":true,"__type":"control"},{"uid":"o4NjkXRcwz","x":-36.599,"y":62.694,"lock":false,"visible":true,"heading":0,"__type":"end-point"}],"speedProfiles":[],"lookaheadKeyframes":[],"uid":"kzJOyvZM1j"}],"pc":{"speedLimit":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":600,"label":"600"},"step":1,"from":40,"to":120},"bentRateApplicableRange":{"minLimit":{"value":0,"label":"0"},"maxLimit":{"value":1,"label":"1"},"step":0.001,"from":0,"to":0.1}},"name":"Path","uid":"u6QrL3Tg8M","lock":false,"visible":true}]}"""
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