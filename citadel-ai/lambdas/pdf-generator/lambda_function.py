import json
import boto3
import os
from io import BytesIO
from datetime import datetime

# ReportLab imports for PDF creation
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

# AWS clients
s3 = boto3.client('s3', region_name='ap-south-1')
BUCKET_NAME = os.environ.get('S3_BUCKET', 'citadel-ai-audio')

def create_styles():
    """Define all text styles for the court document"""
    styles = getSampleStyleSheet()
    
    # Court header - centered, bold
    styles.add(ParagraphStyle(
        name='CourtHeader',
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=6
    ))
    
    # Section heading
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceBefore=12,
        spaceAfter=6
    ))
    
    # Body text - justified like a real legal document
    styles.add(ParagraphStyle(
        name='BodyText',
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
        leading=14
    ))
    
    # Center aligned body
    styles.add(ParagraphStyle(
        name='CenterText',
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4
    ))
    
    return styles

def add_page_number(canvas, doc):
    """Adds page numbers at the bottom of every page - court requirement"""
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(A4[0] / 2, 0.5 * inch, f"- {page_num} -")
    canvas.restoreState()

def generate_form_i(case_data):
    """
    Generates the complete Form I court complaint PDF.
    case_data comes from the Claude analyzer output.
    """
    
    # Extract data from Claude's analysis
    complainant_name = case_data.get('complainant_name', 'Ramesh Kumar')
    complainant_address = case_data.get('complainant_address', 'Lucknow, Uttar Pradesh')
    opposite_party = case_data.get('opposite_party', 'Bharti Airtel Limited')
    amount = case_data.get('amount', 299)
    issue_type = case_data.get('issue_type', 'unfair_trade_practice')
    section = case_data.get('section', '2(47)')
    has_sms = case_data.get('has_sms_proof', True)
    has_bill = case_data.get('has_billing_statement', True)
    
    # Calculate relief amount
    months = 6
    total_deducted = amount * months
    compensation = 5000
    total_relief = total_deducted + compensation
    today = datetime.now().strftime("%d/%m/%Y")
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=0.75 * inch
    )
    
    styles = create_styles()
    story = []
    
    # ============================================
    # SECTION 1: COURT HEADER
    # ============================================
    story.append(Paragraph(
        "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT LUCKNOW",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("CONSUMER COMPLAINT NO. _______ / 2025", styles['CenterText']))
    story.append(Spacer(1, 0.1 * inch))
    
    # Parties table
    parties_data = [
        [f"{complainant_name}\n{complainant_address}", '', 'COMPLAINANT'],
        ['VERSUS', '', ''],
        [f"{opposite_party}\nCorporate Office, New Delhi", '', 'OPPOSITE PARTY']
    ]
    
    story.append(Paragraph(f"<b>{complainant_name}</b>, {complainant_address}", styles['BodyText']))
    story.append(Paragraph("<b>...COMPLAINANT</b>", styles['CenterText']))
    story.append(Paragraph("<b>VERSUS</b>", styles['CenterText']))
    story.append(Paragraph(f"<b>{opposite_party}</b>, Corporate Office, New Delhi", styles['BodyText']))
    story.append(Paragraph("<b>...OPPOSITE PARTY</b>", styles['CenterText']))
    story.append(Spacer(1, 0.1 * inch))
    
    story.append(Paragraph(
        "COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.15 * inch))
    
    # ============================================
    # SECTION 2: INTRODUCTION
    # ============================================
    story.append(Paragraph("1. INTRODUCTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"The Complainant, {complainant_name}, is a resident of {complainant_address} "
        f"and is a consumer of the Opposite Party, {opposite_party}, having availed "
        f"postpaid mobile connection services since January 2024. The Complainant is "
        f"filing this complaint against the Opposite Party for unauthorized deduction "
        f"of Rs. {amount}/- per month without consent.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 3: TRANSACTION DETAILS
    # ============================================
    story.append(Paragraph("2. TRANSACTION DETAILS", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the Complainant has been availing postpaid mobile connection services "
        f"from the Opposite Party since January 2024. That from the month of January 2025, "
        f"the Opposite Party has been deducting Rs. {amount}/- per month from the "
        f"Complainant's account as charges for a Value-Added Service which was never "
        f"subscribed to or consented to by the Complainant. The total amount deducted "
        f"over {months} months amounts to Rs. {total_deducted}/-.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 4: DEFECT / DEFICIENCY
    # ============================================
    story.append(Paragraph("3. DEFECT / DEFICIENCY IN SERVICE", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the aforesaid act of the Opposite Party in deducting Rs. {amount}/- "
        f"per month without the consent of the Complainant constitutes an "
        f"<b>Unfair Trade Practice</b> as defined under <b>Section {section} of the "
        f"Consumer Protection Act, 2019</b>. The Opposite Party has failed to obtain "
        f"informed consent before activating the Value-Added Service and has continued "
        f"deductions despite repeated complaints by the Complainant.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 5: RECTIFICATION ATTEMPTS
    # ============================================
    story.append(Paragraph("4. ATTEMPTS AT RECTIFICATION", styles['SectionHeading']))
    story.append(Paragraph(
        "That the Complainant contacted the customer care of the Opposite Party on "
        "multiple occasions (approximately 5 times) requesting reversal of the "
        "unauthorized charges and deactivation of the unauthorized service. However, "
        "the Opposite Party failed to provide any satisfactory resolution and the "
        "unauthorized deductions continued unabated.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 6: OTHER LEGAL PROVISIONS
    # ============================================
    story.append(Paragraph("5. VIOLATION OF LEGAL PROVISIONS", styles['SectionHeading']))
    story.append(Paragraph(
        "The acts of the Opposite Party are in violation of the following provisions: "
        "(a) Consumer Protection Act, 2019 - Section 2(47) (Unfair Trade Practice); "
        "(b) Consumer Protection Act, 2019 - Section 35 (Filing of Complaints); "
        "(c) Telecom Regulatory Authority of India (TRAI) Regulations regarding "
        "Value-Added Services and prior consent requirements.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 7: EVIDENCE
    # ============================================
    story.append(Paragraph("6. EVIDENCE", styles['SectionHeading']))
    evidence_list = []
    if has_sms:
        evidence_list.append("Annexure A: Copies of SMS/messages showing unauthorized deductions")
    if has_bill:
        evidence_list.append("Annexure B: Mobile billing statements for last 6 months")
    evidence_list.append("Annexure C: Copy of Aadhaar Card (ID Proof)")
    
    for item in evidence_list:
        story.append(Paragraph(f"• {item}", styles['BodyText']))
    
    # ============================================
    # SECTION 8: JURISDICTION
    # ============================================
    story.append(Paragraph("7. JURISDICTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the total amount involved in the present complaint is Rs. {total_relief}/- "
        f"(Rupees {total_relief} only) which is well within the pecuniary jurisdiction "
        f"of this Hon'ble District Commission (below Rs. 1 Crore). The Complainant "
        f"resides within the territorial jurisdiction of this Hon'ble Commission at Lucknow.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 9: LIMITATION
    # ============================================
    story.append(Paragraph("8. LIMITATION", styles['SectionHeading']))
    story.append(Paragraph(
        "That the cause of action is a continuing one as the unauthorized deductions "
        "are still ongoing. The present complaint is being filed within the limitation "
        "period as prescribed under Section 69 of the Consumer Protection Act, 2019.",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 10: RELIEF CLAIMED
    # ============================================
    story.append(Paragraph("9. RELIEF CLAIMED", styles['SectionHeading']))
    story.append(Paragraph(
        f"In light of the above facts and circumstances, the Complainant most "
        f"respectfully prays that this Hon'ble Commission may be pleased to:",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(a) Direct the Opposite Party to refund Rs. {total_deducted}/- "
        f"(Rs. {amount} x {months} months) being the total unauthorized deductions;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(b) Direct the Opposite Party to pay Rs. {compensation}/- as compensation "
        f"for mental agony and harassment caused to the Complainant;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(c) Total relief claimed: Rs. {total_relief}/-",
        styles['BodyText']
    ))
    
    # ============================================
    # SECTION 11: PRAYER CLAUSE
    # ============================================
    story.append(Paragraph("10. PRAYER", styles['SectionHeading']))
    story.append(Paragraph(
        "It is therefore most humbly prayed that this Hon'ble Commission may graciously "
        "be pleased to allow the present complaint and grant the reliefs as prayed above "
        "in the interest of justice.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"Place: Lucknow", styles['BodyText']))
    story.append(Paragraph(f"Date: {today}", styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"(Signature of Complainant)<br/>{complainant_name}", styles['BodyText']))
    
    # ============================================
    # VERIFICATION CLAUSE
    # ============================================
    story.append(PageBreak())
    story.append(Paragraph("VERIFICATION", styles['SectionHeading']))
    story.append(Paragraph(
        f"I, {complainant_name}, the Complainant above named, do hereby verify "
        f"that the contents of the above complaint are true and correct to the best "
        f"of my knowledge and belief and nothing material has been concealed therefrom.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(f"Verified at Lucknow on this {today}", styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("(Signature of Complainant)", styles['BodyText']))
    story.append(Paragraph(f"{complainant_name}", styles['BodyText']))
    
    # ============================================
    # ANNEXURES LIST
    # ============================================
    story.append(PageBreak())
    story.append(Paragraph("LIST OF ANNEXURES", styles['SectionHeading']))
    annexures = [
        ["Annexure A", "Copies of SMS/messages showing unauthorized deductions"],
        ["Annexure B", "Mobile billing statements for last 6 months"],
        ["Annexure C", "Copy of Aadhaar Card (ID Proof)"]
    ]
    for ann, desc in annexures:
        story.append(Paragraph(f"<b>{ann}:</b> {desc}", styles['BodyText']))
    
    # Build the PDF with page numbers
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    buffer.seek(0)
    return buffer

def lambda_handler(event, context):
    """
    CITADEL AI - PDF Generator
    Input:  Case data from Claude analyzer
    Output: S3 presigned URL to download Form I PDF
    """
    print("pdf-generator triggered")
    print("Event received:", json.dumps(event))
    
    try:
        # Get case data from input
        body = json.loads(event.get('body', '{}'))
        case_data = body.get('case_data', {})
        
        # Generate the PDF
        pdf_buffer = generate_form_i(case_data)
        
        # Upload to S3
        file_name = f"complaints/form-i-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=pdf_buffer.getvalue(),
            ContentType='application/pdf'
        )
        
        # Generate presigned URL (valid for 1 hour)
        pdf_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_name},
            ExpiresIn=3600
        )
        
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "pdf_url": pdf_url,
                "file_name": file_name,
                "message": "Form I generated successfully"
            })
        }
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
