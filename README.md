# Multi-Document Fraud Detection Agent

An AI-powered agent that analyzes customs declaration documents to detect potential valuation fraud by identifying inconsistencies within and across multiple document types.

## 🎯 Overview

This MVP implementation focuses on detecting sophisticated fraud schemes that exploit the multi-document nature of customs declarations, including:

- **Valuation Fraud**: Undervaluation of goods to reduce customs duties
- **Quantity/Weight Manipulation**: Falsified quantities or weights across documents
- **Origin Manipulation**: Transshipment fraud to obscure true country of origin

## 🏗️ Architecture

The agent uses a **ReAct (Reasoning + Acting) strategy** with LangChain:

```
OBSERVATION → THOUGHT → ACTION → OBSERVATION → Repeat → FINAL ANSWER
```

### Core Components

- **ReAct Agent**: Intelligent investigation process using LangChain AgentExecutor
- **Fraud Detection Tools**: Specialized tools for cross-document validation
- **Document Processing**: LLM-based extraction and analysis
- **API Backend**: FastAPI for fraud detection endpoints
- **Frontend**: Streamlit interface for document upload and analysis

## 📋 Document Types Supported

### Required Documents
- **Commercial Invoice**: Primary valuation document
- **Packing List**: Quantity, weight, dimensions
- **Bill of Lading**: Shipping and cargo details

### Optional Documents  
- **Certificate of Origin**: Country of origin verification
- **Customs Declaration Form**: Official customs submission

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd crossDocument_validation_agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

5. **Run the backend**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Run the frontend** (in another terminal)
```bash
streamlit run frontend/app.py
```

## 🔧 Usage

### API Endpoints

#### Analyze Documents
```bash
POST /api/v1/analyze
```

Upload multiple documents and receive fraud analysis with:
- Step-by-step agent reasoning
- Cross-document inconsistencies
- Fraud confidence scores
- Detailed evidence compilation

#### Health Check
```bash
GET /health
```

### Web Interface

Access the Streamlit interface at `http://localhost:8501` to:
- Upload document bundles
- View real-time agent analysis
- Examine detailed fraud reports

## 🛠️ Development

### Project Structure
```
src/
├── main.py                    # FastAPI application
├── config.py                  # Configuration management
├── api/                       # API endpoints
├── agent/                     # ReAct agent implementation
├── tools/                     # Fraud detection tools
├── models/                    # Pydantic data models
└── utils/                     # Utilities and helpers
```

### Adding New Tools

1. Create tool in `src/tools/`
2. Register with agent in `src/agent/core.py`
3. Update tool descriptions in `src/agent/prompts.py`

## 📊 Fraud Detection Capabilities

### Cross-Document Validation
- Quantity consistency across documents
- Weight alignment verification
- Entity name and address matching
- Product description consistency
- Geographic origin validation

### Mathematical Analysis
- Unit calculation verification
- Weight-to-quantity ratio analysis
- Package count validation
- Round number pattern detection

### Pattern Recognition
- Product substitution detection
- Origin manipulation identification
- Entity variation analysis
- Fraud evidence synthesis



