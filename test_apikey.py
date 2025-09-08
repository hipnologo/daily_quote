#!/usr/bin/env python3
"""
Robust API key testing script for API Ninjas service.
Tests API key validity, format, and actual API connectivity.
"""

import os
import sys
import logging
from typing import Optional, Dict, Any
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class APIKeyTester:
    """Robust API key tester with comprehensive validation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('API_NINJAS_KEY')
        self.api_url = 'https://api.api-ninjas.com/v1/quotes'
        self.expected_key_length = 40
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create a robust HTTP session with retry strategy."""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def validate_key_format(self) -> bool:
        """Validate API key format and characteristics."""
        if not self.api_key:
            logging.error("API_NINJAS_KEY environment variable not set")
            return False
            
        # Clean the key
        cleaned_key = self.api_key.strip()
        
        # Log key characteristics
        logging.debug(f"API Key Length: {len(cleaned_key)}")
        logging.debug(f"API Key Representation: {repr(cleaned_key)}")
        logging.debug(f"Contains whitespace: {cleaned_key != self.api_key}")
        
        # Validate length
        if len(cleaned_key) != self.expected_key_length:
            logging.error(f"API Key length mismatch. Expected: {self.expected_key_length}, Got: {len(cleaned_key)}")
            return False
            
        # Validate character set (alphanumeric)
        if not cleaned_key.isalnum():
            logging.warning("API Key contains non-alphanumeric characters")
            
        logging.info("API Key format validation passed")
        self.api_key = cleaned_key
        return True
    
    def test_api_connectivity(self) -> Dict[str, Any]:
        """Test actual API connectivity and response."""
        if not self.api_key:
            return {"success": False, "error": "No API key available"}
            
        headers = {'X-Api-Key': self.api_key}
        
        try:
            logging.info(f"Testing API connectivity to {self.api_url}")
            response = self.session.get(
                self.api_url,
                headers=headers,
                timeout=10
            )
            
            result = {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content)
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result["quote_count"] = len(data) if isinstance(data, list) else 1
                    logging.info(f"API test successful: {result['quote_count']} quotes received")
                except ValueError:
                    result["error"] = "Invalid JSON response"
                    logging.error("Received non-JSON response")
            else:
                result["error"] = response.text[:200]  # Truncate error message
                logging.error(f"API request failed: {response.status_code} - {result['error']}")
                
            return result
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def run_comprehensive_test(self) -> bool:
        """Run all tests and return overall success status."""
        logging.info("Starting comprehensive API key test")
        
        # Test 1: Format validation
        if not self.validate_key_format():
            return False
            
        # Test 2: API connectivity
        api_result = self.test_api_connectivity()
        
        if api_result["success"]:
            logging.info("✅ All tests passed - API key is valid and functional")
            return True
        else:
            logging.error(f"❌ API connectivity test failed: {api_result.get('error', 'Unknown error')}")
            return False


def configure_logging(level: str = "INFO") -> None:
    """Configure logging with appropriate format and level."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main() -> int:
    """Main function with proper exit codes."""
    configure_logging("DEBUG")
    
    tester = APIKeyTester()
    success = tester.run_comprehensive_test()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
