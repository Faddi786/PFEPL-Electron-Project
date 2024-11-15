from reportlab.lib.pagesizes import letter  # For setting the PDF page size
from reportlab.platypus import SimpleDocTemplate, Table  # For creating the PDF document and table
from reportlab.lib import colors  # For setting colors in the table
from reportlab.platypus import TableStyle  # For styling the table
import os  # For checking and removing files
import datetime  # For getting the current date and time

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

