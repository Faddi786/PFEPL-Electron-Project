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

from code import details, extras, mail, man_pdf, processing

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
                metadata = processing.get_image_metadata(image_path, "", "", serial_number)  # Pass empty strings for date and flight folder
                if metadata:
                    metadata_list.append(metadata)
                    data.append([metadata[key] for key in ["Serial No", "Image", "Exposure Time", "ISO Speed", "Exposure Bias", "F-Stop", "Exposure Program"]])
                    if (processing.set_highlight_flags(metadata, highlight_dict, drone_name, summary_dict)):
                        fail_count += 1

                    #print(highlight_dict)
                    print("Fail Count : ",fail_count)
                    
                    serial_number += 1

        man_pdf.small_summary(image_count,fail_count,flight_no)
        return metadata_list  # Return the metadata_list

    except Exception as e:
        error_message = f"Error processdsing images: {str(e)}"
        print(error_message)
        return []
    
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