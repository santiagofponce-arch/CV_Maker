from fpdf import FPDF
import io

def generate_pdf(text: str) -> bytes:
    """Converts a standard tailored CV markdown text to a basic PDF file."""
    # FPDF's built-in Helvetica doesn't support complex Unicode. 
    # We replace fancy quotes/bullets with standard ones to avoid errors.
    text = text.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-").replace("•", "-")
    
    # Strip any remaining problematic characters
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    import textwrap
    
    # Process line by line, pre-wrapping text to guarantee no FPDF crashes
    lines = clean_text.split('\n')
    
    for line in lines:
        stripped = line.strip()
        
        # Horizontal rules
        if stripped.startswith('---'):
            pdf.ln(2)
            y = pdf.get_y()
            pdf.line(15, y, 195, y)
            pdf.ln(4)
            continue
            
        # Headers
        if stripped.startswith('# '):
            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(0, 10, txt=stripped[2:], ln=True)
            pdf.ln(2)
        elif stripped.startswith('## '):
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, txt=stripped[3:], ln=True)
            pdf.ln(2)
        elif stripped.startswith('### '):
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 6, txt=stripped[4:], ln=True)
            pdf.ln(2)
            
        # Bullet Points
        elif stripped.startswith('- ') or stripped.startswith('* '):
            pdf.set_font("Helvetica", '', 11)
            # FPDF's basic Helvetica font only supports latin-1, so we use a standard dash instead of a unicode bullet
            bullet_text = "- " + stripped[2:]
            # Python's textwrap is crash-proof compared to FPDF's multi_cell
            wrapped_lines = textwrap.wrap(bullet_text, width=80)
            for i, wrap_line in enumerate(wrapped_lines):
                if i == 0:
                    pdf.set_x(20)
                else:
                    pdf.set_x(23) # Indent subsequent lines of a long bullet point
                pdf.cell(0, 6, txt=wrap_line, ln=True)

        # Standard Text and empty lines
        else:
            pdf.set_font("Helvetica", '', 11)
            if stripped == '':
                pdf.ln(2)
            else:
                wrapped_lines = textwrap.wrap(stripped, width=85)
                for wrap_line in wrapped_lines:
                    pdf.cell(0, 6, txt=wrap_line, ln=True)
    
    return bytes(pdf.output())
