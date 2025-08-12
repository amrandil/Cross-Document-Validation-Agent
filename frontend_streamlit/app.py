"""Streamlit frontend for the Multi-Document Fraud Detection Agent."""

import streamlit as st
import requests
import json
from typing import List, Dict, Any
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Multi-Document Fraud Detection Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"


def main():
    """Main Streamlit application."""
    st.title("🔍 Multi-Document Fraud Detection Agent")
    st.markdown(
        "*AI-powered cross-document analysis for customs fraud detection*")

    # Sidebar
    with st.sidebar:
        st.header("🛠️ Agent Configuration")

        # API connection test
        if st.button("Test API Connection"):
            test_api_connection()

        st.markdown("---")

        # Analysis options
        st.subheader("Analysis Options")
        confidence_threshold = st.slider(
            "Confidence Threshold", 0.0, 1.0, 0.7, 0.1)
        detailed_analysis = st.checkbox("Detailed Analysis", value=True)

        options = {
            "confidence_threshold": confidence_threshold,
            "detailed_analysis": detailed_analysis
        }

    # Main content area
    tab1, tab2, tab3 = st.tabs(
        ["📄 Document Upload", "📊 Analysis Results", "🔧 Agent Information"])

    with tab1:
        document_upload_tab(options)

    with tab2:
        analysis_results_tab()

    with tab3:
        agent_info_tab()


def test_api_connection():
    """Test connection to the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health", timeout=5)
        if response.status_code == 200:
            st.success("✅ API connection successful!")
            health_data = response.json()
            st.json(health_data)
        else:
            st.error(f"❌ API connection failed: {response.status_code}")
    except Exception as e:
        st.error(f"❌ API connection failed: {str(e)}")


def document_upload_tab(options: Dict[str, Any]):
    """Document upload and analysis tab."""
    st.header("📄 Upload Documents for Analysis")

    st.markdown("""
    Upload your customs documents for comprehensive fraud detection analysis.
    The agent will perform cross-document validation to identify potential fraud schemes.
    """)

    # Document upload
    st.subheader("Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose document files",
        accept_multiple_files=True,
        type=['txt', 'pdf', 'docx', 'csv'],
        help="Upload customs documents (invoices, packing lists, bills of lading, certificates)"
    )

    # Bundle ID input
    bundle_id = st.text_input(
        "Bundle ID (optional)",
        placeholder="Leave empty to auto-generate",
        help="Unique identifier for this document bundle"
    )

    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} files uploaded")

        # Show file information
        with st.expander("📋 File Information"):
            for file in uploaded_files:
                st.write(f"**{file.name}** - {file.size} bytes")

        # Analyze button
        if st.button("🔍 Analyze Documents", type="primary"):
            analyze_documents(uploaded_files, bundle_id, options)


def analyze_documents(uploaded_files: List, bundle_id: str, options: Dict[str, Any]):
    """Analyze uploaded documents."""
    with st.spinner("🔄 Analyzing documents for fraud indicators..."):
        try:
            # Prepare files for API
            files = []
            for file in uploaded_files:
                files.append(
                    ("files", (file.name, file.getvalue(), file.type)))

            # Prepare form data
            data = {
                "options": json.dumps(options)
            }
            if bundle_id:
                data["bundle_id"] = bundle_id

            # Call API
            response = requests.post(
                f"{API_BASE_URL}/api/v1/analyze/upload",
                files=files,
                data=data,
                timeout=300  # 5 minutes timeout
            )

            if response.status_code == 200:
                analysis_result = response.json()
                st.session_state.analysis_result = analysis_result
                st.success("✅ Analysis completed successfully!")

                # Show quick summary
                show_analysis_summary(analysis_result)

            else:
                st.error(f"❌ Analysis failed: {response.status_code}")
                st.error(response.text)

        except Exception as e:
            st.error(f"❌ Analysis error: {str(e)}")


def show_analysis_summary(result: Dict[str, Any]):
    """Show analysis summary."""
    st.subheader("📊 Analysis Summary")

    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Bundle ID", result["bundle_id"])

    with col2:
        st.metric("Documents Processed", result["documents_processed"])

    with col3:
        st.metric("Processing Time", f"{result['processing_time_ms']}ms")

    with col4:
        if result.get("fraud_analysis"):
            fraud_detected = result["fraud_analysis"]["fraud_detected"]
            st.metric("Fraud Status",
                      "🚨 DETECTED" if fraud_detected else "✅ CLEAR")
        else:
            st.metric("Fraud Status", "⏳ Processing")

    # Fraud analysis summary
    if result.get("fraud_analysis"):
        fraud_analysis = result["fraud_analysis"]

        st.subheader("🎯 Fraud Assessment")

        # Risk level with color coding
        risk_level = fraud_analysis["risk_level"]
        risk_colors = {
            "LOW": "🟢",
            "MEDIUM": "🟡",
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }

        st.markdown(
            f"**Risk Level:** {risk_colors.get(risk_level, '⚪')} {risk_level}")
        st.markdown(
            f"**Confidence:** {fraud_analysis['overall_confidence']:.2%}")
        st.markdown(
            f"**Investigation Priority:** {fraud_analysis['investigation_priority']}")

        # Executive summary
        if fraud_analysis.get("executive_summary"):
            st.subheader("📋 Executive Summary")
            st.write(fraud_analysis["executive_summary"])


def analysis_results_tab():
    """Analysis results tab."""
    st.header("📊 Detailed Analysis Results")

    if "analysis_result" not in st.session_state:
        st.info("👆 Upload and analyze documents first to see detailed results here.")
        return

    result = st.session_state.analysis_result

    # Agent execution details
    st.subheader("🤖 Agent Execution Trace")

    if result.get("agent_execution"):
        execution = result["agent_execution"]

        # Execution metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Execution ID", execution["execution_id"])
        with col2:
            st.metric("Total Steps", execution["total_steps"])
        with col3:
            st.metric("Status", execution["status"])

        # Agent steps
        if execution.get("steps"):
            st.subheader("🔍 Investigation Steps")

            for step in execution["steps"]:
                with st.expander(f"Step {step['step_number']}: {step['step_type']}"):
                    st.write(f"**Content:** {step['content']}")

                    if step.get("tool_used"):
                        st.write(f"**Tool Used:** {step['tool_used']}")

                    if step.get("tool_output"):
                        st.write("**Tool Output:**")
                        st.code(step["tool_output"], language="text")

                    st.write(f"**Timestamp:** {step['timestamp']}")

    # Fraud analysis details
    if result.get("fraud_analysis"):
        st.subheader("🚨 Detailed Fraud Analysis")
        fraud_analysis = result["fraud_analysis"]

        # Recommended actions
        if fraud_analysis.get("recommended_actions"):
            st.write("**Recommended Actions:**")
            for action in fraud_analysis["recommended_actions"]:
                st.write(f"• {action}")

        # Raw fraud analysis data
        with st.expander("🔍 Raw Analysis Data"):
            st.json(fraud_analysis)


def agent_info_tab():
    """Agent information tab."""
    st.header("🔧 Agent Information")

    if st.button("🔄 Refresh Agent Info"):
        get_agent_info()

    if "agent_info" in st.session_state:
        info = st.session_state.agent_info

        st.subheader("🤖 Agent Capabilities")

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Agent Type:** {info.get('agent_type', 'Unknown')}")
            st.write(f"**Tools Available:** {info.get('tools_count', 0)}")

            # Supported document types
            st.write("**Supported Document Types:**")
            for doc_type in info.get("supported_document_types", []):
                st.write(f"• {doc_type.replace('_', ' ').title()}")

        with col2:
            # Fraud types detected
            st.write("**Fraud Types Detected:**")
            for fraud_type in info.get("fraud_types_detected", []):
                st.write(f"• {fraud_type.replace('_', ' ').title()}")

        # Available tools
        st.subheader("🛠️ Available Tools")
        tools = info.get("tools", [])
        if tools:
            for i, tool in enumerate(tools, 1):
                st.write(f"{i}. {tool}")
        else:
            st.write("No tools information available")


def get_agent_info():
    """Get agent information from API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/agent/info", timeout=10)
        if response.status_code == 200:
            st.session_state.agent_info = response.json()
            st.success("✅ Agent info loaded")
        else:
            st.error(f"❌ Failed to get agent info: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Error getting agent info: {str(e)}")


if __name__ == "__main__":
    main()
