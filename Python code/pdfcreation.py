from fpdf import FPDF
import pandas as pd

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)

    def add_table(self, data_dict, col_widths=None):
        self.set_font('Arial', '', 10)
        if col_widths is None:
            col_widths = [40, 140]  # Increase the default column widths here

        for key, value in data_dict.items():
            self.cell(col_widths[0], 10, key, 1)
            self.cell(col_widths[1], 10, str(value), 1)
            self.ln()



    def add_dataframe_table(self, df):
        self.set_font('Arial', '', 8)

        # Manually set the column widths for each of the 7 columns
        col_widths = [15, 30, 22, 22, 28, 17, 15, 28]  # Example widths for each column

        # Adding headers
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 6, col, 1)
        self.ln()

        # Adding data
        for index, row in df.iterrows():
            failing_factor = row.get('Failing Factor', False)  # Get the Failing Factor value
            if failing_factor:
                self.set_fill_color(255, 0, 0)  # Set fill color to red
                fill = True
            else:
                self.set_fill_color(255, 255, 255)  # Set fill color to white (optional)
                fill = False

            for i, col in enumerate(df.columns):
                item = row.get(col, '')  # Get the value or an empty string if not present
                if col == 'Failing Factor' and not failing_factor:
                    item = ''  # Skip the value if failing factor is False
                self.cell(col_widths[i], 6, str(item), 1, fill=fill)
            self.ln()

        self.ln(4)

    def add_man_df_table(self, df):
        self.set_font('Arial', '', 8)

        # Define the column widths, excluding the last three columns
        col_widths = [27, 25, 22, 22, 28, 17]  # Example widths for the first 6 columns

        # Adding headers, excluding the last three columns
        headers = df.columns[:-3]
        for i, col in enumerate(headers):
            self.cell(col_widths[i], 6, col, 1)
        self.ln()

        # Adding data, excluding the last three columns
        for index, row in df.iterrows():
            for i, col in enumerate(headers):
                item = row.get(col, '')  # Get the value or an empty string if not present
                self.cell(col_widths[i], 6, str(item), 1)
            self.ln()

        self.ln(4)

    def configuration_details(self, df, col_widths=None):
        self.set_font('Arial', '', 10)
        col_widths = [40, 45, 35]  # Default column widths for three columns
        
        # Add the table headers (first row of the DataFrame)
        headers = df.columns.tolist()
        for i, header in enumerate(headers):
            self.cell(col_widths[i], 10, header, 1)
        self.ln()

        # Add the table rows (remaining rows of the DataFrame)
        for index, row in df.iterrows():
            for i, item in enumerate(row):
                self.cell(col_widths[i], 10, str(item), 1)
            self.ln()



        
def user_pdf(pdf_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # General Page Data
    gen_page_data = pdf_data.get("Gen Page Data", {})
    totalsum_dict = gen_page_data.get("totalsum_dict", {})
    processdetails_dict = gen_page_data.get("processdetails_dict", {})
    configuration_details_df = gen_page_data.get("configuration_details", pd.DataFrame())

    pdf.chapter_title('General Page Data')
    pdf.chapter_title('Total Summary')
    pdf.add_table(totalsum_dict)
    pdf.ln(10)
    
    pdf.chapter_title('Process Details')
    pdf.add_table(processdetails_dict)
    pdf.ln(10)

    pdf.chapter_title('Drone Configurations')
    pdf.configuration_details(configuration_details_df)
    pdf.ln(10)


    # All Folders Data
    all_folders_data = pdf_data.get("All folders data", {})
    for folder_name, folder_data in all_folders_data.items():
        pdf.add_page()
        pdf.chapter_title(folder_name)
        
        # Summary Table
        summary_dict = folder_data.get("summary_dict", {})
        pdf.chapter_title('Summary')
        pdf.add_table(summary_dict)
        pdf.ln(10)
        
        # User DataFrame Table
        user_df = folder_data.get("user_df", pd.DataFrame())
        if not user_df.empty:
            pdf.chapter_title('User Data')
            pdf.add_dataframe_table(user_df)
            pdf.ln(10)
            
        # # Manager DataFrame Table
        # man_df = folder_data.get("man_df", pd.DataFrame())
        # if not man_df.empty:
        #     pdf.chapter_title('Manager Data')
        #     pdf.add_dataframe_table(man_df)
        #     pdf.ln(10)
    
    # Output PDF
    pdf.output('user_pdf.pdf')

def man_pdf(pdf_data):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # General Page Data
    gen_page_data = pdf_data.get("Gen Page Data", {})
    totalsum_dict = gen_page_data.get("totalsum_dict", {})
    processdetails_dict = gen_page_data.get("processdetails_dict", {})

    pdf.chapter_title('General Page Data')
    pdf.chapter_title('Total Summary')
    pdf.add_table(totalsum_dict)
    pdf.ln(10)
    
    pdf.chapter_title('Process Details')
    pdf.add_table(processdetails_dict)
    pdf.ln(10)

    # All Folders Data
    all_folders_data = pdf_data.get("All folders data", {})
    for folder_name, folder_data in all_folders_data.items():
        pdf.add_page()
        pdf.chapter_title(folder_name)
        
        # Summary Table
        summary_dict = folder_data.get("summary_dict", {})
        pdf.chapter_title('Summary')
        pdf.add_table(summary_dict)
        pdf.ln(10)
        
        # # User DataFrame Table
        # user_df = folder_data.get("user_df", pd.DataFrame())
        # if not user_df.empty:
        #     pdf.chapter_title('User Data')
        #     pdf.add_dataframe_table(user_df)
        #     pdf.ln(10)
            
        # Manager DataFrame Table
        man_df = folder_data.get("man_df", pd.DataFrame())
        if not man_df.empty:
            pdf.chapter_title('Manager Data')
            pdf.add_man_df_table(man_df)
            pdf.ln(10)
    
    # Output PDF
    pdf.output('man_pdf.pdf')

