import json

def create_jerryio_file(points, output_file):
    # Define the metadata
    metadata = {
        "appVersion": "0.8.3",
        "format": "path.jerryio v0.1",
        "gc": {
            "robotWidth": 18,
            "robotHeight": 18,
            "robotIsHolonomic": False,
            "showRobot": False,
            "uol": 1,
            "pointDensity": 2,
            "controlMagnetDistance": 1.968503937007874,
            "fieldImage": {
                "displayName": "V5RC 2025 - High Stakes (Skills)",
                "signature": "V5RC 2025 - High Stakes (Skills)",
                "origin": {
                    "__type": "built-in"
                }
            },
            "coordinateSystem": "VEX Gaming Positioning System"
        },
        "paths": [
            {
                "segments": [
                    {
                        "controls": [
                            {
                                "uid": "mezLrbLC4F",
                                "x": points[0][0],
                                "y": points[0][1],
                                "lock": False,
                                "visible": True,
                                "heading": points[0][3] if len(points[0]) > 3 else 0,
                                "__type": "end-point"
                            },
                            {
                                "uid": "r8jyCCnZnI",
                                "x": points[-1][0],
                                "y": points[-1][1],
                                "lock": False,
                                "visible": True,
                                "heading": points[-1][3] if len(points[-1]) > 3 else 0,
                                "__type": "end-point"
                            }
                        ],
                        "speedProfiles": [],
                        "lookaheadKeyframes": [],
                        "uid": "B0kX7FPQ7z"
                    }
                ],
                "pc": {
                    "speedLimit": {
                        "minLimit": {
                            "value": 0,
                            "label": "0"
                        },
                        "maxLimit": {
                            "value": 600,
                            "label": "600"
                        },
                        "step": 1,
                        "from": 40,
                        "to": 120
                    },
                    "bentRateApplicableRange": {
                        "minLimit": {
                            "value": 0,
                            "label": "0"
                        },
                        "maxLimit": {
                            "value": 1,
                            "label": "1"
                        },
                        "step": 0.001,
                        "from": 0,
                        "to": 0.1
                    }
                },
                "name": "Path",
                "uid": "xQ7Elwl6qZ",
                "lock": False,
                "visible": True
            }
        ]
    }

    # Write the points and metadata to the output file
    with open(output_file, 'w') as f:
        f.write("#PATH-POINTS-START Path\n")
        for point in points:
            f.write(','.join(map(str, point)) + '\n')
        f.write("#PATH.JERRYIO-DATA " + json.dumps(metadata) + '\n')

# Example usage
points = [(88.148, 100.166), (86.801, 98.687), (85.459, 97.205), (84.12, 95.719), (82.785, 94.23), (81.454, 92.737), (80.127, 91.241), (78.802, 89.742), (77.481, 88.241), (76.163, 86.737), (74.847, 85.23), (73.534, 83.722), (72.224, 82.211), (70.916, 80.698), (69.61, 79.183), (68.307, 77.666), (67.005, 76.148), (65.705, 74.628), (64.406, 73.107), (63.11, 71.584), (61.814, 70.06), (60.52, 68.535), (59.227, 67.009), (57.936, 65.483), (56.645, 63.955), (55.355, 62.427), (54.065, 60.898), (52.777, 59.368), (51.489, 57.838), (50.201, 56.308), (48.914, 54.777), (47.626, 53.247), (46.339, 51.716), (45.052, 50.185), (43.765, 48.654), (42.478, 47.123), (41.19, 45.593), (39.902, 44.063), (38.614, 42.533), (37.325, 41.004), (36.035, 39.476), (34.744, 37.948), (33.453, 36.421), (32.161, 34.894), (30.867, 33.369), (29.572, 31.844), (28.276, 30.321), (26.979, 28.799), (25.68, 27.278), (24.379, 25.759), (23.077, 24.241), (21.773, 22.724), (20.467, 21.21), (19.159, 19.697), (17.849, 18.186), (16.537, 16.676), (15.222, 15.169), (13.905, 13.664), (12.585, 12.162), (11.262, 10.662), (9.937, 9.164), (8.537, 7.589), (8.537, 7.589)]

create_jerryio_file(points, 'trial.jerryio.txt')