# app.py
import streamlit as st
import json
import os
from compliance_agent import ComplianceAgent

# Page config
st.set_page_config(
    page_title="EduComply POC",
    page_icon="🎓",
    layout="wide"
)

# Initialize session state
if 'indicators' not in st.session_state:
    st.session_state.indicators = None
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'agent' not in st.session_state:
    st.session_state.agent = ComplianceAgent()

# Header
st.title("🎓 EduComply - AI Compliance Assistant")
st.markdown("*Automate special education compliance monitoring*")

# Add metrics if analysis exists
if st.session_state.analysis:
    # Calculate summary metrics
    total_indicators = len(st.session_state.analysis)
    complete = sum(1 for d in st.session_state.analysis.values() if d['status'] == 'Complete')
    at_risk = sum(1 for d in st.session_state.analysis.values() if d['status'] == 'Partial')
    missing = sum(1 for d in st.session_state.analysis.values() if d['status'] == 'Missing')
    
    avg_confidence = sum(d['confidence'] for d in st.session_state.analysis.values()) / total_indicators
    
    # Display metrics
    met1, met2, met3, met4 = st.columns(4)
    met1.metric("Total Indicators", total_indicators)
    met2.metric("✅ Complete", complete)
    met3.metric("⚠️ At Risk", at_risk)
    met4.metric("Avg Confidence", f"{avg_confidence:.0f}%")

st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📋 How It Works")
    st.markdown("""
    1. **Upload** compliance protocol
    2. **AI extracts** requirements
    3. **Map** evidence files
    4. **AI analyzes** gaps
    5. **Generate** narratives
    """)
    
    st.markdown("---")
    st.info("**POC Demo** - Built in 6 hours")

# Main workflow
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Step 1: Upload Protocol")
    
    # Option to use sample or upload
    data_source = st.radio(
        "Choose data source:",
        ["Use Sample Data", "Upload Your Own"]
    )
    
    if data_source == "Use Sample Data":
        if st.button("Load Sample Florida Protocol", type="primary"):
            with st.spinner("Loading sample data..."):
                # Load sample protocol
                with open('sample_data\\florida_protocol.txt', 'r', encoding='utf-8') as f:
                    protocol_text = f.read()
                
                # Parse indicators
                st.session_state.indicators = st.session_state.agent.parse_compliance_document(protocol_text)
                
                st.success("✓ Sample protocol loaded!")
                st.rerun()
    
    else:
        uploaded_file = st.file_uploader(
            "Upload compliance protocol (TXT or PDF)",
            type=['txt', 'pdf']
        )
        
        if uploaded_file and st.button("Parse Document", type="primary"):
            with st.spinner("Parsing document with AI..."):
                # Read file
                if uploaded_file.type == "text/plain":
                    protocol_text = uploaded_file.read().decode('utf-8')
                else:
                    # For PDF, use PyPDF2
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    protocol_text = ""
                    for page in pdf_reader.pages:
                        protocol_text += page.extract_text()
                
                # Parse with AI
                st.session_state.indicators = st.session_state.agent.parse_compliance_document(protocol_text)
                
                st.success("✓ Document parsed!")
                st.rerun()
    
    # Show extracted indicators
    if st.session_state.indicators:
        st.markdown("---")
        st.subheader("✓ Extracted Indicators")
        
        for ind in st.session_state.indicators['indicators']:
            with st.expander(f"**Indicator {ind['number']}: {ind['title']}**"):
                st.write(f"**Requirement:** {ind['requirement']}")
                st.write(f"**Citation:** {ind['citation']}")
                st.write("**Evidence Needed:**")
                for ev in ind['evidence_needed']:
                    st.write(f"  • {ev}")

with col2:
    st.header("📁 Step 2: Map Evidence")
    
    if st.session_state.indicators:
        # Option to use sample files or upload
        evidence_source = st.radio(
            "Evidence source:",
            ["Use Sample Files", "List Your Files"]
        )
        
        if evidence_source == "Use Sample Files":
            if st.button("Analyze Sample Evidence", type="primary"):
                with st.spinner("Analyzing evidence with AI..."):
                    # Load sample files
                    with open('sample_data\\sample_files.json', 'r', encoding='utf-8') as f:
                        files = json.load(f)
                    
                    # Analyze
                    st.session_state.analysis = st.session_state.agent.analyze_evidence(
                        st.session_state.indicators,
                        files
                    )
                    
                    st.success("✓ Analysis complete!")
                    st.rerun()
        
        else:
            st.info("Enter your evidence file names (one per line)")
            file_list_text = st.text_area(
                "File names:",
                height=200,
                placeholder="IEP_Student_123_2024.pdf\nEvaluation_Report_456_2024.pdf\n..."
            )
            
            if file_list_text and st.button("Analyze My Evidence", type="primary"):
                with st.spinner("Analyzing your evidence..."):
                    # Parse file list
                    files = [f.strip() for f in file_list_text.split('\n') if f.strip()]
                    
                    # Analyze
                    st.session_state.analysis = st.session_state.agent.analyze_evidence(
                        st.session_state.indicators,
                        files
                    )
                    
                    st.success("✓ Analysis complete!")
                    st.rerun()
        
        # Show analysis results
        if st.session_state.analysis:
            st.markdown("---")
            st.subheader("📊 Compliance Status")
            
            for ind_key, data in st.session_state.analysis.items():
                # Status badge
                status_color = {
                    "Complete": "green",
                    "Partial": "orange",
                    "Missing": "red"
                }
                
                status_emoji = {
                    "Complete": "✅",
                    "Partial": "⚠️",
                    "Missing": "❌"
                }
                
                color = status_color.get(data['status'], 'gray')
                emoji = status_emoji.get(data['status'], '❓')
                
                st.markdown(f"**{emoji} {ind_key.upper()}**")
                st.markdown(f":{color}[{data['status']}] - {data['confidence']}% confidence")
                
                with st.expander("View Details"):
                    st.write("**Evidence Found:**")
                    for f in data['evidence_found'][:5]:
                        st.write(f"  ✓ {f}")
                    
                    if data['evidence_missing']:
                        st.write("**Evidence Missing:**")
                        for m in data['evidence_missing']:
                            st.write(f"  ✗ {m}")
                    
                    st.write(f"**Reasoning:** {data['reasoning']}")
                
                st.markdown("---")
    
    else:
        st.info("👈 Upload a protocol first to begin analysis")

# Bottom section: Generate narratives
if st.session_state.indicators and st.session_state.analysis:
    st.markdown("---")
    st.header("📝 Step 3: Generate Narratives")
    
    # Select indicator
    indicator_options = [
        f"Indicator {ind['number']}: {ind['title']}"
        for ind in st.session_state.indicators['indicators']
    ]
    
    selected = st.selectbox("Select indicator for narrative:", indicator_options)
    
    if st.button("Generate Compliance Narrative", type="primary"):
        with st.spinner("Generating narrative..."):
            # Get selected indicator
            ind_num = selected.split(":")[0].split()[-1]
            indicator = next(
                ind for ind in st.session_state.indicators['indicators']
                if ind['number'] == ind_num
            )
            analysis_key = f"indicator_{ind_num}"
            analysis_data = st.session_state.analysis[analysis_key]
            
            # Generate narrative
            narrative = st.session_state.agent.generate_narrative(
                indicator,
                analysis_data
            )
            
            # Display
            st.success("✓ Narrative generated!")
            st.markdown("### Draft Compliance Narrative")
            st.text_area(
                "Copy this to your compliance report:",
                narrative,
                height=300
            )
            
            # Download button
            st.download_button(
                label="📥 Download Narrative",
                data=narrative,
                file_name=f"narrative_indicator_{ind_num}.txt",
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.caption("EduComply POC v0.1 | Built with Claude Code & Streamlit")