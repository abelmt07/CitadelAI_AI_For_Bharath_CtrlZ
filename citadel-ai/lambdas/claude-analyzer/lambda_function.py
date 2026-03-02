import json
import boto3
import re

# Connect to AWS Bedrock (this is how we talk to Claude 3)
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

def call_claude(transcription, attempt=1):
    """
    Sends the transcription to Claude 3 and gets back legal analysis.
    We try up to 3 times in case Claude returns bad JSON.
    """
    
    # This is the prompt we send to Claude
    prompt = f"""You are a legal AI assistant. Analyze this Hindi consumer complaint and return JSON only. No explanation, no extra text, just the JSON object.

Complaint: {transcription}

Consumer Protection Act sections to use:
- Section 2(47): Unfair trade practice
- Section 35: Filing complaint  
- Section 42: Compensation

Return JSON with exactly these fields:
{{
  "issue_type": "unfair_trade_practice",
  "section": "2(47)",
  "relief_sought": "refund + compensation",
  "opposite_party": "Airtel",
  "amount": 299,
  "confidence": "high"
}}"""

    # Send the prompt to Claude 3 on Bedrock
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })
    )
    
    # Extract the text from Claude's response
    response_body = json.loads(response['body'].read())
    claude_text = response_body['content'][0]['text']
    
    return claude_text

def parse_json_from_claude(claude_text):
    """
    Claude sometimes adds extra text around the JSON.
    This function finds and extracts just the JSON part.
    """
    # Try to find JSON pattern in the response
    json_match = re.search(r'\{.*\}', claude_text, re.DOTALL)
    if json_match:
        return json.loads(json_match.group())
    raise ValueError("No valid JSON found in Claude response")

def lambda_handler(event, context):
    """
    CITADEL AI - Claude Analyzer
    Input:  {"transcription": "hindi text here"}
    Output: Legal analysis as structured JSON
    """
    print("claude-analyzer triggered")
    print("Event received:", json.dumps(event))
    
    # Get the transcription from the input
    body = json.loads(event.get('body', '{}'))
    transcription = body.get('transcription', '')
    
    if not transcription:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "No transcription provided"})
        }
    
    # Try up to 3 times to get valid JSON from Claude
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Attempt {attempt}: Calling Claude...")
            claude_text = call_claude(transcription, attempt)
            print(f"Claude raw response: {claude_text}")
            
            # Parse the JSON from Claude's response
            legal_analysis = parse_json_from_claude(claude_text)
            print("Successfully parsed JSON:", legal_analysis)
            
            # Return the structured data
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "transcription": transcription,
                    "legal_analysis": legal_analysis
                })
            }
            
        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt == max_attempts:
                # All 3 attempts failed
                return {
                    "statusCode": 500,
                    "body": json.dumps({
                        "error": "Failed to analyze complaint after 3 attempts",
                        "details": str(e)
                    })
                }
