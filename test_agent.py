# test_agent.py
import json
from compliance_agent import ComplianceAgent

def test_full_workflow():
    agent = ComplianceAgent()
    
    # Step 1: Load and parse protocol
    print("=" * 60)
    print("STEP 1: Parsing Compliance Protocol")
    print("=" * 60)
    
    with open('sample_data\\florida_protocol.txt', 'r', encoding='utf-8') as f:
        protocol_text = f.read()
    
    indicators = agent.parse_compliance_document(protocol_text)
    print(f"\n✓ Extracted {len(indicators['indicators'])} indicators\n")
    
    for ind in indicators['indicators']:
        print(f"Indicator {ind['number']}: {ind['title']}")
    
    # Step 2: Load evidence files
    print("\n" + "=" * 60)
    print("STEP 2: Loading Evidence Files")
    print("=" * 60)
    
    with open('sample_data\\sample_files.json', 'r', encoding='utf-8') as f:
        files = json.load(f)
    
    print(f"\n✓ Found {len(files)} evidence files\n")
    
    # Step 3: Analyze gaps
    print("=" * 60)
    print("STEP 3: Analyzing Compliance Gaps")
    print("=" * 60)
    
    analysis = agent.analyze_evidence(indicators, files)
    
    print("\nCompliance Status Summary:\n")
    for ind_key, data in analysis.items():
        status_emoji = {
            "Complete": "✅",
            "Partial": "⚠️",
            "Missing": "❌"
        }
        emoji = status_emoji.get(data['status'], '❓')
        print(f"{emoji} {ind_key.upper()}: {data['status']} ({data['confidence']}% confident)")
        print(f"   Found: {len(data['evidence_found'])} files")
        if data['evidence_missing']:
            print(f"   Missing: {', '.join(data['evidence_missing'][:2])}")
        print()
    
    # Step 4: Generate narrative for first indicator
    print("=" * 60)
    print("STEP 4: Generating Compliance Narrative")
    print("=" * 60)
    
    first_indicator = indicators['indicators'][0]
    first_analysis = analysis['indicator_1']
    
    narrative = agent.generate_narrative(first_indicator, first_analysis)
    
    print(f"\nNarrative for Indicator {first_indicator['number']}:\n")
    print(narrative)
    
    print("\n" + "=" * 60)
    print("✓ TEST COMPLETE - All functions working!")
    print("=" * 60)

if __name__ == "__main__":
    test_full_workflow()