"""
Document Management Router
Handles PDF upload, listing, and status tracking
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from ..models.document import Document, DocumentStatus

router = APIRouter()


@router.post("/", response_model=Document)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF document for processing

    - **file**: PDF file to upload
    """
    # TODO: Validate PDF
    # TODO: Store in MinIO
    # TODO: Create database record
    # TODO: Trigger extraction pipeline

    return {
        "id": "doc_demo_001",
        "filename": file.filename,
        "status": DocumentStatus.UPLOADED,
        "upload_date": "2025-10-01T18:00:00Z",
        "size_bytes": 0,
    }


@router.get("/", response_model=List[Document])
async def list_documents(skip: int = 0, limit: int = 100):
    """
    List all uploaded documents

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    # TODO: Query from database
    return []


@router.get("/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """
    Get document details by ID

    - **document_id**: Unique document identifier
    """
    # TODO: Query from database
    raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document

    - **document_id**: Unique document identifier
    """
    # TODO: Delete from MinIO
    # TODO: Delete from database
    return {"status": "deleted", "document_id": document_id}
