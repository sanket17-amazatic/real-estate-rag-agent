"""
Create a sample property PDF for testing ingestion
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os

def create_sample_property_pdf():
    """Create a sample PDF with property information"""
    
    # Create output directory
    os.makedirs("data/pdfs", exist_ok=True)
    
    # Sample property data
    content = """
WAKAD - NEW RESIDENTIAL PROJECTS

1. EVERGREEN HEIGHTS
Location: Wakad, Pune
Type: Residential Apartment
Configuration: 2 BHK, 3 BHK
Price Range: ₹75 Lakhs - ₹1.2 Crores
Area: 1100 - 1800 sq.ft.

Amenities:
- Swimming Pool
- Gymnasium
- Children's Play Area
- Clubhouse
- 24/7 Security
- Power Backup
- Landscaped Gardens
- Indoor Games Room

Connectivity:
- 10 minutes from Hinjewadi IT Park
- Near Pune-Mumbai Expressway
- Close to reputed schools and hospitals
- Easy access to Wakad Metro Station

Developer: Premium Constructions Pvt. Ltd.
Possession: December 2025
RERA Approved: Yes

2. SKYLINE RESIDENCY
Location: Wakad, Pune
Type: Luxury Apartments
Configuration: 2 BHK, 3 BHK, 4 BHK
Price Range: ₹85 Lakhs - ₹2 Crores
Area: 1200 - 2500 sq.ft.

Premium Amenities:
- Rooftop Swimming Pool
- State-of-the-art Gymnasium
- Yoga and Meditation Center
- Multipurpose Hall
- Indoor Sports Complex
- Guest Rooms
- Party Lawn
- Jogging Track
- Senior Citizen Park

Specifications:
- Vitrified Tiles Flooring
- Modular Kitchen
- Premium Bathroom Fittings
- Video Door Phone
- Earthquake Resistant Structure

Location Advantages:
- Prime location in Wakad
- 5 km from Hinjewadi IT Hub
- Adjacent to Shopping Malls
- International Schools nearby
- Multi-specialty Hospitals in vicinity

Developer: Skyline Developers
Possession: June 2026
RERA ID: P52100012345

3. GREEN VALLEY HOMES
Location: Wakad-Rahatani Road
Type: Affordable Housing
Configuration: 1 BHK, 2 BHK
Price Range: ₹45 Lakhs - ₹70 Lakhs
Area: 650 - 1100 sq.ft.

Features:
- PMAY Eligible
- Vastu Compliant
- Earthquake Resistant
- Rainwater Harvesting
- Solar Panel Installation

Basic Amenities:
- Children's Play Area
- Community Hall
- Parking Space
- Security Guards
- Water Supply
- Electricity Backup

Nearby Facilities:
- Schools: 1 km
- Hospitals: 2 km
- Markets: 500 meters
- Bus Stop: 200 meters

Developer: Green Valley Construction
Possession: Ready to Move
RERA Registered

RENTAL PROPERTIES IN WAKAD

1. Furnished 2 BHK - Paradise Complex
Rent: ₹25,000/month
Deposit: ₹75,000
Amenities: Fully Furnished, AC, Modular Kitchen, Covered Parking
Available: Immediate

2. Semi-Furnished 3 BHK - Royal Heights
Rent: ₹35,000/month
Deposit: ₹1,05,000
Amenities: Wardrobe, Kitchen Cabinets, Geyser, 2 Parking
Available: From 1st January

3. Office Space - Tech Plaza
Rent: ₹50/sq.ft.
Area: 1000-5000 sq.ft. available
Amenities: Centralized AC, Power Backup, Lift, Parking
Suitable for: IT Companies, Corporate Offices

LOCALITY INFORMATION - WAKAD

Infrastructure:
- Well-developed locality with excellent connectivity
- Part of Pune's IT corridor
- Metro connectivity planned
- Multiple bus routes available

Social Infrastructure:
- Schools: Euro School, Orchid School, Delhi Public School
- Hospitals: Life Care Hospital, Aditya Birla Hospital
- Shopping: D-Mart, Xion Mall, Brand Factory
- Restaurants: Multiple dining options
- Banks: All major banks present

Investment Potential:
- High rental yield
- Capital appreciation expected
- Growing IT sector nearby
- Excellent connectivity improving
- Planned infrastructure development

For more information, contact:
Real Estate Solutions
Phone: +91-9876543210
Email: info@realestate.com
"""

    # Create PDF
    output_path = "data/pdfs/Wakad_Properties_Sample.pdf"
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='darkblue',
        spaceAfter=12,
    )
    
    # Add content
    for line in content.strip().split('\n'):
        if line.strip():
            if line.strip().isupper() and len(line.strip()) > 10:
                # Main headings
                p = Paragraph(line.strip(), title_style)
            else:
                # Normal text
                p = Paragraph(line.strip(), styles['BodyText'])
            elements.append(p)
            elements.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(elements)
    
    print(f"✅ Created sample PDF: {output_path}")
    print(f"📄 File size: {os.path.getsize(output_path)} bytes")
    return output_path

if __name__ == "__main__":
    create_sample_property_pdf()
