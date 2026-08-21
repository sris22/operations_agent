from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.core.security import get_current_user
from app.services.document_service import delete_document, list_documents, upload_document

router = APIRouter()


@router.post("")
async def upload(
    file: UploadFile = File(...),
    metadata: str | None = Form(None),
    current_user=Depends(get_current_user),
):
    import json

    meta = json.loads(metadata) if metadata else None

    content = await file.read()
    try:
        result = await upload_document(
            filename=file.filename,
            file_content=content,
            metadata=meta,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("")
async def list_docs(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
):
    return await list_documents(page=page, page_size=min(page_size, 100))


@router.delete("/{document_id}")
async def delete_doc(
    document_id: int,
    current_user=Depends(get_current_user),
):
    deleted = await delete_document(document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "document_id": document_id}
