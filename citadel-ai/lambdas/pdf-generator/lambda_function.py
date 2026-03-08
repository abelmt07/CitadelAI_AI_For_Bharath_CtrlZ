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


def blank(val, length=20):
    """Return val if meaningful, else underscores for hand-filling."""
    v = str(val).strip() if val else ''
    if not v or v in ('None', 'null', '0', '___________________', '____', '[Age]', '[Father Name]'):
        return '_' * length
    return v

s3 = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = os.environ.get('S3_BUCKET', 'citadel-audio-ctrlz')

# ─── Issue type → human readable label ───────────────────────────────────────
ISSUE_LABELS = {
    'unauthorized_charge':      'Unauthorized Charge / Unfair Trade Practice',
    'defective_product':        'Supply of Defective Product',
    'service_delay':            'Deficiency in Service — Unreasonable Delay',
    'refund_not_processed':     'Failure to Process Refund',
    'misleading_advertisement': 'Misleading Advertisement',
    'unfair_trade_practice':    'Unfair Trade Practice',
    'deficiency_in_service':    'Deficiency in Service',
    'other':                    'Consumer Rights Violation',
}

# ─── Issue type → primary section ────────────────────────────────────────────
SECTION_MAP = {
    'unauthorized_charge':      '2(47)',
    'defective_product':        '2(9)',
    'service_delay':            '2(11)',
    'refund_not_processed':     '2(47)',
    'misleading_advertisement': '2(28)',
    'unfair_trade_practice':    '2(47)',
    'deficiency_in_service':    '2(11)',
    'other':                    '2(47)',
}

# ─── Issue type → all applicable sections with descriptions ──────────────────
APPLICABLE_SECTIONS = {
    'unauthorized_charge': [
        ('2(47)', 'Unfair Trade Practice — unauthorized deduction without consent'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('39(1)(d)', 'Order to cease unfair trade practice'),
        ('42',    'Compensation for loss and injury suffered'),
    ],
    'defective_product': [
        ('2(9)',  'Defect in goods — product not conforming to quality standards'),
        ('2(34)', 'Product liability — manufacturer/seller responsible for defect'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('42',    'Compensation for defective product and consequential loss'),
    ],
    'service_delay': [
        ('2(11)', 'Deficiency in service — failure to maintain standard of performance'),
        ('2(42)', 'Unfair contract terms — unreasonable service conditions'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('42',    'Compensation for mental agony and financial loss due to delay'),
    ],
    'refund_not_processed': [
        ('2(47)', 'Unfair Trade Practice — withholding legitimate refund'),
        ('2(11)', 'Deficiency in service — failure to honour refund commitment'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('42',    'Compensation for wrongful retention of money'),
    ],
    'misleading_advertisement': [
        ('2(28)', 'Misleading advertisement — false representation to consumer'),
        ('2(47)', 'Unfair Trade Practice — deceptive promotion of goods/services'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('42',    'Compensation for loss caused by reliance on false advertisement'),
    ],
    'unfair_trade_practice': [
        ('2(47)', 'Unfair Trade Practice — deceptive practice causing loss'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('39(1)(d)', 'Order to discontinue unfair trade practice'),
        ('42',    'Compensation for financial loss and mental agony'),
    ],
    'deficiency_in_service': [
        ('2(11)', 'Deficiency in service — failure to render promised service'),
        ('2(42)', 'Unfair contract — one-sided terms against consumer interest'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('42',    'Compensation for loss due to service deficiency'),
    ],
    'other': [
        ('2(47)', 'Unfair Trade Practice — violation of consumer rights'),
        ('35',    'Filing of complaint before District Consumer Commission'),
        ('42',    'Compensation for loss and mental agony'),
    ],
}

# ─── Issue type → elaborated introduction paragraph ──────────────────────────
INTRO_TEXT = {
    'unauthorized_charge': (
        "The Complainant is a bonafide consumer of the Opposite Party and has been availing "
        "their services by paying the agreed charges regularly and without default. Without any "
        "prior intimation, written consent, or authorization from the Complainant, the Opposite "
        "Party began deducting additional charges from the Complainant's account. Such deductions "
        "were made covertly, without any clear disclosure, and constitute a grave violation of the "
        "Complainant's rights as a consumer. The Complainant brings this complaint seeking refund "
        "of all unauthorized amounts and appropriate compensation."
    ),
    'defective_product': (
        "The Complainant purchased a product from the Opposite Party after relying upon the "
        "representations, specifications, and warranties made by the Opposite Party regarding the "
        "quality, performance, and fitness of the said product. Upon receipt and use, the "
        "Complainant discovered that the product was defective, did not conform to the promised "
        "specifications, and was unfit for the purpose for which it was sold. Despite bringing "
        "this defect to the attention of the Opposite Party, no satisfactory remedy was offered, "
        "thereby causing financial loss and mental agony to the Complainant."
    ),
    'service_delay': (
        "The Complainant engaged the services of the Opposite Party upon payment of the agreed "
        "consideration, relying on the promised timeline and delivery commitment made at the time "
        "of placing the order. The Opposite Party, in gross violation of its contractual and "
        "statutory obligations, failed to deliver the said service/product within the stipulated "
        "time, causing significant inconvenience, financial loss, and mental distress to the "
        "Complainant. Such failure constitutes a clear deficiency in service under the Consumer "
        "Protection Act, 2019."
    ),
    'refund_not_processed': (
        "The Complainant made a legitimate purchase from the Opposite Party and subsequently, "
        "being entitled to a refund either due to cancellation, return of defective goods, or "
        "non-delivery of service, made a valid request for refund of the amount paid. Despite "
        "repeated follow-ups over an extended period, the Opposite Party has wrongfully withheld "
        "the refund amount, thereby illegally retaining the Complainant's money without any "
        "legal justification. Such conduct amounts to an unfair trade practice and deficiency "
        "in service under the Consumer Protection Act, 2019."
    ),
    'misleading_advertisement': (
        "The Complainant was induced to purchase goods/avail services from the Opposite Party "
        "solely on the basis of representations, promises, and assurances made in the "
        "Opposite Party's advertisements and promotional materials. The said advertisements "
        "contained materially false and misleading statements regarding the quality, features, "
        "benefits, price, and terms of the product/service. The Complainant, relying in good "
        "faith upon such representations, made payment and upon availing the product/service "
        "discovered that the actual offering fell far short of what was promised, causing "
        "financial loss and mental agony."
    ),
    'unfair_trade_practice': (
        "The Complainant is a bonafide consumer of the Opposite Party and has been subjected "
        "to an unfair trade practice adopted by the Opposite Party in the course of its trade "
        "and business. The Opposite Party, through deceptive, manipulative, and unconscionable "
        "practices, has caused wrongful loss to the Complainant. Such practices are squarely "
        "prohibited under Section 2(47) of the Consumer Protection Act, 2019, and the "
        "Complainant is entitled to seek appropriate redress before this Hon'ble Commission."
    ),
    'deficiency_in_service': (
        "The Complainant availed services from the Opposite Party upon payment of agreed "
        "charges, and had a legitimate expectation of receiving the standard of service as "
        "promised and as required under law. The Opposite Party has failed to render services "
        "of the promised quality and standard, and has acted in a negligent and deficient "
        "manner, causing direct financial loss, inconvenience, and mental agony to the "
        "Complainant. Such conduct constitutes a clear deficiency in service as defined under "
        "Section 2(11) of the Consumer Protection Act, 2019."
    ),
    'other': (
        "The Complainant is a bonafide consumer who has suffered loss on account of the "
        "acts and omissions of the Opposite Party, which constitute a violation of the "
        "Complainant's rights under the Consumer Protection Act, 2019. The Complainant "
        "has made good faith efforts to resolve the matter directly with the Opposite Party, "
        "but having received no satisfactory response, is constrained to approach this "
        "Hon'ble Commission for appropriate relief."
    ),
}

# ─── Issue type → elaborated transaction paragraph ───────────────────────────
TRANSACTION_TEXT = {
    'unauthorized_charge': (
        "That the Complainant is a consumer of the Opposite Party and has been regularly "
        "paying agreed charges for services availed. That starting from the month of "
        "{month_year}, the Opposite Party began deducting Rs. {amount}/- per month "
        "from the Complainant's account under the garb of charges for services which "
        "were never subscribed to or consented to by the Complainant. The Complainant "
        "received notifications showing these deductions but was never informed of any "
        "new service activation. The total unauthorized amount deducted over "
        "{months} months is <b>Rs. {total_deducted}/-</b>. Copies of relevant "
        "statements and messages are attached as <b>Annexure-A</b> and <b>Annexure-B</b>."
    ),
    'defective_product': (
        "That the Complainant purchased a product from the Opposite Party, {opposite_party}, "
        "for a consideration of Rs. {amount}/-, relying upon the specifications and quality "
        "assurances provided. Upon receipt of the product, the Complainant discovered "
        "material defects rendering the product unfit for use. The Complainant immediately "
        "brought the defect to the notice of the Opposite Party through their customer "
        "care channel. Despite the product being clearly defective, the Opposite Party "
        "failed to provide replacement or refund. A copy of the purchase receipt is "
        "attached as <b>Annexure-A</b> and photographs of the defect as <b>Annexure-B</b>."
    ),
    'service_delay': (
        "That the Complainant placed an order for goods/services with the Opposite Party, "
        "{opposite_party}, upon payment of Rs. {amount}/-, with a specific and confirmed "
        "delivery/service timeline. Despite the Opposite Party's commitment, the "
        "service/delivery was delayed by an unreasonable and unacceptable period, causing "
        "significant inconvenience and loss to the Complainant. The Complainant repeatedly "
        "contacted the Opposite Party's customer support to follow up, but received only "
        "vague assurances and no concrete resolution. A copy of the order confirmation is "
        "attached as <b>Annexure-A</b> and communication records as <b>Annexure-B</b>."
    ),
    'refund_not_processed': (
        "That the Complainant had made a payment of Rs. {amount}/- to the Opposite Party, "
        "{opposite_party}, for goods or services. Subsequently, the Complainant became "
        "entitled to a refund on account of cancellation/return/non-delivery and made a "
        "formal refund request. The Opposite Party acknowledged the refund request but "
        "has failed to process and credit the same despite the passage of a reasonable "
        "period. The Complainant has followed up on multiple occasions through calls and "
        "emails. Copies of payment proof and refund request are attached as "
        "<b>Annexure-A</b> and <b>Annexure-B</b> respectively."
    ),
    'misleading_advertisement': (
        "That the Complainant was attracted to the product/service of the Opposite Party, "
        "{opposite_party}, on the basis of an advertisement which promised specific "
        "features, benefits, and terms. The Complainant made a payment of Rs. {amount}/- "
        "relying entirely on the said advertisement. Upon availing the product/service, "
        "the Complainant discovered that the actual offering was materially different "
        "from what was advertised — key features were absent, terms were different, "
        "and the promised benefits were not delivered. A copy of the advertisement "
        "is attached as <b>Annexure-A</b> and purchase receipt as <b>Annexure-B</b>."
    ),
    'unfair_trade_practice': (
        "That the Complainant availed goods/services from the Opposite Party, "
        "{opposite_party}, for consideration of Rs. {amount}/-. In the course of "
        "the transaction, the Opposite Party engaged in unfair trade practices "
        "including but not limited to deceptive pricing, hidden charges, forced "
        "bundling, or misrepresentation of terms. Such practices caused direct "
        "financial loss to the Complainant. The Complainant raised objections with "
        "the Opposite Party but received no satisfactory response. Copies of "
        "relevant documents are attached as <b>Annexure-A</b> and <b>Annexure-B</b>."
    ),
    'deficiency_in_service': (
        "That the Complainant engaged the Opposite Party, {opposite_party}, for "
        "provision of services upon payment of Rs. {amount}/-. The Opposite Party "
        "failed to render services of the agreed standard, quality, and completeness, "
        "thereby committing a deficiency in service. The Complainant raised the "
        "issue of deficiency with the Opposite Party on multiple occasions through "
        "their official channels but received no adequate remedy. Copies of the "
        "service agreement and complaint records are attached as <b>Annexure-A</b> "
        "and <b>Annexure-B</b>."
    ),
    'other': (
        "That the Complainant was a consumer of the Opposite Party, {opposite_party}, "
        "and had a transaction involving Rs. {amount}/-. The Opposite Party committed "
        "acts and omissions causing loss and injury to the Complainant. Despite "
        "repeated attempts to resolve the matter directly with the Opposite Party, "
        "no satisfactory resolution was offered. Copies of relevant documents "
        "evidencing the transaction are attached as <b>Annexure-A</b> and "
        "<b>Annexure-B</b>."
    ),
}

# ─── Issue type → elaborated deficiency paragraph ────────────────────────────
DEFICIENCY_TEXT = {
    'unauthorized_charge': (
        "That the aforesaid act of the Opposite Party in deducting Rs. {amount}/- per "
        "month from the Complainant's account without informed consent, prior intimation, "
        "or written authorization constitutes a gross <b>Unfair Trade Practice</b> as "
        "defined under <b>Section {section} of the Consumer Protection Act, 2019</b>. "
        "The Opposite Party has specifically failed to: (a) obtain prior written consent "
        "before levying additional charges; (b) provide clear and transparent disclosure "
        "of the nature and basis of the charge; (c) offer the Complainant an opportunity "
        "to opt out before deduction; (d) process the Complainant's refund request despite "
        "repeated follow-ups. Such conduct is unconscionable and exploitative of the "
        "Complainant's trust as a loyal customer."
    ),
    'defective_product': (
        "That the product supplied by the Opposite Party suffered from a manifest "
        "<b>defect</b> as defined under <b>Section {section} of the Consumer Protection "
        "Act, 2019</b>, rendering it unfit for its intended purpose and not conforming "
        "to the quality, quantity, potency, purity or standard prescribed or claimed "
        "by the Opposite Party. The Opposite Party is liable under the doctrine of "
        "product liability for: (a) manufacturing or selling a defective product; "
        "(b) failure to adequately inspect and ensure quality before sale; (c) failure "
        "to provide replacement or full refund upon complaint; (d) causing financial "
        "loss and mental agony to the Complainant by virtue of the said defect."
    ),
    'service_delay': (
        "That the failure of the Opposite Party to deliver services within the "
        "committed timeline constitutes a clear <b>Deficiency in Service</b> under "
        "<b>Section {section} of the Consumer Protection Act, 2019</b>. A service "
        "provider is legally obligated to maintain the quality, nature, and manner "
        "of performance which a purchaser may reasonably expect. The Opposite Party "
        "has specifically failed to: (a) fulfil its contractual commitment of timely "
        "delivery; (b) proactively communicate the delay and its reasons; (c) offer "
        "compensation or alternative arrangements during the delay period; (d) process "
        "a refund upon the Complainant's request arising from the delay."
    ),
    'refund_not_processed': (
        "That the deliberate and unjustified withholding of the Complainant's refund "
        "amount by the Opposite Party constitutes both a <b>Deficiency in Service</b> "
        "and an <b>Unfair Trade Practice</b> under <b>Section {section} of the Consumer "
        "Protection Act, 2019</b>. Once the Opposite Party acknowledged the "
        "Complainant's entitlement to a refund, it was under a legal and moral "
        "obligation to process the same promptly. The Opposite Party has: (a) wrongfully "
        "retained the Complainant's money without legal justification; (b) failed to "
        "adhere to its own published refund policy; (c) caused the Complainant to "
        "suffer loss of use of funds and resultant financial inconvenience; (d) shown "
        "willful disregard for the Complainant's rights."
    ),
    'misleading_advertisement': (
        "That the publication and circulation of a materially false and misleading "
        "advertisement by the Opposite Party constitutes a <b>Misleading Advertisement</b> "
        "and an <b>Unfair Trade Practice</b> under <b>Section {section} of the Consumer "
        "Protection Act, 2019</b>. The Opposite Party has specifically: (a) made false "
        "representations regarding the quality, features, and benefits of its "
        "product/service; (b) used deceptive language and imagery to induce purchase; "
        "(c) concealed material facts and conditions that would have affected the "
        "Complainant's purchasing decision; (d) refused to honour the promises made "
        "in the advertisement, thereby causing direct financial loss to the Complainant."
    ),
    'unfair_trade_practice': (
        "That the conduct of the Opposite Party amounts to an <b>Unfair Trade Practice</b> "
        "as defined under <b>Section {section} of the Consumer Protection Act, 2019</b>. "
        "The Opposite Party has engaged in practices that are deceptive, manipulative, "
        "and prejudicial to the interests of the Complainant as a consumer. Specifically, "
        "the Opposite Party has: (a) adopted unfair methods in the course of its trade; "
        "(b) caused wrongful loss to the Complainant through such practices; (c) refused "
        "to acknowledge or remedy the loss caused; (d) exploited its position of "
        "dominance to the detriment of the Complainant."
    ),
    'deficiency_in_service': (
        "That the acts and omissions of the Opposite Party constitute a clear "
        "<b>Deficiency in Service</b> as defined under <b>Section {section} of the "
        "Consumer Protection Act, 2019</b>. The Opposite Party has failed to maintain "
        "the standard of performance which a purchaser of such services may reasonably "
        "expect. Specifically: (a) the services rendered fell short of the agreed "
        "standard and quality; (b) the Opposite Party was negligent and indifferent "
        "to the Complainant's concerns; (c) despite repeated complaints, no remedial "
        "action was taken; (d) the Complainant suffered direct financial loss and "
        "mental agony as a direct consequence of such deficiency."
    ),
    'other': (
        "That the conduct of the Opposite Party constitutes a violation of the "
        "Complainant's rights as a consumer under the Consumer Protection Act, 2019, "
        "including but not limited to <b>Section {section}</b>. The Opposite Party "
        "has failed in its duty of care towards the Complainant and has caused "
        "loss, injury, and mental agony by its acts and omissions. The Complainant "
        "has been left with no alternative but to approach this Hon'ble Commission "
        "for appropriate redress."
    ),
}

# ─── Issue type → rectification paragraph ────────────────────────────────────
RECTIFICATION_TEXT = {
    'unauthorized_charge': (
        "That upon discovering the unauthorized deductions, the Complainant immediately "
        "contacted the customer care department of the Opposite Party on no less than "
        "five (5) occasions through phone calls, email, and the Opposite Party's "
        "official app. On each occasion, the Complainant was either put on hold for "
        "extended periods, transferred between departments, or given vague assurances "
        "of resolution within a few days — none of which materialized. The Opposite "
        "Party's customer care representatives acknowledged the deductions but failed "
        "to reverse them or deactivate the unauthorized service. The Complainant also "
        "sent a formal written email complaint, but received only an automated "
        "acknowledgment. Having exhausted all available avenues of self-help, the "
        "Complainant is constrained to approach this Hon'ble Commission."
    ),
    'defective_product': (
        "That the Complainant immediately upon discovering the defect in the product "
        "contacted the Opposite Party's customer care and registered a formal complaint. "
        "The Complainant provided photographs and description of the defect and "
        "requested either a replacement of the product or a full refund. Despite "
        "multiple follow-up calls and emails over a period of several weeks, the "
        "Opposite Party either denied the defect, delayed the resolution, or offered "
        "an inadequate partial remedy. The Opposite Party's technical team inspected "
        "the product but failed to acknowledge the manufacturing defect. The Complainant "
        "has maintained a complete record of all communications with the Opposite Party."
    ),
    'service_delay': (
        "That upon the expiry of the committed delivery/service timeline, the Complainant "
        "immediately contacted the Opposite Party's customer support team to inquire "
        "about the delay. The Opposite Party's representatives offered repeated "
        "assurances of imminent resolution without providing any concrete timeline. "
        "The Complainant followed up on at least five (5) separate occasions over "
        "phone and email. The Opposite Party failed to provide any satisfactory "
        "explanation for the delay or any compensatory arrangement. Upon eventually "
        "seeking a refund due to the unacceptable delay, the Opposite Party refused "
        "or further delayed the refund processing, compounding the deficiency."
    ),
    'refund_not_processed': (
        "That the Complainant, upon becoming entitled to a refund, submitted a formal "
        "refund request through the Opposite Party's official channel. The Opposite "
        "Party initially acknowledged the request and provided an estimated refund "
        "timeline. However, the refund was not credited within the promised period. "
        "The Complainant then contacted the Opposite Party's customer care on multiple "
        "occasions — each time being told the refund was 'in process' or 'under review'. "
        "The Complainant also escalated the matter via email to the Opposite Party's "
        "grievance redressal officer. Despite the passage of a reasonable period "
        "well beyond the Opposite Party's own stated policy, the refund has not "
        "been processed, leaving the Complainant with no option but to file this complaint."
    ),
    'misleading_advertisement': (
        "That upon discovering that the product/service received was materially "
        "different from what was advertised, the Complainant immediately contacted "
        "the Opposite Party's customer care and brought the discrepancy to their "
        "attention. The Complainant provided specific details of the misleading "
        "advertisement and the actual product/service received. The Opposite Party's "
        "representatives were evasive and offered no satisfactory explanation for "
        "the discrepancy. The Complainant requested either delivery of the promised "
        "product/service or a full refund, but both requests were refused or ignored. "
        "The Complainant has preserved copies of the misleading advertisement "
        "and all subsequent communications."
    ),
    'unfair_trade_practice': (
        "That upon identifying the unfair trade practice adopted by the Opposite Party, "
        "the Complainant formally brought the same to the attention of the Opposite "
        "Party's customer care and grievance redressal team. The Complainant clearly "
        "articulated the nature of the unfair practice and the loss caused. The "
        "Opposite Party's representatives failed to acknowledge any wrongdoing or "
        "offer any meaningful remedy. The Complainant followed up on multiple "
        "occasions over phone and email, maintaining records of all communications. "
        "Having received no satisfactory response, the Complainant is constrained "
        "to approach this Hon'ble Commission for redress."
    ),
    'deficiency_in_service': (
        "That upon experiencing the deficiency in the Opposite Party's service, "
        "the Complainant contacted the Opposite Party's customer care and formally "
        "registered a service complaint. The Complainant clearly described the "
        "nature of the deficiency and the loss suffered. The Opposite Party "
        "acknowledged receipt of the complaint but failed to take prompt or "
        "adequate remedial action. Multiple follow-up calls and emails by the "
        "Complainant elicited only token responses and no substantive resolution. "
        "The Complainant also escalated the matter to senior management of the "
        "Opposite Party, but received no meaningful response."
    ),
    'other': (
        "That the Complainant made all reasonable efforts to resolve the dispute "
        "directly with the Opposite Party before approaching this Hon'ble Commission. "
        "The Complainant contacted the Opposite Party's customer care on multiple "
        "occasions through various channels including phone, email, and the "
        "Opposite Party's official app. Despite such efforts, the Opposite Party "
        "failed to offer any satisfactory resolution. The Complainant has maintained "
        "a complete record of all communications with the Opposite Party."
    ),
}


def create_styles():
    styles = getSampleStyleSheet()
    defs = [
        ('CourtHeader',    dict(fontSize=12, fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6,  leading=16)),
        ('SectionHeading', dict(fontSize=11, fontName='Helvetica-Bold', alignment=TA_LEFT,   spaceBefore=14, spaceAfter=6)),
        ('BodyText',       dict(fontSize=10, fontName='Helvetica',      alignment=TA_JUSTIFY, spaceBefore=4, spaceAfter=4,  leading=15)),
        ('CenterText',     dict(fontSize=10, fontName='Helvetica',      alignment=TA_CENTER,  spaceBefore=4, spaceAfter=4)),
        ('BoldCenter',     dict(fontSize=11, fontName='Helvetica-Bold', alignment=TA_CENTER,  spaceBefore=6, spaceAfter=6)),
        ('SmallText',      dict(fontSize=9,  fontName='Helvetica',      alignment=TA_LEFT,    spaceBefore=2, spaceAfter=2,  leading=13)),
        ('IndentText',     dict(fontSize=10, fontName='Helvetica',      alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=2,  leading=15, leftIndent=20)),
    ]
    for name, kwargs in defs:
        if name not in styles:
            styles.add(ParagraphStyle(name=name, **kwargs))
    return styles


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.drawCentredString(A4[0] / 2, 0.4 * inch, f"- {canvas.getPageNumber()} -")
    canvas.restoreState()


def fmt(template, **kwargs):
    """Safe format — replaces known keys, ignores missing ones."""
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def generate_form_i(case_data):
    # ── Complainant details ──────────────────────────────────────────────────
    complainant_name    = blank(case_data.get('complainant_name'), 25)
    father_name         = blank(case_data.get('father_name'), 25)
    age                 = blank(case_data.get('age'), 4)
    complainant_address = case_data.get('complainant_address', 'Lucknow, Uttar Pradesh')

    # ── Opposite party — supports both old and new field names ──────────────
    opposite_party = blank(case_data.get('company_name') or case_data.get('opposite_party'), 25)
    op_address     = case_data.get('op_address', 'Corporate Office, New Delhi - 110001')

    # ── Issue type ───────────────────────────────────────────────────────────
    issue_type  = case_data.get('issue_type') or 'unauthorized_charge'
    issue_label = ISSUE_LABELS.get(issue_type, 'Consumer Complaint')

    # ── Section — supports both old and new field names ─────────────────────
    section = (case_data.get('legal_section') or case_data.get('section') or SECTION_MAP.get(issue_type, '2(47)'))
    section = str(section).replace('Section ', '').strip()

    # ── Amount ───────────────────────────────────────────────────────────────
    try:
        amount = int(case_data.get('amount', 0) or 0)
    except (ValueError, TypeError):
        amount = 0

    # ── Relief ───────────────────────────────────────────────────────────────
    relief_sought = case_data.get('relief_sought') or case_data.get('relief') or 'refund'

    # ── Evidence flags ───────────────────────────────────────────────────────
    has_sms  = case_data.get('has_sms_proof', True)
    has_bill = case_data.get('has_billing_statement', True)

    # ── Calculated fields ────────────────────────────────────────────────────
    months         = 6 if (amount > 0 and issue_type == 'unauthorized_charge') else 1
    total_deducted = amount * months
    compensation   = 5000
    total_relief   = total_deducted + compensation
    today          = datetime.now().strftime("%d/%m/%Y")
    day            = datetime.now().strftime("%d")
    month_year     = datetime.now().strftime("%B %Y")
    year           = datetime.now().strftime("%Y")

    # Template variables for text substitution
    tv = dict(
        amount=amount, months=months, total_deducted=total_deducted,
        compensation=compensation, total_relief=total_relief,
        opposite_party=opposite_party, section=section,
        issue_label=issue_label, month_year=month_year,
        relief_sought=relief_sought,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.0*inch, leftMargin=1.0*inch,
        topMargin=1.0*inch,   bottomMargin=0.75*inch,
        title="Form I - Consumer Complaint"
    )
    styles = create_styles()
    story  = []

    # ════════════════════════════════════════════════════════════════
    # COURT HEADER
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph(
        "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL<br/>COMMISSION AT LUCKNOW",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"IN RE: COMPLAINT NO. ________ OF {year}", styles['CenterText']))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph("IN THE MATTER OF:", styles['CenterText']))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"<b>{complainant_name}</b>", styles['CenterText']))
    story.append(Paragraph(f"S/o {father_name}, Age: {age} years", styles['CenterText']))
    story.append(Paragraph(f"R/o {complainant_address}", styles['CenterText']))
    story.append(Paragraph("<b>....Complainant</b>", styles['CenterText']))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph("<b>Versus</b>", styles['BoldCenter']))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(f"<b>{opposite_party}</b>", styles['CenterText']))
    story.append(Paragraph(f"{op_address}", styles['CenterText']))
    story.append(Paragraph("<b>....Opposite Party</b>", styles['CenterText']))
    story.append(Spacer(1, 0.1*inch))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.black))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        "COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(
        f"(Complaint regarding: <b>{issue_label}</b>)",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph("<b>MOST RESPECTFULLY SHOWETH:</b>", styles['CenterText']))
    story.append(Spacer(1, 0.1*inch))

    # ════════════════════════════════════════════════════════════════
    # SECTION 1: INTRODUCTION
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(1) INTRODUCTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"The Complainant, <b>{complainant_name}</b>, S/o <b>{father_name}</b>, aged "
        f"<b>{age} years</b>, is a resident of <b>{complainant_address}</b> and is a "
        f"bonafide consumer of the Opposite Party, <b>{opposite_party}</b>, within the "
        f"meaning of Section 2(7) of the Consumer Protection Act, 2019.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        f"The Opposite Party, <b>{opposite_party}</b>, is a company/firm engaged in "
        f"trade and commerce, operating across India with its office at "
        f"<b>{op_address}</b>, and is an 'opposite party' within the meaning of the "
        f"Consumer Protection Act, 2019.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        fmt(INTRO_TEXT.get(issue_type, INTRO_TEXT['other']), **tv),
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 2: TRANSACTION / FACTS
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(2) FACTS OF THE TRANSACTION", styles['SectionHeading']))
    story.append(Paragraph(
        fmt(TRANSACTION_TEXT.get(issue_type, TRANSACTION_TEXT['other']), **tv),
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 3: DEFECT / DEFICIENCY
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(3) NATURE OF DEFECT / DEFICIENCY IN SERVICE", styles['SectionHeading']))
    story.append(Paragraph(
        fmt(DEFICIENCY_TEXT.get(issue_type, DEFICIENCY_TEXT['other']), **tv),
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 4: ATTEMPTS AT RECTIFICATION
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(4) ATTEMPTS AT RECTIFICATION", styles['SectionHeading']))
    story.append(Paragraph(
        fmt(RECTIFICATION_TEXT.get(issue_type, RECTIFICATION_TEXT['other']), **tv),
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 5: STATUTORY PROVISIONS VIOLATED
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(5) STATUTORY PROVISIONS VIOLATED", styles['SectionHeading']))
    story.append(Paragraph(
        "The acts and omissions of the Opposite Party are in violation of the following "
        "provisions of the Consumer Protection Act, 2019:",
        styles['BodyText']
    ))
    applicable = APPLICABLE_SECTIONS.get(issue_type, APPLICABLE_SECTIONS['other'])
    for sec_num, sec_desc in applicable:
        story.append(Paragraph(
            f"&nbsp;&nbsp;&nbsp;● <b>Section {sec_num}</b> — {sec_desc}",
            styles['BodyText']
        ))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        "The Complainant is entitled to protection under all of the above provisions "
        "and this Hon'ble Commission is competent to grant relief in respect thereof.",
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 6: EVIDENCE
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(6) LIST OF DOCUMENTS / EVIDENCE", styles['SectionHeading']))
    story.append(Paragraph(
        "The Complainant shall rely upon the following documents in support of this "
        "complaint, true copies of which are annexed hereto:",
        styles['BodyText']
    ))
    ann_idx = 'A'
    if has_sms:
        story.append(Paragraph(
            f"&nbsp;&nbsp;&nbsp;<b>Annexure-{ann_idx}:</b> "
            f"SMS/notification messages, screenshots evidencing the complaint (True Copy)",
            styles['BodyText']
        ))
        ann_idx = chr(ord(ann_idx) + 1)
    if has_bill:
        story.append(Paragraph(
            f"&nbsp;&nbsp;&nbsp;<b>Annexure-{ann_idx}:</b> "
            f"Billing statements, payment receipts, transaction records (True Copy)",
            styles['BodyText']
        ))
        ann_idx = chr(ord(ann_idx) + 1)
    story.append(Paragraph(
        f"&nbsp;&nbsp;&nbsp;<b>Annexure-{ann_idx}:</b> "
        f"Copy of Aadhaar Card — Identity Proof of Complainant (True Copy)",
        styles['BodyText']
    ))
    ann_idx = chr(ord(ann_idx) + 1)
    story.append(Paragraph(
        f"&nbsp;&nbsp;&nbsp;<b>Annexure-{ann_idx}:</b> "
        f"Copies of all correspondence with Opposite Party including emails, chat transcripts (True Copy)",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        "The Complainant reserves the right to produce additional documents and evidence "
        "at the time of hearing as may be required.",
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 7: JURISDICTION
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(7) JURISDICTION", styles['SectionHeading']))
    story.append(Paragraph(
        f"<b>Pecuniary Jurisdiction:</b> The total amount involved in the present "
        f"complaint is <b>Rs. {total_relief}/-</b> (Rupees {total_relief} only), "
        f"which is well within the pecuniary jurisdiction of this Hon'ble District "
        f"Consumer Disputes Redressal Commission. As per Section 34 of the Consumer "
        f"Protection Act, 2019, the District Commission has jurisdiction to entertain "
        f"complaints where the value of goods or services paid as consideration does "
        f"not exceed Rupees One Crore.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.04*inch))
    story.append(Paragraph(
        f"<b>Territorial Jurisdiction:</b> The Complainant is a resident of Lucknow "
        f"and the cause of action partly arose within the territorial limits of Lucknow. "
        f"This Hon'ble Commission therefore has territorial jurisdiction to try and "
        f"decide this complaint as per Section 34(2) of the Consumer Protection Act, 2019.",
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 8: LIMITATION
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(8) LIMITATION", styles['SectionHeading']))
    story.append(Paragraph(
        "That the present complaint is being filed within the period of two years "
        "prescribed under Section 69 of the Consumer Protection Act, 2019 from the "
        "date on which the cause of action arose. The cause of action is of a "
        "continuing nature as the Opposite Party's unlawful conduct and/or failure "
        "to remedy the deficiency is ongoing. The complaint is therefore well within "
        "the period of limitation and is maintainable in law.",
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 9: RELIEF CLAIMED
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(9) RELIEF CLAIMED", styles['SectionHeading']))
    story.append(Paragraph(
        "In light of the above stated facts and circumstances, and in the interest "
        "of justice, the Complainant most respectfully claims the following reliefs "
        "from this Hon'ble Commission:",
        styles['BodyText']
    ))
    if amount > 0:
        relief_label = 'Refund' if 'refund' in relief_sought.lower() else 'Restitution'
        story.append(Paragraph(
            f"(a) <b>{relief_label} of Rs. {total_deducted}/-</b> "
            f"(Rupees {total_deducted} only) being the principal amount paid/deducted "
            f"by the Complainant, with interest at the rate of 18% per annum from "
            f"the date of payment till the date of actual realization;",
            styles['BodyText']
        ))
    else:
        story.append(Paragraph(
            f"(a) <b>Appropriate relief</b> including {relief_sought} for the "
            f"deficiency/unfair practice committed by the Opposite Party, with "
            f"interest at the rate of 18% per annum;",
            styles['BodyText']
        ))
    story.append(Paragraph(
        f"(b) <b>Compensation of Rs. {compensation}/-</b> (Rupees Five Thousand only) "
        f"for mental agony, harassment, loss of time, and financial inconvenience "
        f"caused to the Complainant by the negligent and willful conduct of the "
        f"Opposite Party under Section 42 of the Consumer Protection Act, 2019;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(c) <b>Total relief claimed: Rs. {total_relief}/-</b> "
        f"(Rupees {total_relief} only);",
        styles['BodyText']
    ))
    story.append(Paragraph(
        "(d) Cost of this complaint proceedings;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        "(e) Any other relief that this Hon'ble Commission deems fit, just, and "
        "proper in the facts and circumstances of the present case.",
        styles['BodyText']
    ))

    # ════════════════════════════════════════════════════════════════
    # SECTION 10: PRAYER CLAUSE
    # ════════════════════════════════════════════════════════════════
    story.append(Paragraph("(10) PRAYER CLAUSE", styles['SectionHeading']))
    story.append(Paragraph(
        "In light of the foregoing, it is most respectfully prayed that this "
        "Hon'ble District Consumer Disputes Redressal Commission may graciously "
        "be pleased to:",
        styles['BodyText']
    ))
    if amount > 0:
        story.append(Paragraph(
            f"(i) Direct the Opposite Party to refund/pay Rs. {total_deducted}/- "
            f"(Rupees {total_deducted} only) to the Complainant, being the principal "
            f"amount, with interest at 18% per annum from the date of cause of action "
            f"till actual payment;",
            styles['BodyText']
        ))
    else:
        story.append(Paragraph(
            f"(i) Direct the Opposite Party to provide the appropriate {relief_sought} "
            f"as entitled to the Complainant, with interest at 18% per annum;",
            styles['BodyText']
        ))
    story.append(Paragraph(
        f"(ii) Direct the Opposite Party to pay compensation of Rs. {compensation}/- "
        f"(Rupees Five Thousand only) to the Complainant for mental agony, "
        f"harassment, and financial loss;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        f"(iii) Direct the Opposite Party to immediately cease and desist from the "
        f"{issue_label.lower()} and ensure no recurrence;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        "(iv) Award cost of this complaint proceeding to the Complainant;",
        styles['BodyText']
    ))
    story.append(Paragraph(
        "(v) Pass such other and further orders as this Hon'ble Commission may "
        "deem fit and proper in the facts and circumstances of this case, and "
        "in the interest of justice.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(f"Place: Lucknow", styles['BodyText']))
    story.append(Paragraph(f"Dated: {today}", styles['BodyText']))
    story.append(Spacer(1, 0.35*inch))
    story.append(Paragraph(
        f"_______________________<br/><b>{complainant_name}</b><br/>Complainant",
        styles['CenterText']
    ))

    # ════════════════════════════════════════════════════════════════
    # VERIFICATION
    # ════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("<b>VERIFICATION</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"I, <b>{complainant_name}</b>, S/o <b>{father_name}</b>, aged <b>{age} years</b>, "
        f"resident of <b>{complainant_address}</b>, the complainant above named, do hereby "
        f"solemnly verify that the contents of my above complaint in paragraphs 1 to 10 "
        f"are true and correct to the best of my knowledge and belief, no part of it is "
        f"false and nothing material has been concealed therein.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        f"Verified at <b>Lucknow</b> this <b>{day}</b> day of <b>{month_year}</b>.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.35*inch))
    story.append(Paragraph(
        f"_______________________<br/><b>{complainant_name}</b><br/>Complainant/Deponent",
        styles['CenterText']
    ))

    # ════════════════════════════════════════════════════════════════
    # AFFIDAVIT
    # ════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("AFFIDAVIT IN SUPPORT OF THE COMPLAINT", styles['CourtHeader']))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        "BEFORE THE HON'BLE DISTRICT CONSUMER DISPUTES REDRESSAL COMMISSION AT LUCKNOW",
        styles['CourtHeader']
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(f"IN RE: COMPLAINT NO. ________ OF {year}", styles['CenterText']))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(f"<b>{complainant_name}</b> ....Complainant", styles['CenterText']))
    story.append(Paragraph("<b>Versus</b>", styles['CenterText']))
    story.append(Paragraph(f"<b>{opposite_party}</b> ....Opposite Party", styles['CenterText']))
    story.append(Spacer(1, 0.1*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>AFFIDAVIT</b>", styles['BoldCenter']))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        f"I, <b>{complainant_name}</b>, S/o <b>{father_name}</b>, aged <b>{age} years</b>, "
        f"resident of <b>{complainant_address}</b>, do hereby solemnly affirm and state "
        f"on oath as under:",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(Paragraph(
        "(1) That I am the Complainant in the above case and am thoroughly conversant "
        "with the facts and circumstances of the present case. I am competent to swear "
        "this affidavit.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(
        "(2) That I have filed the above consumer complaint before this Hon'ble Commission "
        "against the Opposite Party and the contents of the said complaint are true and "
        "correct to the best of my knowledge and belief. The contents of the complaint "
        "may be read as an integral part of this affidavit.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(
        "(3) That the documents annexed to the complaint as Annexures are true copies "
        "of the originals which are in my possession and shall be produced before this "
        "Hon'ble Commission as and when required.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(
        "(4) That I have not filed any other complaint or proceeding in respect of the "
        "same subject matter before any other court, tribunal, or consumer forum.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.35*inch))
    story.append(Paragraph(
        f"_______________________<br/><b>{complainant_name}</b><br/>Deponent",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>VERIFICATION OF AFFIDAVIT</b>", styles['SectionHeading']))
    story.append(Paragraph(
        f"I, the above named deponent, do hereby verify that the contents of this "
        f"affidavit in paragraphs 1 to 4 above are true and correct to the best of "
        f"my knowledge and belief. Nothing is false and nothing material has been "
        f"concealed therein.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        f"Verified at <b>Lucknow</b> this <b>{day}</b> day of <b>{month_year}</b>.",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.35*inch))
    story.append(Paragraph(
        f"_______________________<br/><b>{complainant_name}</b><br/>Deponent",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        "<i>Note: This affidavit must be sworn before a Notary Public or Oath Commissioner "
        "appointed by the High Court before filing. Please carry original documents for "
        "verification at the time of notarization.</i>",
        styles['SmallText']
    ))

    # ════════════════════════════════════════════════════════════════
    # LIST OF ANNEXURES
    # ════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("LIST OF ANNEXURES", styles['CourtHeader']))
    story.append(Spacer(1, 0.06*inch))
    story.append(Paragraph(
        f"In the matter of <b>{complainant_name}</b> vs <b>{opposite_party}</b> "
        f"— Complaint No. ________ of {year}",
        styles['CenterText']
    ))
    story.append(Spacer(1, 0.08*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.black))
    story.append(Spacer(1, 0.1*inch))
    ann_idx = 'A'
    if has_sms:
        story.append(Paragraph(
            f"<b>Annexure-{ann_idx}:</b> SMS/notification messages and screenshots "
            f"evidencing the consumer complaint (True Copy)",
            styles['BodyText']
        ))
        ann_idx = chr(ord(ann_idx) + 1)
    if has_bill:
        story.append(Paragraph(
            f"<b>Annexure-{ann_idx}:</b> Billing statements, payment receipts, and/or "
            f"transaction records showing the amount involved (True Copy)",
            styles['BodyText']
        ))
        ann_idx = chr(ord(ann_idx) + 1)
    story.append(Paragraph(
        f"<b>Annexure-{ann_idx}:</b> Copy of Aadhaar Card — Identity and Address Proof "
        f"of Complainant (True Copy)",
        styles['BodyText']
    ))
    ann_idx = chr(ord(ann_idx) + 1)
    story.append(Paragraph(
        f"<b>Annexure-{ann_idx}:</b> Copies of all communications (emails, chat, calls) "
        f"between Complainant and Opposite Party (True Copy)",
        styles['BodyText']
    ))
    story.append(Spacer(1, 0.25*inch))
    story.append(Paragraph(
        "<i>All annexures are true copies of originals. Originals will be produced "
        "at the time of hearing as required by this Hon'ble Commission.</i>",
        styles['SmallText']
    ))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    return buffer


def lambda_handler(event, context):
    print("pdf-generator triggered")
    print("Event received:", json.dumps(event))

    try:
        body      = json.loads(event.get('body', '{}'))
        case_data = body.get('case_data', {})
        print('CASE DATA RECEIVED:', json.dumps(case_data))

        # Support both old field names (opposite_party, section) and
        # new generalized field names (company_name, legal_section)
        if 'company_name' in case_data and 'opposite_party' not in case_data:
            case_data['opposite_party'] = case_data['company_name']
        if 'legal_section' in case_data and 'section' not in case_data:
            case_data['section'] = case_data['legal_section']

        pdf_buffer = generate_form_i(case_data)

        file_name = f"complaints/form-i-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=pdf_buffer.getvalue(),
            ContentType='application/pdf'
        )

        pdf_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': file_name},
            ExpiresIn=3600
        )

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "pdf_url":    pdf_url,
                "file_name":  file_name,
                "message":    "Form I generated successfully"
            })
        }

    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }