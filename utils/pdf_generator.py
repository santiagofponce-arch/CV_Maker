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
    
    # Process line by line for professional styling
    lines = clean_text.split('\n')
    
    # helper to break up giant continuous strings (URLs, dashes)
    def break_long_words(s, max_len=60):
        words = s.split(' ')
        chunked = []
        for w in words:
            if len(w) > max_len:
                chunked.append(' '.join([w[i:i+max_len] for i in range(0, len(w), max_len)]))
            else:
                chunked.append(w)
        return ' '.join(chunked)

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('---'):
            # Horizontal rule instead of crashing on a long string of dashes
            pdf.ln(4)
            y = pdf.get_y()
            pdf.line(15, y, 195, y)
            pdf.ln(4)
            continue
            
        stripped = break_long_words(stripped)
        
        if stripped.startswith('# '):
            pdf.set_font("Helvetica", 'B', 16)
            pdf.cell(0, 10, text=stripped[2:], ln=True)
            pdf.ln(2)
        elif stripped.startswith('## '):
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, text=stripped[3:], ln=True)
            pdf.ln(2)
        elif stripped.startswith('### '):
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 6, text=stripped[4:], ln=True)
            pdf.ln(1)
        elif stripped.startswith('- ') or stripped.startswith('* '):
            pdf.set_font("Helvetica", '', 11)
            pdf.set_x(20)  # Indent for bullet points
            # Handle wrapping for long bullet points
            # text="• " works, but since we break long words above, this is safe from crashes
            try:
                pdf.multi_cell(0, 6, text="• " + stripped[2:])
            except ValueError:
                pdf.cell(0, 6, text="[Error wrapping bullet line]", ln=True)
        else:
            pdf.set_font("Helvetica", '', 11)
            if stripped == '':
                pdf.ln(2) # Add spacing for empty lines
            else:
                try:
                    pdf.multi_cell(0, 6, text=stripped)
                except ValueError:
                    pdf.cell(0, 6, text="[Error wrapping line]", ln=True)
    
    return bytes(pdf.output())
