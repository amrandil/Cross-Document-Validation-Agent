# Sample Documents for Fraud Detection Testing

This directory contains sample customs documents designed to test the Multi-Document Fraud Detection Agent's ability to identify sophisticated fraud schemes through cross-document analysis.

## Document Set Overview

The sample documents represent a shipment of smartphones from a German company to a US importer. However, they contain **intentional inconsistencies** that indicate multiple types of fraud.

### Documents Included

1. **`commercial_invoice.txt`** - Commercial Invoice from TechExport GmbH
2. **`packing_list.txt`** - Packing List with product details
3. **`bill_of_lading.txt`** - Bill of Lading for ocean freight
4. **`certificate_of_origin.txt`** - German Certificate of Origin

## 🚨 Fraud Indicators Embedded

### 1. Product Substitution Fraud
- **Invoice**: Declares "Premium Smartphones with Accessories" at $400/unit, 2.5kg each
- **Packing List**: Lists "Basic Smartphones" at 0.4kg each
- **Weight Discrepancy**: 250kg total (invoice) vs 40kg total (packing list)
- **Evidence**: Premium products shipped but basic products declared for lower duties

### 2. Origin Manipulation / Transshipment Fraud
- **Certificate**: Claims German origin with German manufacturing
- **Bill of Lading**: Shows shipment originating from Shanghai, China
- **Entity Mismatch**: Different company names (TechExport GmbH vs TechExport Trading Co.)
- **Evidence**: False origin certificate to evade higher Chinese electronics tariffs

### 3. Entity Misrepresentation
- **Invoice**: TechExport GmbH, Berlin, Germany
- **Bill of Lading**: TechExport Trading Co., Shanghai, China
- **Evidence**: Coordinated entity variations to support false origin scheme

### 4. Value/Weight Inconsistencies
- **Mathematical Errors**: Weight calculations don't align across documents
- **Pricing Anomalies**: $400 per unit seems reasonable for basic phones but undervalued for premium models

## Expected Agent Behavior

The fraud detection agent should identify:

1. **Cross-Document Inconsistencies**:
   - Product description variations (Premium vs Basic)
   - Weight discrepancies (2.5kg vs 0.4kg per unit)
   - Total weight mismatches (250kg vs 40kg)

2. **Geographic Impossibilities**:
   - German origin claimed but shipped from China
   - No evidence of transit through Germany
   - Entity location mismatches

3. **Coordinated Fraud Scheme**:
   - Multiple fraud vectors supporting each other
   - Systematic undervaluation through product substitution
   - False origin to avoid tariffs

4. **High Confidence Assessment**:
   - Multiple corroborating evidence points
   - Clear patterns across document types
   - Sophisticated coordinated scheme

## Testing Instructions

### Using the Streamlit Frontend
1. Start the backend: `python -m src.main`
2. Start the frontend: `streamlit run frontend/app.py`
3. Upload all four sample documents
4. Observe the agent's step-by-step analysis
5. Review the comprehensive fraud assessment

### Using the API Directly
```bash
# Test with curl
curl -X POST "http://localhost:8000/api/v1/analyze/upload" \
  -F "files=@sample_documents/commercial_invoice.txt" \
  -F "files=@sample_documents/packing_list.txt" \
  -F "files=@sample_documents/bill_of_lading.txt" \
  -F "files=@sample_documents/certificate_of_origin.txt" \
  -F "bundle_id=test_fraud_case_001"
```

## Expected Output

The agent should produce:
- **Fraud Status**: DETECTED
- **Confidence Level**: 85-95%
- **Risk Level**: HIGH or CRITICAL
- **Investigation Priority**: HIGH
- **Multiple Fraud Indicators**: Product substitution, origin manipulation, entity misrepresentation
- **Specific Evidence**: Cross-document inconsistencies with detailed explanations

## Educational Value

These documents demonstrate:
- How fraud schemes exploit multiple document types
- Why cross-document analysis is essential
- The sophistication of real-world customs fraud
- The importance of AI-powered detection systems

⚠️ **Note**: These are synthetic documents created for testing purposes only. They do not represent any real companies or transactions. 