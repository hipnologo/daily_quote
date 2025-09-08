from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import psutil
import os
import logging
from pathlib import Path

class SystemService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # System uptime
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.now().timestamp() - boot_time
            uptime = str(timedelta(seconds=int(uptime_seconds)))
            
            # Database status
            try:
                self.db.execute("SELECT 1")
                db_status = "healthy"
            except Exception:
                db_status = "error"
            
            return {
                "status": "healthy" if cpu_usage < 90 and memory_usage < 90 else "warning",
                "uptime": uptime,
                "cpu_usage": round(cpu_usage, 2),
                "memory_usage": round(memory_usage, 2),
                "disk_usage": round(disk_usage, 2),
                "database_status": db_status
            }
            
        except Exception as e:
            return {
                "status": "error",
                "uptime": "unknown",
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "database_status": "error",
                "error": str(e)
            }
    
    async def get_process_status(self) -> List[Dict[str, Any]]:
        """Get status of background processes"""
        # This is a simplified implementation
        # In production, you'd track actual background jobs/processes
        
        processes = [
            {
                "name": "Daily Quote Fetcher",
                "status": "active",
                "last_run": "2024-01-15T08:00:00Z",
                "next_run": "2024-01-16T08:00:00Z",
                "success_rate": 98.5
            },
            {
                "name": "Sentiment Analysis",
                "status": "idle",
                "last_run": "2024-01-15T09:30:00Z",
                "next_run": "on-demand",
                "success_rate": 95.2
            },
            {
                "name": "Vector Generation",
                "status": "idle",
                "last_run": "2024-01-14T14:20:00Z",
                "next_run": "on-demand",
                "success_rate": 92.8
            }
        ]
        
        return processes
    
    async def get_logs(self, level: str = "INFO", limit: int = 100) -> Dict[str, Any]:
        """Get system logs"""
        # This is a simplified implementation
        # In production, you'd read from actual log files or logging system
        
        log_levels = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        
        min_level = log_levels.get(level, 20)
        
        # Sample log entries
        sample_logs = [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "level": "INFO",
                "message": "Daily quote fetch completed successfully",
                "module": "daily_quote"
            },
            {
                "timestamp": "2024-01-15T10:25:00Z",
                "level": "INFO",
                "message": "Starting daily quote fetch process",
                "module": "daily_quote"
            },
            {
                "timestamp": "2024-01-15T09:45:00Z",
                "level": "WARNING",
                "message": "API rate limit approaching",
                "module": "api_client"
            },
            {
                "timestamp": "2024-01-15T09:30:00Z",
                "level": "INFO",
                "message": "Sentiment analysis completed for 150 quotes",
                "module": "sentiment"
            },
            {
                "timestamp": "2024-01-15T08:00:00Z",
                "level": "INFO",
                "message": "System startup completed",
                "module": "main"
            }
        ]
        
        # Filter by log level
        filtered_logs = [
            log for log in sample_logs 
            if log_levels.get(log["level"], 0) >= min_level
        ]
        
        # Limit results
        filtered_logs = filtered_logs[:limit]
        
        return {
            "logs": filtered_logs,
            "total": len(filtered_logs),
            "level_filter": level
        }
    
    async def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics over time"""
        # This is a simplified implementation
        # In production, you'd store and retrieve actual metrics from a time-series database
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Generate sample metrics (in production, query from metrics storage)
        import random
        
        metrics = []
        current_time = start_time
        
        while current_time <= end_time:
            metrics.append({
                "timestamp": current_time.isoformat(),
                "cpu_usage": round(random.uniform(20, 80), 2),
                "memory_usage": round(random.uniform(30, 70), 2),
                "disk_usage": round(random.uniform(40, 60), 2),
                "api_requests": random.randint(50, 200),
                "response_time": round(random.uniform(100, 500), 2)
            })
            current_time += timedelta(minutes=30)
        
        # Calculate summary statistics
        if metrics:
            cpu_values = [m["cpu_usage"] for m in metrics]
            memory_values = [m["memory_usage"] for m in metrics]
            response_times = [m["response_time"] for m in metrics]
            
            summary = {
                "avg_cpu": round(sum(cpu_values) / len(cpu_values), 2),
                "max_cpu": max(cpu_values),
                "avg_memory": round(sum(memory_values) / len(memory_values), 2),
                "max_memory": max(memory_values),
                "avg_response_time": round(sum(response_times) / len(response_times), 2),
                "max_response_time": max(response_times)
            }
        else:
            summary = {}
        
        return {
            "metrics": metrics,
            "summary": summary,
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            }
        }
