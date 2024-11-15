# Define drone specifications using a multi-level dictionary
global drone_specs
drone_specs = {
    "Talon": {
        "Exposure Time": {"min": 800, "max": 2000},
        "ISO Speed": {"min": 50, "max": 600},
        "Exposure Bias": {"min": -1, "max": 0},
        "F-Stop": {"min": 2.8, "max": 9},
        "Exposure Program": ["Manual", "Shutter Priority"]
    },
    "Impulse": {
        "Exposure Time": {"min": 800, "max": 1600},
        "ISO Speed": {"min": 50, "max": 600},
        "Exposure Bias": {"min": -1, "max": 0},
        "F-Stop": {"min": 2.8, "max": 9},
        "Exposure Program": ["Manual", "Shutter Priority"]

    }
}

global exposure_program_mapping   
exposure_program_mapping = {
    0: "Not Defined",
    1: "Manual",
    2: "Program AE",
    3: "Aperture Priority",
    4: "Shutter Priority",
    5: "Creative (Slow speed)",
    6: "Action (High speed)",
    7: "Portrait",
    8: "Landscape",
    9: "Bulb"
}
