## 1. Business Context & Problem Statement

### Core Challenge

**Customs Valuation Fraud in International Trade**: During the customs clearance process, importers must declare the accurate value of goods to determine the correct amount of import duties and taxes owed. However, importers frequently engage in **undervaluation fraud** by deliberately declaring goods at values lower than their actual transaction value to illegally reduce their customs duty payments.

**The Problem**: Customs authorities struggle to detect sophisticated valuation fraud schemes because fraudsters use coordinated deception across multiple required documents (invoices, packing lists, shipping documents, certificates of origin). While individual documents may appear legitimate when examined separately, the fraud becomes apparent only when **analyzing all documents together** to identify cross-document inconsistencies.

**Current Gap**: Manual cross-document validation is time-consuming, inconsistent, and often misses complex fraud patterns that span multiple document types. Customs agencies need an automated solution that can systematically detect these sophisticated schemes that exploit the multi-document nature of customs declarations.

---

## 2. Task Requirements & Fraud Detection Scope

### 2.1 Primary Objective

**Develop an AI agent that analyzes submitted customs declaration documents to identify potential valuation fraud by detecting inconsistencies within and across documents.**

### 2.2 Document Types to Process

### Core Documents (Always Required)

1. **Commercial Invoice**
    - Purpose: Primary document used by most foreign customs agencies for import control, valuation and duty determination
    - Key Fields: Item descriptions, quantities, unit prices, total values, currency, supplier/buyer details
    - Fraud Risk: Primary target for undervaluation manipulation
2. **Packing List**
    - Purpose: Identifies the quantity, weight, dimensions, and carton count of the shipped products
    - Key Fields: Item descriptions, quantities, weights, dimensions, package counts
    - Fraud Risk: Inconsistencies with invoice quantities/descriptions
3. **Bill of Lading (B/L)**
    - Purpose: Legal document for shipping goods, contains all essential details of the shipper, receiver, goods, and shipping terms
    - Key Fields: Shipper/consignee details, cargo description, weight, shipping terms
    - Fraud Risk: Weight/description mismatches with other documents

### Supporting Documents (When Available)

1. **Certificate of Origin**
    - Purpose: States the origin of the exported commodity and serves as a declaration by the exporter
    - Fraud Risk: Transshipment to obscure the true country of origin, and illegally evade customs duties
2. **Customs Declaration Form**
    - Purpose: Official declaration submitted to customs authorities
    - Key Fields: Declared values, classifications, duty calculations
    - Fraud Risk: Central document for all fraud schemes

### 2.3 Types of Fraud to Detect

### 2.3.1 Valuation Fraud (Priority 1)

**Undervaluation**: Most common type of customs fraud, where importers declare too low a value for the imported product to illegally reduce import duty owed

**Detection Patterns:**

- Round numbers suggesting estimates rather than actual prices
- Values that don't align with quantity/weight ratios

### 2.3.2 Quantity/Weight Manipulation (Priority 1)

**Description**: Falsify quantity or weight, often using forged or altered invoices

**Detection Patterns:**

- Quantity mismatches between the invoice, packing list, and B/L
- Weight inconsistencies across documents
- Unit weight calculations that seem unreasonable
- Package count discrepancies

### 2.3.3 Origin Manipulation (Priority 1)

**Transshipment Fraud**: Send goods from country of origin to intermediate country to obscure true origin and evade customs duties

**Detection Patterns:**

- Origin country mismatches between documents
- Shipping routes inconsistent with declared origin
- Suppliers located in different countries than declared origin

---

# Agent Architecture

## **Core Design Principles**

The agent should be built with small integrable components that allow for incremental development. The list of evaluation criteria can be expandable. The Agent can start by an MVP with the most important criteria or rules to validate, then we can add on top of them more detailed or sophisticated validation requirements in the future that can require more sophisticated validation systems.

The MVP should only check cross-document consistency and frauds hidden within documents.

Later, we can check the feasibility of adding more checks in the agent reasoning phase like checking market value, or historical patterns.

---

## **Agent Workflow:**

> **ReAct Strategy (Observation + Reasoning + Acting)**
> 

### **Core Agent Loop**

The agent operates using a **modified ReAct (Reasoning + Acting) strategy**, starting with initial observation:

<aside>

## **Agent Operational Flow**

The agent operates through an intelligent, document-driven investigation process that begins with a comprehensive environmental assessment. In the **Observation phase**, the agent first identifies and classifies the types of documents present in the submission (invoice, packing list, bill of lading, certificates, etc.), then determines the expected data schema (if not already provided) and required fields for each document type. The agent systematically extracts both standard required information and identifies any additional relevant data points, patterns, or anomalies that may provide investigative insights, while assessing the relevance and significance of each data element within the context of the specific case.

During the **Thought phase**, the agent synthesizes and cross-analyzes all collected data to identify suspicious patterns, inconsistencies, or fraud indicators across the document set. This involves comparing corresponding data points between documents, evaluating mathematical relationships, assessing the logical coherence of the declared information, and forming hypotheses about potential fraud schemes based on detected anomalies.

In the **Action phase**, the agent executes targeted investigative actions based on its analysis, which may include re-examining specific documents with enhanced focus, performing detailed calculations and validations, cross-referencing information against available external sources or databases (may be out of scope for the MVP), and applying specialized fraud detection tools. The agent dynamically selects and sequences these actions based on the specific patterns and risk indicators identified during the analysis phase, ensuring that each investigation is tailored to the unique characteristics and potential fraud vectors of the case at hand.

</aside>

**Tradition ReAct Loop**

```
THOUGHT → ACTION → OBSERVATION → Repeat → FINAL ANSWER
```

**Modified Loop**

```
OBSERVATION → THOUGHT → ACTION → OBSERVATION → Repeat → FINAL ANSWER
```

**Why We Need Initial Observation:**

- **Environmental Awareness**: Agent must first perceive what documents it has received
- **Context Setting**: Understanding the scope and nature of the case before reasoning

### **ReAct Cycle Breakdown for Fraud Detection**

### **INITIAL OBSERVATION (Environmental Perception)**

The agent first observes its environment to understand what it's working with:

- **Document Bundle Assessment**: "I have received 4 documents: invoice, packing list, certificate of origin, and bill of lading"
- **Basic Characteristics**: "This is a $500K electronics shipment from an unknown supplier"
- **Document Quality**: "All documents are clear PDFs with good readability"
- **Completeness Check**: "All required document types are present for analysis"

### **THOUGHT (Reasoning)**

Based on initial observations, the agent reasons about strategy:

- **Risk Assessment**: "High value + unknown supplier + electronics = enhanced scrutiny needed"
- **Investigation Strategy**: "I should start with cross-document consistency checks"
- **Tool Selection**: "Given the risk profile, I'll begin with quantity and product validation"
- **Hypothesis Formation**: "Let me check for common fraud patterns in electronics shipments"

### **ACTION (Tool Execution)**

The agent executes specific validation tools:

- **Document Processing**: Extract and parse structured data from documents
- **Validation Execution**: Run selected fraud detection tools
- **Tool Usage**: Query databases or apply business rules
- **Evidence Gathering**: Compile findings for analysis

### **OBSERVATION (Results Analysis)**

The agent observes the results of its actions:

- **Tool Outputs**: "Quantity validation shows 15% discrepancy between invoice and packing list"
- **Pattern Detection**: "Product descriptions show suspicious variations"
- **Evidence Quality**: "High confidence findings with multiple supporting data points"
- **New Information**: "Additional red flags discovered during validation"

### **Complete Modified ReAct Cycle Example - MVP Implementation**

### **Scenario: Suspicious Electronics Shipment**

```
INITIAL OBSERVATION: 
I have received a customs declaration bundle containing 4 documents: commercial invoice, packing list, certificate of origin, and bill of lading. 
The shipment involves 100 electronic devices valued at $40,000 from supplier "TechExport GmbH" to buyer "Electronics Import LLC". All documents are clear PDFs suitable for analysis.

THOUGHT: 
I have a complete document set for analysis. Let me start with basic cross-document validation to check if all documents tell a consistent story. I'll begin with quantity consistency since this is fundamental to all other validations.

ACTION: validate_quantity_consistency

OBSERVATION: 
Quantity validation results:
- Invoice: 100 units "smartphones"
- Packing List: 100 units "premium smartphones + accessories"  
- Bill of Lading: 100 units electronic devices
Quantities are numerically consistent but product descriptions show variations.

THOUGHT: 
While quantities match numerically, there's a concerning product description 
discrepancy. The invoice shows basic "smartphones" but the packing list specifies "premium smartphones + accessories". This could indicate product substitution fraud. 
Let me validate the weight consistency to see if it supports premium vs basic products.

ACTION: validate_weight_consistency

OBSERVATION: Weight validation results:
- Packing List: Total weight 250kg (2.5kg per unit)
- Bill of Lading: Total weight 250kg 
- Weight consistency: PASS between documents
- Weight analysis: 2.5kg per smartphone seems excessive for basic phones

THOUGHT: 
The weights are consistent between documents (good) but 2.5kg per smartphone 
is unusually heavy for basic phones, which typically weigh 0.2-0.5kg each. This weight is more consistent with premium smartphones plus accessories. Combined with the product description mismatch, this strengthens the product substitution hypothesis. Let me check the mathematical consistency of the pricing.

ACTION: validate_unit_calculations

OBSERVATION: 
Mathematical validation results:
- Declared: 100 units × $400 each = $40,000 total
- Calculation verification: PASS - math is correct
- Unit price analysis: $400 per basic smartphone seems reasonable
- Cross-reference: If premium phones + accessories, $400 would be undervalued

THOUGHT: 
The mathematics are correct, but if these are actually premium phones with 
accessories (as suggested by weight and packing list description), then $400 per unit would be significantly undervalued. Let me check the origin consistency to see if there are additional fraud indicators.

ACTION: validate_geographic_consistency

OBSERVATION: Geographic validation results:
- Certificate of Origin: "Made in Germany, manufactured by TechExport GmbH"
- Bill of Lading: Loading port "Shanghai, China" → destination "Dubai, UAE"
- Route analysis: German products loading from Chinese port without transit documentation
- Geographic consistency: FAIL - major discrepancy detected

THOUGHT: 
Critical inconsistency found! The certificate claims German manufacturing 
but the shipment originates directly from Shanghai, China, with no evidence of transit through Germany. This indicates false origin certificate fraud, possibly to evade higher duties on Chinese electronics. Combined with the product substitution evidence, this appears to be a coordinated fraud scheme.

ACTION: validate_entity_consistency

OBSERVATION: 
Entity validation results:
- Invoice: Supplier "TechExport GmbH, Berlin, Germany"
- Certificate: Manufacturer "TechExport GmbH, Berlin, Germany"  
- Bill of Lading: Shipper "TechExport Trading Co., Shanghai, China"
- Entity consistency: FAIL - supplier location mismatch between documents

THOUGHT: 
The entity information reveals another layer of deception. The invoice and 
certificate claim a German company, but the actual shipper is based in Shanghai, China. This confirms the false origin scheme. I have multiple fraud indicators: product substitution, false origin certificate, and entity location misrepresentation. 
Let me synthesize all evidence for final assessment.

ACTION: synthesize_fraud_evidence

OBSERVATION: 
Fraud evidence synthesis:
- Product substitution indicators: 85% confidence
  * Invoice: "smartphones" vs Packing List: "premium smartphones + accessories"
  * Weight supports premium products (2.5kg vs expected 0.5kg for basic)
- False origin certificate: 95% confidence  
  * Certificate claims Germany, shipment from China
  * No transit documentation or German port involvement
- Entity misrepresentation: 90% confidence
  * Supplier claimed in Germany, actual shipper in China
  * Coordinated documentation to support false origin claim
- Overall fraud probability: 90% confidence

THOUGHT: 
The evidence is overwhelming and internally consistent across multiple fraud 
vectors. This is clearly a sophisticated coordinated scheme involving:
1. Product substitution (declaring basic phones, shipping premium + accessories)
2. False origin certificate (claiming German origin for Chinese goods)  
3. Entity misrepresentation (fake German supplier identity)
The combination of these fraud types suggests systematic undervaluation and duty evasion.

FINAL ANSWER: 
FRAUD DETECTED - Coordinated multi-vector fraud scheme identified with 90% confidence.

FRAUD SUMMARY:
- Primary Scheme: Product substitution with false origin certificate
- Evidence: Cross-document inconsistencies in product descriptions, weight anomalies supporting premium goods, geographic impossibilities, and entity location misrepresentation
- Financial Impact: Estimated undervaluation of $20,000-30,000 based on premium product pricing
- Duty Evasion: False German origin to avoid higher Chinese electronics tariffs
- Recommendation: Immediate physical inspection, supplier investigation, and enforcement action required

SUPPORTING EVIDENCE:
- Document inconsistencies across 4 different document types
- Weight-to-product analysis supporting premium goods hypothesis  
- Geographic route analysis proving false origin claims
- Entity verification showing coordinated misrepresentation
```

### **🛠️ ACTIONS & TOOLS (LangChain Integration)**

### **LangChain Tool Framework**

Each validation action is implemented as a **LangChain Tool** with standard interface.

### **MVP Tool Suite**

This tool suite provides a conceptual idea of the tool set that can be present in  an MVP implementation. Tools can be added, modified, or excluded during development based on actual fraud detection needs and performance requirements.

**Cross-Document Validation Tools:**

- `extract_data_from_document`
- `validate_quantity_consistency` - **LangChain Tool**: Compare quantities across invoice, packing list, and B/L
- `validate_weight_consistency` - **LangChain Tool**: Check weight alignment across all documents
- `validate_entity_consistency` - **LangChain Tool**: Verify entity names and addresses match
- `validate_product_descriptions` - **LangChain Tool**: Ensure product descriptions are consistent
- `validate_value_consistency` - **LangChain Tool**: Cross-check declared values and calculations
- `validate_geographic_consistency` - **LangChain Tool**: Verify origin claims against shipping routes
- `detect_timing_anomalies` - **LangChain Tool**: Check document date consistency and logical sequence

**Mathematical Validation Tools:**

- `validate_unit_calculations` - **LangChain Tool**: Verify quantity × unit price = total value
- `validate_weight_ratios` - **LangChain Tool**: Check if weight/quantity ratios are reasonable
- `validate_package_calculations` - **LangChain Tool**: Ensure package counts align with quantities
- `detect_round_number_patterns` - **LangChain Tool**: Identify suspiciously round pricing

**Pattern Detection Tools:**

- `detect_product_substitution` - **LangChain Tool**: Compare product descriptions for subtle variations
- `detect_origin_manipulation` - **LangChain Tool**: Identify transshipment fraud indicators
- `detect_entity_variations` - **LangChain Tool**: Find suspicious entity name/address variations
- `synthesize_fraud_evidence` - **LangChain Tool**: Combine all validation results into fraud assessment

**Future Enhanced Tools (Post-MVP):**

- `validate_market_pricing` - **LangChain Tool**: Compare prices against market databases
- `validate_hscode_classification` - Langchain Tool: checks if the Declared Code is correct
- `analyze_historical_patterns` - **LangChain Tool**: Check entity transaction history
- `validate_trade_agreements` - **LangChain Tool**: Verify preferential tariff eligibility
- `analyze_entity_relationships` - **LangChain Tool**: Deep corporate structure analysis

### **📚 LEARNING & MEMORY (Not for MVP)**

**Learning Mechanisms integrated with LangChain:**

### **Memory Integration**

```python
from langchain.memory import ConversationBufferMemory, VectorStoreRetrieverMemory

class FraudDetectionMemory:
    def __init__(self):
        # Short-term memory for current investigation
        self.conversation_memory = ConversationBufferMemory()

        # Long-term memory for patterns and historical cases
        self.vector_memory = VectorStoreRetrieverMemory(
            retriever=fraud_pattern_vectorstore.as_retriever()
        )

```

---

### **Extensibility Design**

### **Adding External/New Tools**

1. Implement tool interface
2. Register tool with tool manager
3. Update relevant actions to use new tool
4. No changes needed to core agent logic

---

### **Report Generation**

The agent generates structured reports with:

- **Executive Summary**: High-level fraud assessment
- **Evidence Details**: Specific inconsistencies found across documents
- **Confidence Analysis**: Reliability of conclusions
- **Recommended Actions**: Next steps for investigators
- **Supporting Documentation**: Cross-document evidence compilation

This architecture ensures the agent can start simple and grow sophisticated while maintaining reliability and explainability throughout its evolution.

---

# Implementation Roadmap

## **MVP: Core Cross-Document Fraud Detection**

### **MVP Scope**

**Single Focus**: Detect fraud that's only visible when analyzing multiple documents together

**Core Capabilities**:

1. **Document bundle processing** (invoice + packing list + certificates + shipping docs)
2. **Cross-document field extraction** and mapping
3. **Basic consistency validation** (quantities, weights, values, entities)
4. **Simple fraud pattern detection** (detect fraud that can be detected from inconsistencies based on the data available)
5. **Clear reporting** with evidence from multiple documents

**No Market Data Required**: Focus purely on internal document consistency

MVP Value Delivery

```
Example MVP Detection:
- Invoice: 100 basic phones @ $200 = $20,000
- Packing List: 100 premium phones + accessories, Weight: 150kg  
- Shipping Manifest: Container weight 150kg
- Insurance: $45,000 coverage

MVP Agent Output:
"FRAUD DETECTED: Product substitution scheme
- Invoice describes basic phones but packing list shows premium models
- Insurance value 125% above invoice value suggests undervaluation
- Weight consistent with premium phones, not basic models
- Evidence: Cross-document product description mismatch"
```

---

## Design Choices & Technology Stack

---

## **MVP Design Decisions**

### **1. LLM & Model Architecture**

**Chosen**: **OpenAI GPT Models**

**Rationale**:

- **Best-in-class reasoning capabilities** for complex fraud pattern detection
- **Strong document analysis performance** for unstructured data extraction
- **Mature API ecosystem** with reliable service and comprehensive documentation
- **JSON mode support** for structured data extraction from documents
- **Function calling capabilities** essential for ReAct tool integration

**MVP Configuration**:

- **Primary Model**: GPT-4 Turbo (128K context window for large document sets)
- **Fallback Model**: GPT-3.5 Turbo (for simple validation tasks to manage costs)
- **Temperature**: 0.1-0.3 (low temperature for consistent, reliable fraud detection)

---

### **2. Document Processing Architecture**

### **Document Extraction Strategy**

**Chosen**: **LLM-Based Extraction**

**Implementation Approach**:

```python
class LLMDocumentProcessor:
    def extract_structured_data(self, document, document_type):
        prompt = f"""
        Extract structured data from this {document_type} document.
        Return JSON with fields: {self.get_expected_schema(document_type)}

        Document content: {document}
        """
        return self.llm.invoke(prompt, response_format="json")

```

**Rationale**:

- **Maximum flexibility** for handling diverse document formats and layouts
- **Adaptive extraction** based on document quality and structure
- **Contextual understanding** of document relationships and inconsistencies

---

### **3. Tool Architecture**

### **Tool Implementation Strategy**

**Chosen**: **LLM-Based Tools** (with programmatic calculations where applicable)

**Hybrid Approach**:

- **LLM Tools**: Complex pattern recognition, contextual analysis, fuzzy matching
- **Programmatic Tools**: Mathematical calculations, exact rule checking, data formatting

**Tool Granularity**: **Fine-grained approach**

- Each validation criterion = One specific tool
- Examples: `quantity_consistency_tool`, `weight_validation_tool`, `entity_matching_tool`
- **Benefits**: Modular development, easy testing, incremental enhancement

---

### **4. Workflow Orchestration**

### **Agent Execution Framework**

**Chosen**: **LangChain AgentExecutor**

**Rationale**:

- **Proven ReAct implementation** with robust error handling
- **Tool integration framework** handles all tool calling logic
- **Built-in conversation memory** for maintaining investigation context
- **Rapid prototyping** with minimal custom orchestration code

---

### **5. Learning & Adaptation ( Not for MVP - for Future Increments)**

### **Planned Learning Approaches (Post-MVP)**

**Phase 2 Learning Strategy**:

- **Rule-based adjustments**: Modify validation thresholds based on performance
- **Few-shot learning**: Update prompts with examples from corrected cases
- **Pattern database**: Maintain repository of confirmed fraud patterns

**Implementation Framework**:

```python
# Future learning system design
class FraudLearningSystem:
    def adjust_rule_weights(self, case_feedback):
        # Modify tool confidence thresholds based on outcomes
        pass

    def update_few_shot_examples(self, case_result, human_correction):
        # Add successful/corrected cases to tool prompts
        pass

    def extract_new_patterns(self, confirmed_fraud_cases):
        # Identify new fraud patterns from validated cases
        pass

```

**MVP Approach**: **No learning system** - focus on core fraud detection capabilities first.

---

## **Technology Stack**

### **Core Framework & Libraries**

### **Agent Framework**

- Langchain

### **Data Processing & Utilities**

Data manipulation

- pandas
- numpy

Data validation

- pydantic

### **Web Framework & API**

- FastAPI
- uvicorn