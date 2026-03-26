import subprocess
import os
import tempfile

def generate_pdf(text: str) -> bytes:
    """Compiles LaTeX code into a PDF using pdflatex and returns the PDF bytes."""
    
    # Clean out any accidental markdown codeblocks the AI might have still outputted
    if text.startswith("```latex"):
        text = text[8:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
        
    with tempfile.TemporaryDirectory() as temp_dir:
        tex_file_path = os.path.join(temp_dir, "cv.tex")
        pdf_file_path = os.path.join(temp_dir, "cv.pdf")
        
        with open(tex_file_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        # Run pdflatex inside the temp directory
        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "cv.tex"],
                cwd=temp_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            # If pdflatex fails, we still try to read the PDF if it produced one (nonstopmode)
            # Otherwise we raise the compilation error log
            if not os.path.exists(pdf_file_path):
                raise RuntimeError(f"LaTeX Compilation Failed: {e.stdout.decode('utf-8', errors='ignore')}")
                
        if not os.path.exists(pdf_file_path):
            raise RuntimeError("LaTeX completed but PDF was not generated.")
            
        with open(pdf_file_path, "rb") as f:
            return f.read()
