import json
import boto3
import re

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_nova(transcription):
    prompt = f"""You are a legal AI assistant for Indian consumer complaints.
Analyze this Hindi consumer complaint and return ONLY a JSON object. No explanation, no markdown, no extra text. Just the raw JSON.

Complaint: {transcription}

You MUST choose issue_type from EXACTLY one of these values:
- "unauthorized_charge" = company deducted money without permission (e.g. Airtel cutting balance)
- "defective_product" = product received was broken or faulty (e.g. Amazon sent damaged phone)
- "service_delay" = delivery or service was very late (e.g. Swiggy order 2 hours late)
- "refund_not_processed" = refund not given after return or cancellation (e.g. Flipkart kept money)
- "misleading_advertisement" = false promises made in advertisement
- "other" = anything else

You MUST choose section from EXACTLY one of these:
- "2(47)" = for unauthorized_charge or misleading_advertisement
- "2(9)" = for defective_product
- "2(11)" = for service_delay or refund_not_processed

Examples:
- "एयरटेल ने ₹299 काटे" → issue_type: "unauthorized_charge", opposite_party: "Airtel"
- "अमेज़ॉन ने खराब मोबाइल भेजा" → issue_type: "defective_product", opposite_party: "Amazon"
- "स्विगी का ऑर्डर लेट" → issue_type: "service_delay", opposite_party: "Swiggy"
- "फ्लिपकार्ट ने रिफंड नहीं दिया" → issue_type: "refund_not_processed", opposite_party: "Flipkart"

Return JSON with EXACTLY these fields and nothing else:
{{
  "issue_type": "<pick from the list above>",
  "section": "<2(47) or 2(9) or 2(11)>",
  "relief_sought": "<refund or replacement or compensation>",
  "opposite_party": "<company name from the complaint>",
  "amount": <number only, no rupee symbol, or null if not mentioned>,
  "confidence": "<high or medium or low>"
}}"""

    response = bedrock.invoke_model(
        modelId='amazon.nova-lite-v1:0',
        body=json.dumps({
            "messages": [
                {"role": "user", "content": [{"text": prompt}]}
            ]
        })
    )

    response_body = json.loads(response['body'].read())
    nova_text = response_body['output']['message']['content'][0]['text']
    return nova_text


def parse_json(text):
    # Strip markdown code blocks if Nova wraps in ```json
    text = re.sub(r'```json|```', '', text).strip()
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError("No valid JSON found in response")


def lambda_handler(event, context):
    print("claude-analyzer triggered")
    print("Event:", json.dumps(event))

    body = json.loads(event.get('body', '{}'))
    transcription = body.get('transcription', '')

    if not transcription:
        return {
            "statusCode": 400,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "No transcription provided"})
        }

    for attempt in range(1, 4):
        try:
            print(f"Attempt {attempt}: Calling Nova...")
            nova_text = call_nova(transcription)
            print(f"Nova raw response: {nova_text}")

            legal_analysis = parse_json(nova_text)
            print("Parsed:", legal_analysis)

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({
                    "transcription": transcription,
                    "legal_analysis": legal_analysis
                })
            }

        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt == 3:
                return {
                    "statusCode": 500,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({
                        "error": "Failed after 3 attempts",
                        "details": str(e)
                    })
                }

