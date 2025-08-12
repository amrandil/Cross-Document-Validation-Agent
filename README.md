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
- **Frontend**: Modern React/Next.js interface for document upload and analysis

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
- Node.js 18+ and pnpm
- OpenAI API key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Cross-Document-Validation-Agent
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

3. **Install backend dependencies**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend
pnpm install
cd ..
```

### Running the Application

#### Option 1: Development Mode (Recommended)

1. **Start the backend server** (Terminal 1)
```bash
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the React frontend** (Terminal 2)
```bash
cd frontend
pnpm dev
```

3. **Access the application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

#### Option 2: Using Docker

```bash
docker-compose up --build
```

## 🔧 Usage

### Web Interface

Access the React interface at `http://localhost:3000` to:
- Upload document bundles with drag & drop
- Configure analysis settings
- View real-time agent analysis
- Examine detailed fraud reports
- Monitor API connection status

### API Endpoints

#### Analyze Documents
```bash
POST /api/v1/analyze/upload
```

Upload multiple documents and receive fraud analysis with:
- Step-by-step agent reasoning
- Cross-document inconsistencies
- Fraud confidence scores
- Detailed evidence compilation

#### Health Check
```bash
GET /api/v1/health
```

#### Agent Information
```bash
GET /api/v1/agent/info
```

## 🛠️ Development

### Project Structure
```
Cross-Document-Validation-Agent/
├── src/                       # Backend source code
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration management
│   ├── api/                  # API endpoints
│   ├── agent/                # ReAct agent implementation
│   ├── tools/                # Fraud detection tools
│   ├── models/               # Pydantic data models
│   └── utils/                # Utilities and helpers
├── frontend/                 # React/Next.js frontend
│   ├── app/                  # Next.js app directory
│   ├── components/           # React components
│   ├── hooks/                # Custom React hooks
│   ├── lib/                  # Utility libraries
│   └── public/               # Static assets
├── frontend_streamlit/       # Legacy Streamlit frontend
├── sample_documents/         # Sample documents for testing
└── testCases/                # Test case documents
```

### Frontend Development

The React frontend is built with:
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible components
- **React Hook Form** - Form handling
- **React Dropzone** - File uploads

### Backend Development

#### Adding New Tools

1. Create tool in `src/tools/`
2. Register with agent in `src/agent/core.py`
3. Update tool descriptions in `src/agent/prompts.py`

#### API Development

The backend provides RESTful APIs with automatic documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

## 🔍 Testing

### Sample Documents

Use the documents in `sample_documents/` for testing:
- `commercial_invoice.txt`
- `packing_list.txt`
- `bill_of_lading.txt`
- `certificate_of_origin.txt`

### Test Cases

Browse `testCases/` directory for real-world document examples from various companies.

## 🚨 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Ensure virtual environment is activated
   - Check OpenAI API key in `.env`
   - Verify all dependencies are installed

2. **Frontend won't start**
   - Ensure Node.js 18+ is installed
   - Run `pnpm install` in frontend directory
   - Check if port 3000 is available

3. **API connection fails**
   - Verify backend is running on port 8000
   - Check CORS settings in backend
   - Use "Test API" button in frontend

### Logs

- **Backend logs**: Check terminal running uvicorn
- **Frontend logs**: Check browser developer console
- **Application logs**: Check `logs/` directory



