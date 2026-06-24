from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def create_structured_pdf(filename):
    print(f"🛠️ Generating a brand new structured PDF: {filename}...")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    
    # Set up styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontSize=16,
        leading=20,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=12
    )

    # Document Content
    story.append(Paragraph("Quantum Smart Mug Pro - User Manual", title_style))
    story.append(Spacer(1, 20))
    
    # Section 1
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph(
        "Welcome to the future of beverage containment. The Quantum Smart Mug Pro is engineered "
        "to maintain your drinks at the exact atomic temperature you desire. Equipped with a "
        "micro-fusion heating element and Bluetooth 6.0, this mug ensures your coffee never goes cold.", 
        body_style
    ))
    
    # Section 2
    story.append(Paragraph("2. Technical Specifications", h1_style))
    story.append(Paragraph("• Battery Capacity: 10,000 mAh internal lithium-ion cell.", body_style))
    story.append(Paragraph("• Operating Temperature Range: 45°C to 85°C (113°F to 185°F).", body_style))
    story.append(Paragraph("• Charging Interface: Liquid-proof USB-C and 15W wireless magnetic base.", body_style))
    story.append(Paragraph("• Weight: 450 grams when completely empty.", body_style))
    
    # Section 3
    story.append(Paragraph("3. Setup and Pairing", h1_style))
    story.append(Paragraph(
        "To connect your mug to your smartphone, hold down the power button on the bottom of the "
        "base for exactly 5 seconds until the LED indicator pulses blue. open the Quantum Brew App "
        "and select 'Scan for Devices'. The default pairing passcode is 0000.", 
        body_style
    ))
    
    # Section 4
    story.append(Paragraph("4. Troubleshooting Guide", h1_style))
    story.append(Paragraph(
        "If your mug flashes a red light, it indicates a thermal overload. Turn off the device "
        "immediately and let it cool for 15 minutes. For connection issues, reset the network "
        "chip by pressing the power button 3 times rapidly.", 
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print("✅ Successfully generated sample.pdf with real text!")

if __name__ == "__main__":
    create_structured_pdf("sample.pdf")
