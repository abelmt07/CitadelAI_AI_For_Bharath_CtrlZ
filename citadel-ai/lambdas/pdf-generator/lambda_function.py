import json
import boto3
import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable
from reportlab.lib import colors

# AWS clients
s3 = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = os.environ.get('S3_BUCKET', 'citadel-audio-ctrlz')


def create_styles():
    """Define all text styles for the court document"""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='CourtHeader',
        fontSize=12,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading',
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_LEFT,
        spaceBefore=14,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='BodyText',
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
        leading=15
    ))
    styles.add(ParagraphStyle(
        name='CenterText',
        fontSize=10,
        fontName='Helvetica',
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='BoldCenter',
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='SmallText',
        fontSize=9,
        fontName='Helvetica',
        alignment=TA_LEFT,
        spaceBefore=2,
        spaceAfter=2,
        leading=13
    ))

    return styles


def add_page_number(canvas, doc):
    """Adds page numbers at bottom - court requirement, must be 1,2,3 no letters"""
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(A4[0] / 2, 0.4 * inch, f"- {page_num} -")
    canvas.restoreState()


def generate_form_i(case_data):
    """
    Generates complete Form I court complaint PDF matching official Prasad Law template.
    Includes all 10 sections + Verification + Affidavit.
    """

    # Extract data from Claude's analysis
    complainant_name   = case_data.get('complainant_name', 'Ramesh Kumar')
    father_name        = case_data.get('father_name', 'Shri [Father Name]')
    age                = case_data.get('age', '[Age]')
    complainant_address = case_data.get('complainant_address', 'Lucknow, Uttar Pradesh')
    opposite_party     = case_data.get('opposite_party', 'Bharti Airtel Limited')
    op_address         = case_data.get('op_address', 'Corporate Office, New Delhi - 110001')
    amount             = case_data.get('amount', 299)
    section            = case_data.get('section', '2(47)')
    has_sms            = case_data.get('has_sms_proof', True)
    has_bill           = case_data.get('has_billing_statement', True)

    # Calculated fields
    months         = 6
    total_deducted = amount * months
    compensation   = 5000
    total_relief   = total_deducted + compensation
    today          = datetime.now().strftime("%d/%m/%Y")
    day            = datetime.now().strftime("%d")
    month_year     = datetime.now().strftime("%B %Y")
    year           = datetime.now().strftime("%Y")

    # Build PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.0 * inch,
        leftMargin=1.0 * inch,
        topMargin=1.0 * inch,
        bottomMargin=0.75 * inch,
        title="Form I - Consumer Complaint"
    )

    styles = create_styles()
    story  = []

    # ============================================================
    # COURT HEADER
    # ============================================================
    story.append(Paragraph(
        "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL<br/>COMMISSION AT LUCKNOW",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(f"IN RE: COMPLAINT NO. ________ OF {year}", styles['CenterText']))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("IN THE MATTER OF:", styles['CenterText']))
    story.append(Spacer(1, 0.08 * inch))

    # Complainant block
    story.append(Paragraph(f"<b>{complainant_name}</b>", styles['CenterText']))
    story.append(Paragraph(f"{complainant_address}", styles['CenterText']))
    story.append(Paragraph("<b>....Complainant</b>", styles['CenterText']))
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph("<b>Versus</b>", styles['BoldCenter']))
    story.append(Spacer(1, 0.06 * inch))

    # Opposite party block
    story.append(Paragraph(f"<b>{opposite_party}</b>", styles['CenterText']))
    story.append(Paragraph(f"{op_address}", styles['CenterText']))
    story.append(Paragraph("<b>....Opposite Party</b>", styles['CenterText']))
    story.append(Spacer(1, 0.1 * inch))

    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph(
        "COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("<b>MOST RESPECTFULLY SHOWETH:</b>", styles['CenterText']))
    story.append(Spacer(1, 0.1 * inch))

    # ============================================================
    # SECTION 1: INTRODUCTION
    # ============================================================
    story.append(Paragraph("(1) INTRODUCTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"The Complainant, {complainant_name}, S/o {father_name}, aged {age} years, "
        f"is a resident of {complainant_address} and is a consumer of the Opposite "
        f"Party, {opposite_party}, having availed postpaid mobile connection services "
        f"since January 2024. The Opposite Party, {opposite_party}, is a registered "
        f"telecom company operating across India with its corporate office at {op_address}. "
        f"The Complainant is filing this complaint for unauthorized deduction of "
        f"Rs. {amount}/- per month without consent.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 2: TRANSACTION
    # ============================================================
    story.append(Paragraph("(2) TRANSACTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the Complainant has been availing postpaid mobile connection services "
        f"from the Opposite Party since January 2024. That from January 2025, the "
        f"Opposite Party began deducting Rs. {amount}/- per month as charges for a "
        f"so-called 'Value-Added Service' which was never subscribed to or consented "
        f"to by the Complainant. The Complainant received SMS notifications showing "
        f"these unauthorized deductions. Copies of billing statements are attached and "
        f"marked as <b>Annexure-A</b> and <b>Annexure-B</b>. Total unauthorized "
        f"amount deducted over {months} months: <b>Rs. {total_deducted}/-</b>.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 3: DEFECT / DEFICIENCY
    # ============================================================
    story.append(Paragraph("(3) DEFECT/DEFICIENCY", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the aforesaid act of the Opposite Party in deducting Rs. {amount}/- "
        f"per month without the knowledge or consent of the Complainant constitutes "
        f"an <b>Unfair Trade Practice</b> as defined under <b>Section {section} of "
        f"the Consumer Protection Act, 2019</b>. The Opposite Party failed to: "
        f"(a) obtain informed consent before activating the Value-Added Service; "
        f"(b) provide any written intimation of such activation; "
        f"(c) process refund requests despite repeated complaints. "
        f"This constitutes a clear deficiency in service and unfair trade practice.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 4: RECTIFICATION
    # ============================================================
    story.append(Paragraph("(4) RECTIFICATION", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the Complainant contacted the customer care of the Opposite Party on "
        f"approximately 5 (five) occasions requesting reversal of unauthorized charges "
        f"and deactivation of the unauthorized service. The Complainant also sent a "
        f"written complaint via email. However, the Opposite Party failed to provide "
        f"any satisfactory resolution and the unauthorized deductions continued. "
        f"No legal notice has been issued prior to this complaint as the cause of "
        f"action is continuing and the Complainant has been left with no other recourse.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 5: OTHER PROVISIONS
    # ============================================================
    story.append(Paragraph("(5) OTHER PROVISIONS", styles['SectionHeading']))
    story.append(Paragraph(
        "The acts of the Opposite Party are in violation of the following provisions: "
        "(a) <b>Section 2(47), Consumer Protection Act, 2019</b> — Unfair Trade Practice; "
        "(b) <b>Section 35, Consumer Protection Act, 2019</b> — Filing of Complaints; "
        "(c) <b>Section 42, Consumer Protection Act, 2019</b> — Compensation; "
        "(d) <b>TRAI Regulations</b> on Value-Added Services requiring prior written "
        "consent before activation of any paid service. The Complainant is entitled "
        "to protection under all of the above provisions.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 6: EVIDENCE
    # ============================================================
    story.append(Paragraph("(6) EVIDENCE", styles['SectionHeading']))
    story.append(Paragraph(
        "The Complainant shall rely upon the following documents, copies of which "
        "are annexed hereto as True Copies:",
        styles['BodyText']
    ))
    annexure_index = 'A'
    evidence_items = []
    if has_sms:
        evidence_items.append(f"<b>Annexure-{annexure_index}:</b> Copies of SMS messages showing unauthorized deductions (True Copy)")
        annexure_index = chr(ord(annexure_index) + 1)
    if has_bill:
        evidence_items.append(f"<b>Annexure-{annexure_index}:</b> Mobile billing statements for last 6 months (True Copy)")
        annexure_index = chr(ord(annexure_index) + 1)
    evidence_items.append(f"<b>Annexure-{annexure_index}:</b> Copy of Aadhaar Card — ID Proof of Complainant (True Copy)")

    for item in evidence_items:
        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{item}", styles['BodyText']))

    # ============================================================
    # SECTION 7: JURISDICTION
    # ============================================================
    story.append(Paragraph("(7) JURISDICTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"That the total amount involved in the present complaint is <b>Rs. {total_relief}/-</b> "
        f"(Rupees {total_relief} only) which is well within the pecuniary jurisdiction "
        f"of this Hon'ble District Commission (claims below Rs. 1 Crore fall under "
        f"District Commission jurisdiction as per Section 34 of the Consumer Protection "
        f"Act, 2019). The Complainant resides in Lucknow which falls within the "
        f"territorial jurisdiction of this Hon'ble Commission.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 8: LIMITATION
    # ============================================================
    story.append(Paragraph("(8) LIMITATION", styles['SectionHeading']))
    story.append(Paragraph(
        "That the present complaint is being filed within the period prescribed under "
        "Section 69 of the Consumer Protection Act, 2019. The cause of action is a "
        "continuing one as the unauthorized deductions are still ongoing and the "
        "Complainant continues to suffer loss month upon month.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 9: RELIEF CLAIMED
    # ============================================================
    story.append(Paragraph("(9) RELIEF CLAIMED", styles['SectionHeading']))
    story.append(Paragraph(
        "In light of the above facts and circumstances, the Complainant respectfully "
        "claims the following reliefs:",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(a) <b>Refund of Rs. {total_deducted}/-</b> "
        f"(Rs. {amount} x {months} months) being the total amount of unauthorized "
        f"deductions made without consent;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(b) <b>Compensation of Rs. {compensation}/-</b> for mental agony, "
        f"harassment and financial loss caused to the Complainant by the negligence "
        f"of the Opposite Party;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(c) <b>Total relief claimed: Rs. {total_relief}/-</b> "
        f"(Rs. {total_deducted} + Rs. {compensation});",
        styles['BodyText']
    ))
    story.append(Paragraph(
        "(d) Any other relief that this Hon'ble Commission deems fit and proper "
        "in the facts and circumstances of the present case.",
        styles['BodyText']
    ))

    # ============================================================
    # SECTION 10: PRAYER CLAUSE
    # ============================================================
    story.append(Paragraph("(10) PRAYER CLAUSE", styles['SectionHeading']))
    story.append(Paragraph(
        "It is, therefore, most respectfully prayed that this Hon'ble Commission "
        "may kindly be pleased to:",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(i) Direct the Opposite Party to refund Rs. {total_deducted}/- "
        f"being the total unauthorized deductions;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(ii) Direct the Opposite Party to pay Rs. {compensation}/- as "
        f"compensation for mental agony and harassment;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(iii) Direct the Opposite Party to immediately deactivate the "
        f"unauthorized Value-Added Service;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        "(iv) Grant such other and further relief as this Hon'ble Commission "
        "may deem fit and proper in the interest of justice.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.25 * inch))

    # Signature block
    story.append(Paragraph(f"Place: Lucknow", styles['BodyText']))
    story.append(Paragraph(f"Dated: {today}", styles['BodyText']))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        f"_______________________<br/>"
        f"<b>{complainant_name}</b><br/>"
        f"Complainant",
        styles['CenterText']
    ))

    # ============================================================
    # VERIFICATION
    # ============================================================
    story.append(PageBreak())
    story.append(Paragraph("<b>Verification</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"I, <b>{complainant_name}</b>, the complainant above named, do hereby "
        f"solemnly verify that the contents of my above complaint are true and "
        f"correct to my knowledge, no part of it is false and nothing material "
        f"has been concealed therein.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        f"Verified this <b>{day}</b> day of <b>{month_year}</b> at <b>Lucknow</b>.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        f"_______________________<br/>"
        f"<b>{complainant_name}</b><br/>"
        f"Complainant",
        styles['CenterText']
    ))

    # ============================================================
    # AFFIDAVIT IN SUPPORT OF COMPLAINT
    # ============================================================
    story.append(PageBreak())
    story.append(Paragraph(
        "AFFIDAVIT IN SUPPORT OF THE COMPLAINT",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(
        "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT LUCKNOW",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(f"IN RE: COMPLAINT NO. ________ OF {year}", styles['CenterText']))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("IN THE MATTER OF:", styles['CenterText']))
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph(f"<b>{complainant_name}</b> ....Complainant", styles['CenterText']))
    story.append(Paragraph("<b>Versus</b>", styles['CenterText']))
    story.append(Paragraph(f"<b>{opposite_party}</b> ....Opposite Party", styles['CenterText']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("<b>AFFIDAVIT</b>", styles['BoldCenter']))
    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph(
        f"Affidavit of <b>{complainant_name}</b> S/o <b>{father_name}</b>, "
        f"aged <b>{age} years</b>, resident of <b>{complainant_address}</b>.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph(
        "I, the above named deponent do hereby solemnly affirm and declare as under:",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.08 * inch))

    story.append(Paragraph(
        "(1) That I am the Complainant in the above case, thoroughly conversant "
        "with the facts and circumstances of the present case and am competent "
        "to swear this affidavit.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.06 * inch))
    story.append(Paragraph(
        "(2) That the facts contained in my accompanying complaint, the contents "
        "of which have not been repeated herein for the sake of brevity, may be "
        "read as an integral part of this affidavit and are true and correct "
        "to my knowledge.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        f"_______________________<br/>"
        f"<b>{complainant_name}</b><br/>"
        f"Deponent",
        styles['CenterText']
    ))

    # Affidavit Verification
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("<b>Verification</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"I, the above named deponent do hereby solemnly verify that the contents "
        f"of my above affidavit are true and correct to my knowledge, no part of "
        f"it is false and nothing has been concealed therein.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        f"Verified this <b>{day}</b> day of <b>{month_year}</b> at <b>Lucknow</b>.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.35 * inch))
    story.append(Paragraph(
        f"_______________________<br/>"
        f"<b>{complainant_name}</b><br/>"
        f"Deponent",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph(
        "<i>Note: This affidavit requires notarization before filing. "
        "Please get it attested from an Oath Commissioner appointed by a High Court.</i>",
        styles['SmallText']
    ))

    # ============================================================
    # ANNEXURES LIST PAGE
    # ============================================================
    story.append(PageBreak())
    story.append(Paragraph("LIST OF ANNEXURES", styles['CourtHeader']))
    story.append(Spacer(1, 0.1 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.1 * inch))

    ann_idx = 'A'
    if has_sms:
        story.append(Paragraph(
            f"<b>Annexure-{ann_idx}:</b> Copies of SMS/messages showing unauthorized "
            f"deductions of Rs. {amount}/- (True Copy)",
            styles['BodyText']
        ))
        ann_idx = chr(ord(ann_idx) + 1)
    if has_bill:
        story.append(Paragraph(
            f"<b>Annexure-{ann_idx}:</b> Mobile billing statements for last 6 months "
            f"showing recurring deductions (True Copy)",
            styles['BodyText']
        ))
        ann_idx = chr(ord(ann_idx) + 1)
    story.append(Paragraph(
        f"<b>Annexure-{ann_idx}:</b> Copy of Aadhaar Card — Identity Proof of "
        f"Complainant (True Copy)",
        styles['BodyText']
    ))

    # Build PDF with page numbers
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer


def lambda_handler(event, context):
    """
    CITADEL AI - PDF Generator Lambda
    Input:  Case data from Claude analyzer
    Output: S3 presigned URL to download Form I PDF
    """
    print("pdf-generator triggered")
    print("Event received:", json.dumps(event))

    try:
        body      = json.loads(event.get('body', '{}'))
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

        # Generate presigned URL valid for 1 hour
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
