from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_database
from services.file_service import FileService
from utils.auth import get_current_user

router = APIRouter()

@router.get("", include_in_schema=False)
@router.get("/")
async def list_quote_files(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """List all quote files"""
    service = FileService(db)
    files = await service.list_quote_files()
    return {"files": files}

@router.get("/{filename}")
async def read_file(
    filename: str,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Read content of a quote file"""
    service = FileService(db)
    try:
        return await service.read_file_content(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{filename}/backup")
async def backup_file(
    filename: str,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Create backup of a quote file"""
    service = FileService(db)
    try:
        backup_name = await service.backup_file(filename)
        return {"message": f"Backup created: {backup_name}"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
