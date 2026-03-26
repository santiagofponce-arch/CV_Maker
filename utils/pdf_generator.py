from fpdf import FPDF
import textwrap

class CVTemplate(FPDF):
    def footer(self):
        # Adds an automatic page number at the bottom of each page
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_pdf(text: str) -> bytes:
    """Converts a standard tailored CV markdown text to a professional PDF file."""
    text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf = CVTemplate()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(15, 15, 15)
    
    lines = clean_text.split('\n')
    
    # We assume text directly under the main # Header is contact info, so we center it!
    contact_info_mode = True 
    
    for line in lines:
        stripped = line.strip()
        
        # Horizontal rules
        if stripped.startswith('---'):
            pdf.ln(2)
            y = pdf.get_y()
            pdf.set_draw_color(200, 200, 200)
            pdf.line(15, y, 195, y)
            pdf.ln(4)
            continue
            
        # Main Header (Usually Name)
        if stripped.startswith('# '):
            pdf.set_font("Helvetica", 'B', 22)
            pdf.set_text_color(33, 50, 76) # Professional Dark Blue
            pdf.cell(0, 12, txt=stripped[2:].upper(), align="C", ln=True)
            pdf.ln(2)
            
        # Section Headers (Experience, Education)
        elif stripped.startswith('## '):
            contact_info_mode = False # Turn off contact info centering
            pdf.ln(6)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.set_text_color(33, 50, 76)
            pdf.cell(0, 8, txt=stripped[3:].upper(), ln=True)
            
            # Draw a sleek line directly under the section header
            y = pdf.get_y()
            pdf.set_draw_color(33, 50, 76)
            pdf.line(15, y, 195, y)
            pdf.ln(3)
            
        # Sub Headers (Job Titles, Companies)
        elif stripped.startswith('### '):
            contact_info_mode = False
            pdf.set_font("Helvetica", 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, txt=stripped[4:], ln=True)
            pdf.ln(1)
            
        # Bullet Points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            contact_info_mode = False
            pdf.set_font("Helvetica", '', 11)
            pdf.set_text_color(40, 40, 40) # Soft grey for easier reading
            bullet_text = "- " + stripped[2:]
            wrapped_lines = textwrap.wrap(bullet_text, width=90)
            for i, wrap_line in enumerate(wrapped_lines):
                if i == 0:
                    pdf.set_x(18)
                else:
                    pdf.set_x(21) # Indent underneath bullet point
                pdf.cell(0, 5, txt=wrap_line, ln=True)

        # Standard Text and empty lines
        else:
            if stripped == '':
                pdf.ln(2)
            else:
                if contact_info_mode:
                    # Center align contact info at the very top of the CV
                    pdf.set_font("Helvetica", '', 10)
                    pdf.set_text_color(100, 100, 100)
                    wrapped_lines = textwrap.wrap(stripped, width=95)
                    for wrap_line in wrapped_lines:
                        pdf.cell(0, 5, txt=wrap_line, align="C", ln=True)
                else:
                    pdf.set_font("Helvetica", '', 11)
                    pdf.set_text_color(40, 40, 40)
                    wrapped_lines = textwrap.wrap(stripped, width=95)
                    for wrap_line in wrapped_lines:
                        pdf.cell(0, 5, txt=wrap_line, ln=True)
    
    return bytes(pdf.output())
