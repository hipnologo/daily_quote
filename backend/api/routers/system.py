from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from pydantic import BaseModel
import psutil
import os
from datetime import datetime

from database import get_database
from services.system_service import SystemService
from utils.auth import get_current_user

router = APIRouter()

class SystemHealth(BaseModel):
    status: str
    uptime: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    database_status: str

class ProcessStatus(BaseModel):
    name: str
    status: str
    last_run: str
    next_run: str
    success_rate: float

@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get system health metrics"""
    service = SystemService(db)
    return await service.get_health_metrics()

@router.get("/processes", response_model=List[ProcessStatus])
async def get_process_status(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get status of background processes"""
    service = SystemService(db)
    return await service.get_process_status()

@router.get("/logs")
async def get_system_logs(
    level: str = Query("INFO", regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get system logs"""
    service = SystemService(db)
    return await service.get_logs(level, limit)

@router.get("/metrics")
async def get_performance_metrics(
    hours: int = Query(24, ge=1, le=168),  # Last 24 hours by default
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get performance metrics over time"""
    service = SystemService(db)
    return await service.get_performance_metrics(hours)
