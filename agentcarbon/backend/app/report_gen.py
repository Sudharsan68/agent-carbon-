from fpdf import FPDF
from datetime import datetime

class ESGReportPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 20)
        self.set_text_color(34, 139, 34)
        self.cell(0, 10, 'AgentCarbon', ln=True, align='L')
        self.ln(5)

def generate_real_pdf(email, total_co2, total_kwh, facilities, ai_insights):
    pdf = ESGReportPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'Corporate Sustainability Report', ln=True, align='C')
    pdf.ln(5)
    
    # Meta Info
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f'Generated for: {email}', ln=True)
    pdf.cell(0, 6, f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
    pdf.ln(10)
    
    # Executive Summary
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'Executive Summary', ln=True)
    pdf.set_font('helvetica', '', 12)
    
    # CRITICAL: These now use the passed variables, NO hardcoded numbers
    pdf.cell(0, 8, f"Total Carbon Emissions: {total_co2:,.2f} kg CO2", ln=True)
    pdf.cell(0, 8, f"Total Energy Consumption: {total_kwh:,.2f} kWh", ln=True)
    pdf.ln(5)
    
    # Facilities Table
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'Facility Distribution', ln=True)
    
    pdf.set_font('helvetica', 'B', 11)
    pdf.cell(80, 10, 'Facility Name', 1)
    pdf.cell(60, 10, 'Total CO2 (kg)', 1)
    pdf.cell(40, 10, 'Bill Count', 1)
    pdf.ln()
    
    pdf.set_font('helvetica', '', 11)
    if not facilities:
        pdf.cell(180, 10, 'No data available for this user.', 1, ln=True, align='C')
    else:
        for fac in facilities:
            pdf.cell(80, 10, str(fac.get('name', 'N/A')), 1)
            pdf.cell(60, 10, f"{fac.get('total_co2', 0):,.2f}", 1)
            pdf.cell(40, 10, str(fac.get('bill_count', 0)), 1)
            pdf.ln()

    # AI Insights
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'AI-Driven Insights & Reduction Strategies', ln=True)
    pdf.set_font('helvetica', '', 11)
    pdf.multi_cell(0, 7, ai_insights)
    
    return pdf.output()
