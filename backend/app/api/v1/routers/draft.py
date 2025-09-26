from fastapi import APIRouter, Depends, HTTPException, UploadFile
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.draft_schema import DraftRead
from app.crud.draft_crud import draft_crud
from app.api.deps import get_db, get_current_user
from app.models.user_model import User
from app.controllers.draft import draft_create

router = APIRouter()

@router.post("/", response_model=DraftRead, status_code=201)
async def create_draft(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = await draft_create(file=file, db=db, current_user=current_user)
    
    return draft

@router.get("/{draft_id}", response_model=DraftRead)
async def get_draft(
    draft_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = await draft_crud.get(db, id=draft_id, user_id=current_user.id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return draft

@router.delete("/{draft_id}", status_code=204)
async def delete_draft(
    draft_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = await draft_crud.remove(db, id=draft_id, user_id=current_user.id)
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    return