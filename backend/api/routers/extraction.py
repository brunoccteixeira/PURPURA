"""
Data Extraction Router
Handles LLM and transformer-based extraction operations
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..models.extraction import ExtractionResult, ExtractionMethod

router = APIRouter()


@router.get("/{document_id}", response_model=ExtractionResult)
async def get_extraction_results(document_id: str):
    """
    Get extraction results for a document

    - **document_id**: Unique document identifier
    """
    # TODO: Query from Trino (extract_results table)
    raise HTTPException(status_code=404, detail="Extraction results not found")


@router.post("/{document_id}/extract")
async def trigger_extraction(
    document_id: str,
    method: ExtractionMethod = ExtractionMethod.HYBRID
):
    """
    Trigger extraction for a document

    - **document_id**: Unique document identifier
    - **method**: Extraction method (transformer, llm, hybrid)
    """
    # TODO: Trigger extraction pipeline
    # TODO: Update document status to PROCESSING
    return {
        "status": "extraction_started",
        "document_id": document_id,
        "method": method,
    }


@router.post("/{document_id}/validate")
async def validate_extraction(document_id: str, corrections: Dict[str, Any]):
    """
    Validate and correct extraction results

    - **document_id**: Unique document identifier
    - **corrections**: User-provided corrections to extracted data
    """
    # TODO: Apply corrections
    # TODO: Update extraction results in Trino
    # TODO: Retrain models with validated data
    return {"status": "validated", "document_id": document_id}
