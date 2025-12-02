from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import shutil
from datetime import datetime

class FileService:
    def __init__(self, db: Session):
        self.db = db
        # Check Docker path first, then local dev path
        docker_path = Path("/app")
        local_path = Path(__file__).parent.parent.parent.parent
        
        if (docker_path / "quotes.txt").exists():
            self.quotes_base_path = docker_path
        else:
            self.quotes_base_path = local_path
    
    async def list_quote_files(self) -> List[Dict[str, Any]]:
        """List all quote files"""
        files = []
        patterns = ["quotes.txt", "quotes_*.txt"]
        
        for pattern in patterns:
            for file_path in self.quotes_base_path.glob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "lines": self._count_lines(file_path)
                    })
        
        return sorted(files, key=lambda x: x["filename"])
    
    async def read_file_content(self, filename: str) -> Dict[str, Any]:
        """Read content of a quote file"""
        file_path = self.quotes_base_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            lines = content.split('\n')
            quotes = [line.strip() for line in lines if line.strip()]
            
            return {
                "filename": filename,
                "quote_count": len(quotes),
                "quotes": quotes[:100],  # Limit to first 100 for preview
                "total_lines": len(quotes)
            }
        except Exception as e:
            raise Exception(f"Error reading file {filename}: {str(e)}")
    
    async def backup_file(self, filename: str) -> str:
        """Create backup of a quote file"""
        file_path = self.quotes_base_path / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        backup_path = file_path.parent / backup_name
        
        shutil.copy2(file_path, backup_path)
        
        return backup_name
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0
