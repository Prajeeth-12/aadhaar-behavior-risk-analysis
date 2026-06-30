from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        # Logo
        # self.image('assets/logo.png', 10, 8, 33) 
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'UIDAI Migration Analysis Report', 0, 0, 'C')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

    def chapter_title(self, num, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, 'Section %d : %s' % (num, label), 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, body)
        self.ln()

def generate_report(output_path="outputs/UIDAI_Report.pdf", text_summary_path="outputs/executive_summary.txt"):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Read Executive Summary
    summary_text = "Executive Summary not found."
    if os.path.exists(text_summary_path):
        with open(text_summary_path, 'r', encoding='latin-1') as f:
            summary_text = f.read()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Executive Summary', 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, summary_text)
    
    # Add Visuals
    pdf.add_page()
    pdf.chapter_title(1, 'Key Visualizations')
    
    # Add images if they exist
    base_assets = os.path.join(os.path.dirname(__file__), 'assets')
    images = [
        ('timeseries_daily_trend.png', 'Daily Enrollment Trend'),
        ('clustering_visualization.png', 'District Clustering'),
        ('intervention_simulation.png', 'Intervention ROI')
    ]
    
    y = pdf.get_y()
    for img_file, title in images:
        img_path = os.path.join(base_assets, img_file)
        if os.path.exists(img_path):
            if y > 220:
                pdf.add_page()
                y = 20
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, title, 0, 1)
            pdf.image(img_path, x=10, w=170)
            pdf.ln(100) # Space for image
            y = pdf.get_y()
            
    pdf.output(output_path, 'F')
    return output_path

if __name__ == "__main__":
    generate_report()
