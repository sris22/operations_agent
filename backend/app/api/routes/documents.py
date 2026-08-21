from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()


@router.post("")
async def upload_document(current_user=Depends(get_current_user)):
    return {"message": "Document upload - to be implemented"}


@router.get("")
async def list_documents(current_user=Depends(get_current_user)):
    return {"documents": []}


@router.delete("/{document_id}")
async def delete_document(document_id: int, current_user=Depends(get_current_user)):
    return {"message": "Document delete - to be implemented"}
