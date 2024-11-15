import os
import exifread
from PIL import Image
import piexif
import pandas as pd
import random
import numpy as np
import datetime


import pdfcreation

# Initialize global totals
total_pass = 0
total_fail = 0
total_count = 0


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


# Exposure Program mapping
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

def get_readable_exposure_program(program):
    if program in exposure_program_mapping:
        return exposure_program_mapping[program]
    return program  # Assuming program is already a string or None

def match_values(user_df, man_df, drone_name):
    global drone_specs
    drone_specs_for_drone = drone_specs.get(drone_name, None)
    if drone_specs_for_drone is None:
        return user_df, man_df
    
    # Extract expected ranges from drone specifications
    exposuretime_min = drone_specs_for_drone["Exposure Time"]["min"]
    exposuretime_max = drone_specs_for_drone["Exposure Time"]["max"]

    exposurebias_min = drone_specs_for_drone["Exposure Bias"]["min"]
    exposurebias_max = drone_specs_for_drone["Exposure Bias"]["max"]
    
    exposureprogram_list = drone_specs_for_drone["Exposure Program"]

    isospeed_min = drone_specs_for_drone["ISO Speed"]["min"]
    isospeed_max = drone_specs_for_drone["ISO Speed"]["max"]

    fstop_min = drone_specs_for_drone["F-Stop"]["min"]
    fstop_max = drone_specs_for_drone["F-Stop"]["max"]

    def get_denominator(value):
        if isinstance(value, tuple) and len(value) == 2:
            return value[1]
        return None


    # Iterate through each row to check for failing factors
    for _, row in user_df.iterrows():
        exposure_time = row['Exposure Time']
        iso_speed = row['ISO Speed']
        exposure_bias = row['Exposure Bias']
        f_stop = row['F-stop']
        exposure_program = row['Exposure Program']
        image_name = row['Image Name']

        failing_factors = []
        criteriaforfailure = []
        expectedvalue = []
        actualvalue = []

        # Validate Exposure Time
        if exposure_time:
            exposure_time_denominator = get_denominator(exposure_time)
            if exposure_time_denominator is not None:
                exposure_time_value = 1 / exposure_time_denominator
                if not (exposuretime_min <= exposure_time_value <= exposuretime_max):
                    failing_factors.append(f"Exposure Time")
                    criteriaforfailure.append("Exposure Time")
                    expectedvalue.append(f"{exposuretime_min}-{exposuretime_max}")
                    actualvalue.append(f"{exposure_time_value}")

        # Validate ISO Speed
        if iso_speed:
            try:
                iso_speed_value = int(iso_speed)
                if not (isospeed_min <= iso_speed_value <= isospeed_max):
                    failing_factors.append(f"ISO Speed")
                    criteriaforfailure.append("ISO Speed")
                    expectedvalue.append(f"{isospeed_min}-{isospeed_max}")
                    actualvalue.append(f"{iso_speed_value}")
            except ValueError:
                # If ISO Speed is not a valid integer, mark as failing
                failing_factors.append(f"ISO Speed")
                criteriaforfailure.append("ISO Speed")
                expectedvalue.append(f"{isospeed_min}-{isospeed_max}")
                actualvalue.append("Invalid ISO Speed")

        # Validate Exposure Bias
        if exposure_bias and not (exposurebias_min <= float(exposure_bias) <= exposurebias_max):
            failing_factors.append(f"Exposure Bias")
            criteriaforfailure.append("Exposure Bias")
            expectedvalue.append(f"{exposurebias_min}-{exposurebias_max}")
            actualvalue.append(f"{exposure_bias}")

        # Validate F-stop
        if f_stop and not (fstop_min <= float(f_stop) <= fstop_max):
            failing_factors.append(f"F-stop")
            criteriaforfailure.append("F-stop")
            expectedvalue.append(f"{fstop_min}-{fstop_max}")
            actualvalue.append(f"{f_stop}")

        # Validate Exposure Program
        if exposure_program not in exposureprogram_list:
            failing_factors.append(f"Exposure Program")
            criteriaforfailure.append("Exposure Program")
            expectedvalue.append(f"{', '.join(exposureprogram_list)}")
            actualvalue.append(f"{exposure_program}")

        # Update the 'Failing Factor' column
        user_df.at[row.name, 'Failing Factor'] = ", ".join(failing_factors) if failing_factors else False

        # If there are failing factors, update man_df
        if failing_factors:
            # Find the first row in man_df with a hyphen in "Fail Image" column
            for man_idx in man_df.index:
                if '-' in man_df.at[man_idx, 'Fail Image']:
                    man_df.at[man_idx, 'Criteria for Failure'] = ", ".join(criteriaforfailure)
                    man_df.at[man_idx, 'Expected Value'] = ", ".join(expectedvalue)
                    man_df.at[man_idx, 'Actual Value'] = ", ".join(actualvalue)
                    man_df.at[man_idx, 'Fail Image'] = image_name
                    break  # Exit the loop after updating one row

    return user_df, man_df





def update_mandf_pass_column(df, folder_path):
    # Check if the provided folder path is valid
    if not folder_path or not os.path.isdir(folder_path):
        raise ValueError(f"Invalid folder path: '{folder_path}'")
    
    # Get the list of image files from the folder
    all_images = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    #print("These are all images in the folder:", all_images)
    
    # Get the list of images already in the "Fail Image" column
    fail_images = df['Fail Image'].dropna().unique()
    #print("These are fail images in the DataFrame:", fail_images)

    # Filter out the images that are already in the "Fail Image" column
    available_images = [img for img in all_images if img not in fail_images]
    #print("These are available images:", available_images)
    
    # Randomly select up to 5 image names from the available images
    num_images_to_select = min(5, len(available_images))
    selected_images = random.sample(available_images, num_images_to_select) if num_images_to_select > 0 else []
    #print("Selected images:", selected_images)
    
    #print("this is the man df", df)
    # Update the DataFrame
    df['Pass Image'] = selected_images

    df['Folder Path'] = folder_path
    
    return df


def update_summary(user_df, folder_path):
    global total_pass, total_fail, total_count
    
    # Extract values
    count = len(user_df)
    fail = (user_df['Failing Factor'] != False).sum()

    pass_ = count - fail
    fail_percentage = round((fail / count) * 100, 2) if count > 0 else 0

    # Update the dictionary
    summary_dict = {
        "Pass": pass_,
        "Fail": fail,
        "Fail Percentage": fail_percentage,
        "Count": count,
        "Folder Path" : folder_path
    }

    # Update global totals
    total_pass += pass_
    total_fail += fail
    total_count += count

    return summary_dict



def process_folder(folder_path, folder_idx, drone_name):
    # Initialize folder-specific data structures
    
    # Create the folder-specific dataframes
    user_df = pd.DataFrame(columns=['Serial', 'Image Name', 'Exposure Time', 'Exposure Bias', 
                                    'Exposure Program', 'ISO Speed', 'F-stop', 'Failing Factor'])
    # Define the columns
    columns = ['Criteria for Failure', 'Expected Value', 'Actual Value', 'Fail Image', 'Folder Path']

    # Create the DataFrame with 5 rows of default values ('-')
    man_df = pd.DataFrame({col: ['-'] * 5 for col in columns})

    # Process the folder
    for idx, image_name in enumerate(os.listdir(folder_path)):
        image_path = os.path.join(folder_path, image_name)

        # Extract metadata from image
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

        image = Image.open(image_path)
        exif_data = image._getexif()

        # Extract desired EXIF tags
        exposure_time = str(tags.get('EXIF ExposureTime', "N/A"))
        iso_speed = exif_data.get(piexif.ExifIFD.ISOSpeedRatings, "N/A")
        exposure_program = exif_data.get(piexif.ExifIFD.ExposureProgram, "N/A")
        f_number = exif_data.get(piexif.ExifIFD.FNumber, "N/A")
        exposure_bias = exif_data.get(piexif.ExifIFD.ExposureBiasValue, "N/A")

        exposure_program_format = get_readable_exposure_program(exposure_program)

        # Append the data to user_df
        user_df = user_df._append({
            'Serial': idx + 1,
            'Image Name': image_name,
            'Exposure Time': exposure_time,
            'Exposure Bias': exposure_bias,
            'Exposure Program': exposure_program_format,
            'ISO Speed': iso_speed,
            'F-stop': f_number,
            'Failing Factor': False  # Default to False, will be updated later
        }, ignore_index=True)

    # Match values against predefined drone specs
    user_df, man_df = match_values(user_df, man_df, drone_name)

    man_df = update_mandf_pass_column(man_df,folder_path)

    # Replace all NaN values with hyphen in the entire DataFrame
    user_df.fillna("-", inplace=True)
    #print(user_df)
    # Replace all NaN values with hyphen in the entire DataFrame
    man_df.fillna("-", inplace=True)

    # Assuming user_df is already defined and contains the necessary data
    summary_dict = update_summary(user_df, folder_path)

    # Create a dictionary for the folder
    folder_data = {
        "summary_dict": summary_dict,
        "user_df": user_df,
        "man_df": man_df
    }

    return folder_data

def main(folder_paths, drone_name):
    # Initialize the dictionary of all folders
    all_folders_data = {}

    # Loop over each folder path in the list
    for folder_idx, folder_path in enumerate(folder_paths, start=1):
        folder_data = process_folder(folder_path, folder_idx, drone_name)
        folder_name = f"folder_{folder_idx}"
        all_folders_data[folder_name] = folder_data

    return all_folders_data

def totalsum_processdetails(total_pass, total_fail, total_count, total_failpercentage, pilot_name, drone_name, site_name, total_flightcount):
    # Get current timestamp
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Create the first dictionary
    dict1 = {
        "Pilot Name": pilot_name,
        "Timestamp": timestamp,
        "Drone Name": drone_name,
        "Site Name": site_name,
        "Flight Count": total_flightcount
    }
    
    # Create the second dictionary
    dict2 = {
        "Total Pass": total_pass,
        "Total Fail": total_fail,
        "Total Image Count": total_count,
        "Total Fail Percentage": total_failpercentage
    }
    
    return dict1, dict2


# Function to print the nested data structure
def print_structure(d, indent=0):
    for key, value in d.items():
        print('    ' * indent + str(key) + ":")
        if isinstance(value, dict):
            print_structure(value, indent + 1)
        elif isinstance(value, pd.DataFrame):
            print('    ' * (indent + 1) + value.to_string().replace('\n', '\n' + '    ' * (indent + 1)))
        else:
            print('    ' * (indent + 1) + str(value))


def configuration_details_function(drone_name):
    # Access the global drone_specs dictionary
    global drone_specs
    
    # Check if the drone name exists in the dictionary
    if drone_name not in drone_specs:
        raise ValueError(f"Drone name '{drone_name}' not found in the specifications.")
    
    # Extract the specifications for the given drone
    specs = drone_specs[drone_name]
    
    # Prepare data for the DataFrame
    data = []
    for factor, values in specs.items():
        if isinstance(values, dict):  # For factors with min and max values
            min_value = values.get('min')
            max_value = values.get('max')
        else:  # For factors like 'Exposure Program' with a list of values
            min_value = ", ".join(values)
            max_value = ""
        
        data.append([factor, min_value, max_value])
    
    # Create the DataFrame
    df = pd.DataFrame(data, columns=['Factor', 'Min', 'Max'])
    
    return df



if __name__ == "__main__":

    # Example folder paths (replace with actual paths)
    folder_paths = [
        r"C:\Users\Fahad\Desktop\Current Software\Electron\Images\Talon",
        r"C:\Users\Fahad\Desktop\Current Software\Electron\Images\Striver"
    ]

    # Example usage:
    Pilotname = "John Doe"
    Dronename = "Talon"
    Sitename = "Site A"
    total_flightcount = len(folder_paths)

    # Call the main function
    all_folders_data = main(folder_paths, Dronename)
    total_failpercentage = round((total_fail / total_count) * 100, 2) if total_count > 0 else 0

    processdetails_dict, totalsum_dict = totalsum_processdetails(total_pass, total_fail, total_count, total_failpercentage, Pilotname, Dronename, Sitename, total_flightcount)

    configuration_details = configuration_details_function(Dronename)
    gen_page_data = {
        "totalsum_dict": totalsum_dict,
        "processdetails_dict": processdetails_dict,
        "configuration_details" : configuration_details
    }

    #print(gen_page_data)

    pdf_data = {
    "Gen Page Data":gen_page_data,
    "All folders data":all_folders_data
    }


print("pdfdata:")
print_structure(pdf_data)

pdfcreation.user_pdf(pdf_data)
pdfcreation.man_pdf(pdf_data)