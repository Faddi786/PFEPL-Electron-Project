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
        self.set_font('Arial', '', 12)
        if col_widths is None:
            col_widths = [40] * len(data_dict)

        for key, value in data_dict.items():
            self.cell(col_widths[0], 10, key, 1)
            self.cell(col_widths[1], 10, str(value), 1)
            self.ln()

    def add_dataframe_table(self, df):
        self.set_font('Arial', '', 10)
        col_widths = [30] * len(df.columns)
        for col in df.columns:
            self.cell(col_widths[0], 10, col, 1)
        self.ln()

        for index, row in df.iterrows():
            for item in row:
                self.cell(col_widths[0], 10, str(item), 1)
            self.ln()
        self.ln(4)

def user_pdf(pdf_data):
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
        
        # User DataFrame Table
        user_df = folder_data.get("user_df", pd.DataFrame())
        if not user_df.empty:
            pdf.chapter_title('User Data')
            pdf.add_dataframe_table(user_df)
            pdf.ln(10)
            
        # Manager DataFrame Table
        man_df = folder_data.get("man_df", pd.DataFrame())
        if not man_df.empty:
            pdf.chapter_title('Manager Data')
            pdf.add_dataframe_table(man_df)
            pdf.ln(10)
    
    # Output PDF
    pdf.output('report.pdf')

