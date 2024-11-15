from PIL import Image  # For opening and processing images
import os  # For handling file paths and operations
import exifread  # For reading EXIF data from images
import piexif  # For handling EXIF data in images

def get_readable_exposure_program(program):
        # Convert numeric codes to strings, if necessary
        if program in exposure_program_mapping:
            return exposure_program_mapping[program]
        return program  # Assuming program is already a string or None

def get_image_metadata(image_path, date_folder, flight_folder, serial_number):
    try:
        # Open image file for reading (binary mode)
        with open(image_path, 'rb') as f:
            # Read EXIF data using exifread
            tags = exifread.process_file(f)

        
        # Load the image using PIL
        image = Image.open(image_path)

        # Get the EXIF data
        exif_data = image._getexif()

        # Extract desired EXIF tags
        exposure_time = str(tags.get('EXIF ExposureTime'))

        iso_speed = exif_data.get(piexif.ExifIFD.ISOSpeedRatings, "N/A")
        exposure_program = exif_data.get(piexif.ExifIFD.ExposureProgram, "N/A")
        f_number = exif_data.get(piexif.ExifIFD.FNumber, "N/A")
        exposure_bias = exif_data.get(piexif.ExifIFD.ExposureBiasValue, "N/A")
        # Handling numeric values and mapping exposure program
        exposure_program_format = get_readable_exposure_program(exposure_program)
                 

        # Formulate the metadata dictionary
        metadata = {
            "Serial No": serial_number,
            "Date folder": date_folder,
            "Flight folder": flight_folder,
            "Image": os.path.basename(image_path),
            "Exposure Time": exposure_time,            
            "ISO Speed": iso_speed,
            "Exposure Bias": exposure_bias,
            "F-Stop": f_number,
            "Exposure Program": exposure_program_format
        }
        
        #print(metadata)
        return metadata
    except Exception as e:
        print(f"Error reading EXIF data: {e}")
        return None



def set_highlight_flags(metadata, highlight_dict, drone_name, summary_dict):
    highlight = False
    
    try:
        drone_specs_for_drone = drone_specs.get(drone_name, None)
        if drone_specs_for_drone is None:
            # If the drone name is not found in the drone_specs dictionary, return
            return
            
        # Helper function to extract denominator from IFDRational object
        def get_denominator(value):
            if isinstance(value, tuple) and len(value) == 2:
                return value[1]
            return None
        
        # Convert metadata values where necessary
        exposure_time = metadata.get("Exposure Time")
        
        iso_speed = metadata.get("ISO Speed")
        exposure_bias = metadata.get("Exposure Bias")
        f_stop = metadata.get("F-Stop")
        exposure_program = metadata.get("Exposure Program")
        
        # Highlight flags initialization
        highlight_dict[metadata["Serial No"]] = False  # Default to no highlight

        # Validate against specs
        if exposure_time:
            exposure_time_denominator = get_denominator(exposure_time)
            if exposure_time_denominator is not None:
                exposure_time_denominator = int(exposure_time_denominator)
                exposure_time_value = 1 / exposure_time_denominator
                print(exposure_time_value)
                if not drone_specs_for_drone["Exposure Time"]["min"] <= exposure_time_value <= drone_specs_for_drone["Exposure Time"]["max"]:
                    highlight_dict[metadata["Serial No"]] = True
                    highlight = True
                    print(f"Error: Exposure Time {exposure_time_value} out of range for {drone_name}")

        if iso_speed and not drone_specs_for_drone["ISO Speed"]["min"] <= int(iso_speed) <= drone_specs_for_drone["ISO Speed"]["max"]:
            highlight_dict[metadata["Serial No"]] = True
            highlight = True
            #print(f"Error: ISO Speed {iso_speed} out of range for {drone_name}")

        if exposure_bias and not drone_specs_for_drone["Exposure Bias"]["min"] <= float(exposure_bias) <= drone_specs_for_drone["Exposure Bias"]["max"]:
            highlight_dict[metadata["Serial No"]] = True
            highlight = True
            print(f"Error: Exposure Bias {exposure_bias} out of range for {drone_name}")

        if f_stop and not drone_specs_for_drone["F-Stop"]["min"] <= float(f_stop) <= drone_specs_for_drone["F-Stop"]["max"]:
            highlight_dict[metadata["Serial No"]] = True
            highlight = True
            print(f"Error: F-Stop {f_stop} out of range for {drone_name}")

        # Validate exposure program against supported programs
        if exposure_program not in drone_specs_for_drone["Exposure Program"]:
            highlight_dict[metadata["Serial No"]] = True
            highlight = True
            print(f"Error: Exposure Program '{exposure_program}' not supported for {drone_name}")



    except Exception as e:
        print(f"Error setting highlight flags: {e}")
        
    finally:
        return highlight

