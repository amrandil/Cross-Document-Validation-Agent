"""Document models for the fraud detection agent."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentType(str, Enum):
    """Types of documents that can be processed."""
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    CUSTOMS_DECLARATION = "customs_declaration"


class Document(BaseModel):
    """Base document model."""
    document_type: DocumentType
    filename: str
    content: str = Field(...,
                         description="Raw document content or extracted text")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class Entity(BaseModel):
    """Entity information (supplier, buyer, etc.)."""
    name: str
    address: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    contact_info: Optional[str] = None


class ProductItem(BaseModel):
    """Product item information."""
    description: str
    quantity: float
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    total_value: Optional[float] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    hs_code: Optional[str] = None


class CommercialInvoice(BaseModel):
    """Commercial invoice structured data."""
    invoice_number: str
    invoice_date: datetime
    supplier: Entity
    buyer: Entity
    items: List[ProductItem]
    currency: str
    total_value: float
    payment_terms: Optional[str] = None
    incoterms: Optional[str] = None


class PackingList(BaseModel):
    """Packing list structured data."""
    packing_list_number: Optional[str] = None
    date: Optional[datetime] = None
    items: List[ProductItem]
    total_packages: Optional[int] = None
    total_weight: Optional[float] = None
    total_volume: Optional[float] = None
    package_details: Optional[List[str]] = None


class BillOfLading(BaseModel):
    """Bill of lading structured data."""
    bl_number: str
    date: datetime
    shipper: Entity
    consignee: Entity
    notify_party: Optional[Entity] = None
    vessel_name: Optional[str] = None
    voyage_number: Optional[str] = None
    port_of_loading: str
    port_of_discharge: str
    cargo_description: str
    total_weight: Optional[float] = None
    number_of_packages: Optional[int] = None
    freight_terms: Optional[str] = None


class CertificateOfOrigin(BaseModel):
    """Certificate of origin structured data."""
    certificate_number: str
    issue_date: datetime
    issuing_authority: str
    exporter: Entity
    consignee: Entity
    country_of_origin: str
    goods_description: str
    value: Optional[float] = None
    currency: Optional[str] = None


class CustomsDeclaration(BaseModel):
    """Customs declaration structured data."""
    declaration_number: str
    date: datetime
    declarant: Entity
    items: List[ProductItem]
    total_declared_value: float
    currency: str
    duty_calculation: Optional[Dict[str, float]] = None
    tariff_codes: Optional[List[str]] = None


class DocumentBundle(BaseModel):
    """Bundle of documents for analysis."""
    bundle_id: str = Field(...,
                           description="Unique identifier for the document bundle")
    documents: List[Document]
    commercial_invoice: Optional[CommercialInvoice] = None
    packing_list: Optional[PackingList] = None
    bill_of_lading: Optional[BillOfLading] = None
    certificate_of_origin: Optional[CertificateOfOrigin] = None
    customs_declaration: Optional[CustomsDeclaration] = None

    def get_document_types(self) -> List[DocumentType]:
        """Get list of document types in this bundle."""
        return [doc.document_type for doc in self.documents]

    def has_required_documents(self) -> bool:
        """Check if bundle has all required document types."""
        required = {
            DocumentType.COMMERCIAL_INVOICE,
            DocumentType.PACKING_LIST,
            DocumentType.BILL_OF_LADING
        }
        present = set(self.get_document_types())
        return required.issubset(present)

    def get_document_by_type(self, doc_type: DocumentType) -> Optional[Document]:
        """Get document by type from bundle."""
        for doc in self.documents:
            if doc.document_type == doc_type:
                return doc
        return None
