import os
from PIL import Image
from PIL.ExifTags import TAGS
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from tkinter import Tk, Label, Entry, Button, filedialog
from reportlab.lib import colors
import smtplib
from email.mime.text import MIMEText
import socket
import pandas as pd
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import subprocess
import json
import sys
import pyelectron
import sqlite3
import exifread
import re
import piexif
from fractions import Fraction  


def check_internet_connection():
    try:
        # Try to connect to a well-known website to check for internet connection
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False


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



def fraction_to_float(fraction_str):
    if '/' in fraction_str:
        numerator, denominator = fraction_str.split('/')
        try:
            return float(numerator) / float(denominator)
        except ZeroDivisionError:
            print("Error: Denominator cannot be zero.")
    else:
        try:
            return float(fraction_str)
        except ValueError:
            print(f"Error converting '{fraction_str}' to float.")


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



def small_summary(total_images_count,fail_count,flight_no):
    pass_images_count = total_images_count-fail_count
    fail_images_count = fail_count
    total_images_count = total_images_count
    fail_percent = (fail_images_count / total_images_count) * 100 if total_images_count > 0 else 0

    # Write summary to text file
    with open(summary_filename, 'a') as file:
        file.write(f"Flight no: {flight_no}%\n\n")
        file.write(f"Pass Images: {pass_images_count}\n")
        file.write(f"Fail Images: {fail_images_count}\n")
        file.write(f"Total image count: {total_images_count}\n")
        file.write(f"Fail Percent: {fail_percent:.2f}%\n\n")

global highlight_dict, summary_dict 

highlight_dict = {}

summary_dict = {}


def process_images(flight_no, drone_name, site_name, root_folder, name, id, serial_number):


    metadata_list = []
    data = [["Serial No", "Image", "Exposure Time", "ISO Speed", "Exposure Bias", "F-Stop", "Exposure Program"]]
    
    summary_dict = {}
    image_count = 0
    fail_count=0

    try:
        # Verify if the root_folder exists
        if not os.path.exists(root_folder):
            error_message = f"Error: The specified root folder '{root_folder}' does not exist."
            print(error_message)
            return

        for file in os.listdir(root_folder):
            if file.lower().endswith(('.jpg', '.jpeg', '.png' )):
                image_count += 1
                image_path = os.path.join(root_folder, file)
                metadata = get_image_metadata(image_path, "", "", serial_number)  # Pass empty strings for date and flight folder
                if metadata:
                    metadata_list.append(metadata)
                    data.append([metadata[key] for key in ["Serial No", "Image", "Exposure Time", "ISO Speed", "Exposure Bias", "F-Stop", "Exposure Program"]])
                    if (set_highlight_flags(metadata, highlight_dict, drone_name, summary_dict)):
                        fail_count += 1

                    #print(highlight_dict)
                    print("Fail Count : ",fail_count)
                    
                    
                    serial_number += 1

        small_summary(image_count,fail_count,flight_no)
        return metadata_list  # Return the metadata_list

    except Exception as e:
        error_message = f"Error processdsing images: {str(e)}"
        print(error_message)
        return []
    
        



def text_file(highlight_dict, name, id, drone_name, site_name, flight_no):
    # Calculate pass/fail counts and other statistics
    pass_images_count = sum(1 for v in highlight_dict.values() if not v)
    fail_images_count = sum(1 for v in highlight_dict.values() if v)
    total_images_count = len(highlight_dict)
    fail_percent = (fail_images_count / total_images_count) * 100 if total_images_count > 0 else 0

    # Get current date and time
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")  # %I for 12-hour format, %p for AM/PM indicator

    # Write summary to text file
    with open(summary_filename, 'a') as file:
        file.write(f"Total Final Summary : \n")
        file.write(f"Pass Images: {pass_images_count}\n")
        file.write(f"Fail Images: {fail_images_count}\n")
        file.write(f"Total image count: {total_images_count}\n")
        file.write(f"Fail Percent: {fail_percent:.2f}%\n\n")
        



def generate_pdf(new_file_name, metadata_list, email, highlight_dict):
    # Generate PDF using metadata from all images
    
    doc = SimpleDocTemplate(new_file_name, pagesize=letter)
    
    try:
        
        # Create table for image data
        data = [["Serial No", "Image", "Exposure Time", "ISO Speed", "Exposure Bias", "F-Stop", "Exposure Program"]]
        for metadata in metadata_list:
            data.append([metadata[key] for key in ["Serial No", "Image", "Exposure Time", "ISO Speed", "Exposure Bias", "F-Stop", "Exposure Program"]])

        table = Table(data)

        style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray), 
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Header row text color
                            ('LEFTPADDING', (0, 0), (-1, -1), 5),  # Left padding
                            ('RIGHTPADDING', (0, 0), (-1, -1), 5),  # Right padding
                            ('FONTSIZE', (0, 0), (-1, -1), 8)])  # Font size

        table.setStyle(style)

        # Iterate through highlight_dict to set row color
        for row_number_str, should_highlight in highlight_dict.items():
            row_number = int(row_number_str)   # Convert the string key to an integer index and add 1 for the header row
            if should_highlight:
                for index in range(len(data[0])):  # Loop through each column
                    table.setStyle(TableStyle([('BACKGROUND', (index, row_number), (index, row_number), colors.red)]))

        # Build the PDF with pass/fail counts and image data table
        content = []  # Define the content variable
        doc.build(content + [table])    
        
    except Exception as e:
        print("This is an error of generate_pdf function:", e)



def send_email_with_attachment(subject, body, recipients, cc_recipients, attachment_path):
    server = None  # Initialize server variable with None
    try:
        # Create a multipart message
        msg = MIMEMultipart()
        msg['From'] = 'extrashaikh786@gmail.com'  # Replace with your email address
        msg['To'] = ", ".join(recipients)
        msg['Cc'] = ", ".join(cc_recipients)
        msg['Subject'] = subject

        # Add body to the email
        msg.attach(MIMEText(body, 'plain'))

        # Attach the file
        with open(attachment_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= {attachment_path}')

        msg.attach(part)

        # Connect to SMTP server (for example, Gmail's SMTP server)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)  # Change to your SMTP server
            #server.set_debuglevel(1)  # Enable debugging
            server.starttls()
            # Login to your email account
            try:
                server.login('extrashaikh786@gmail.com', 'rxjvxznjewruuxbf')  # Replace with your email and password
            except smtplib.SMTPAuthenticationError:
                print("Authentication failed. Check your email and password.")
                return
            # Send email
            recipients_with_cc = recipients + cc_recipients
            try:
                server.sendmail('extrashaikh786@gmail.com', recipients_with_cc, msg.as_string())
                print("\033[92mEmail sent successfully to {}\033[0m with \033[92mCC to {}\033[0m".format(", ".join(recipients), ", ".join(cc_recipients)))
                print("\033[92mProgram has been successfully ran, Congratulations\033[0m")
                os.remove(attachment_path)
                
            except Exception as send_error:
                print("An error occurred while sending email:", send_error)
                return
        except smtplib.SMTPConnectError as smtp_connect_error:
            print("Failed to connect to SMTP server:", smtp_connect_error)
            return
        except Exception as server_error:
            print("An error occurred while connecting to SMTP server:", server_error)
            return
        finally:
            if server is not None:
                server.quit()  # Check if server is not None before calling quit()
    except Exception as e:
        print("An unexpected error occurred:", e)



def convert_to_forward_slashes(path):
    # Replace backslashes with forward slashes
    return path.replace('\\', '/')

def main():


    if len(sys.argv) != 7:
        print("Usage: python script_name.py flight_no drone_name site_name name id email new_file_name root_folders_input")
        sys.exit(1)

    flight_no = "F1"
    drone_name = sys.argv[1]
    site_name = sys.argv[2]
    name = sys.argv[3]
    id = sys.argv[4]
    email = sys.argv[5]
    root_folders_input = sys.argv[6]
    
    collection_of_root_folders = root_folders_input.split(',')
    metadata_list = []  # List to store metadata for all images
    new_file_name = "output.pdf"
    serial_number = 1  # Initialize serial number outside the loop
    
    global summary_filename
    summary_filename = f"{name}_Images summary.txt"

    for root_folder in collection_of_root_folders:
        # Process images
        metadata_list.extend(process_images(flight_no, drone_name, site_name, root_folder, name, id, serial_number))
        # Increment serial number for next set of images
        serial_number += len(metadata_list)
         # Increment flight number for the next iteration
        flight_no = "F" + str(int(flight_no[1:]) + 1)
        print(flight_no)
        
        
    
    # After processing all images, generate PDF with all metadata
    generate_pdf(new_file_name,metadata_list,email, highlight_dict)
    #print(highlight_dict)
    text_file(highlight_dict, name, id, drone_name, site_name, flight_no)

    # Get current date and time
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")  # %I for 12-hour format, %p for AM/PM indicator

    # Ensure internet connection before attempting to send an email
    if check_internet_connection():

        # Email subject and body
        email_subject = f"Image Processing Summary by {name}"
        email_body = f"Date: {current_date}\nTime: {current_time}\nName: {name}\nID: {id}\nDrone Name : {drone_name}\nSite Name: {site_name}\n"

        # Function call to send an email with the PDF attachment
        send_email_with_attachment(email_subject, email_body, [email], ['shaikhfahad687@gmail.com', 'shaikhfahad687@gmail.com', 'shaikhfahad687@gmail.com'], summary_filename)


if __name__ == "__main__":
    main()