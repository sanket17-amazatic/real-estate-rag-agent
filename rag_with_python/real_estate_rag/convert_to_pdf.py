"""
Utility script to convert text files to PDF
This helps convert your mock data text file to PDF format for ingestion
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
import os


def text_to_pdf(input_text_file, output_pdf_file, title="Property Brochure"):
    """
    Convert text file to PDF
    
    Args:
        input_text_file: Path to input text file
        output_pdf_file: Path to output PDF file
        title: Document title
    """
    # Read text content
    with open(input_text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_pdf_file,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a237e',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Heading style
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#283593',
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Normal text style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Add title
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))
    
    # Split content into sections
    sections = content.split('---')
    
    for section in sections:
        if not section.strip():
            continue
        
        # Split section into lines
        lines = section.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 6))
                continue
            
            # Check if it's a heading (all caps or ends with specific patterns)
            if (line.isupper() and len(line) < 100) or line.startswith('File'):
                elements.append(Paragraph(line, heading_style))
            else:
                # Replace special characters
                line = line.replace('&', '&amp;')
                line = line.replace('<', '&lt;')
                line = line.replace('>', '&gt;')
                
                elements.append(Paragraph(line, normal_style))
        
        # Add page break between major sections
        if '========================' in section or 'File ' in section:
            elements.append(PageBreak())
    
    # Build PDF
    doc.build(elements)
    print(f"✅ PDF created successfully: {output_pdf_file}")


def convert_mock_data_to_pdfs(input_file):
    """
    Convert the mock data file into separate PDFs per project
    
    Args:
        input_file: Path to the NewLaunches_MockData.txt file
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create output directory
    output_dir = "data/pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Split by file markers
    projects = content.split('File ')
    
    for i, project in enumerate(projects[1:], 1):  # Skip first empty split
        if not project.strip():
            continue
        
        # Extract project name from first line
        lines = project.strip().split('\n')
        first_line = lines[0] if lines else f"Project_{i}"
        
        # Extract locality from first line (e.g., "1 – PRJ-NEW-2025-002 (Viman Nagar)")
        locality = "Unknown"
        if '(' in first_line and ')' in first_line:
            locality = first_line.split('(')[1].split(')')[0].strip()
        
        # Create filename
        safe_locality = locality.replace(' ', '_').replace('/', '_')
        output_file = os.path.join(output_dir, f"Property_{i}_{safe_locality}.pdf")
        
        # Add file marker back
        project_content = f"File {project}"
        
        # Create PDF for this project
        text_to_pdf(
            input_text_file=None,  # We'll write content directly
            output_pdf_file=output_file,
            title=f"{locality} Property Brochure"
        )
        
        # Write text content to temp file first
        temp_file = f"temp_project_{i}.txt"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(project_content)
        
        # Convert to PDF
        text_to_pdf(temp_file, output_file, f"{locality} Property Brochure")
        
        # Clean up temp file
        os.remove(temp_file)
        
        print(f"Created: {output_file}")


if __name__ == "__main__":
    import sys
    
    # Check if input file is provided
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # Use default file
        input_file = r"c:\Users\AH012\OneDrive\Desktop\DEMO\NewLaunches_MockData (1).txt"
    
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        print("\nUsage: python convert_to_pdf.py <input_text_file>")
        sys.exit(1)
    
    print(f"Converting: {input_file}")
    print("="*80)
    
    # Option 1: Convert entire file to single PDF
    output_pdf = "data/pdfs/NewLaunches_Complete.pdf"
    os.makedirs("data/pdfs", exist_ok=True)
    text_to_pdf(input_file, output_pdf, "Pune Real Estate - New Launches")
    
    print("\n" + "="*80)
    print(f"✅ Conversion complete!")
    print(f"📄 Output: {output_pdf}")
    print("\nYou can now upload this PDF using:")
    print(f'  curl -X POST "http://localhost:8000/ingest/pdf" -F "file=@{output_pdf}"')
