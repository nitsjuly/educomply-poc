# compliance_agent.py
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ComplianceAgent:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in .env file!")
        self.client = Anthropic(api_key=api_key)
    
    def parse_compliance_document(self, text_content):
        """
        Extract compliance indicators from PDF text
        """
        prompt = f"""You are analyzing a Florida special education compliance monitoring protocol.

Extract the TOP 4 compliance indicators in this EXACT JSON format:

{{
    "indicators": [
        {{
            "number": "1",
            "title": "Brief title",
            "requirement": "What must be done",
            "evidence_needed": ["Evidence type 1", "Evidence type 2"],
            "citation": "Regulatory citation"
        }}
    ]
}}

Document text:
{text_content[:8000]}

Return ONLY valid JSON. No markdown, no explanation."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        
        # Clean up potential markdown
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        
        return json.loads(response_text.strip())
    
    def analyze_evidence(self, indicators, file_list):
        """
        Analyze what evidence exists vs. what's missing
        """
        prompt = f"""You are analyzing special education compliance evidence.

REQUIREMENTS:
{json.dumps(indicators, indent=2)}

AVAILABLE FILES:
{json.dumps(file_list, indent=2)}

For each indicator, determine:
1. Status: "Complete", "Partial", or "Missing"
2. Which files satisfy the requirement
3. What's still needed
4. Confidence (0-100)

Return JSON:
{{
    "indicator_1": {{
        "status": "Complete|Partial|Missing",
        "evidence_found": ["filename1.pdf"],
        "evidence_missing": ["Missing doc type"],
        "confidence": 85,
        "reasoning": "Brief explanation"
    }}
}}

Return ONLY valid JSON."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        
        return json.loads(response_text.strip())
    
    def generate_narrative(self, indicator, analysis):
        """
        Generate compliance narrative for one indicator
        """
        prompt = f"""Write a compliance narrative for this indicator.

INDICATOR:
{json.dumps(indicator, indent=2)}

ANALYSIS:
{json.dumps(analysis, indent=2)}

Write a professional 2-3 paragraph compliance narrative that:
1. States the requirement with regulatory citation
2. Describes evidence of compliance
3. Addresses gaps if any exist

Use formal audit language. Return plain text (no markdown)."""

        message = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text


# Test function
if __name__ == "__main__":
    agent = ComplianceAgent()
    
    # Test with sample text
    sample_text = """
    Florida IDEA Part B Monitoring Protocol
    
    Indicator 1: Child Find and Evaluation Timelines
    Initial evaluations must be completed within 60 calendar days of receiving 
    parental consent. Districts must maintain documentation of:
    - Parent consent forms with dates
    - Completed evaluation reports
    - Timeline tracking systems
    
    Indicator 2: IEP Development and Implementation
    IEPs must be developed with required components per 34 CFR 300.320.
    Evidence includes completed IEPs, meeting notices, parent participation documentation.
    """
    
    print("Testing compliance agent...")
    result = agent.parse_compliance_document(sample_text)
    print(json.dumps(result, indent=2))