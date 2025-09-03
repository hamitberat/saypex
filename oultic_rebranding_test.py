#!/usr/bin/env python3
"""
Oultic Rebranding Verification Tests
Focus on verifying that the backend API has been properly rebranded to Oultic
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = "https://vidflow-15.preview.emergentagent.com/api"

class OulticRebrandingTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_api_title_branding(self):
        """Test that API title shows 'Oultic Video Platform API'"""
        print("\n=== Testing API Title Branding ===")
        
        try:
            # Check if there's an OpenAPI docs endpoint that shows the title
            response = self.make_request("GET", "/docs")
            if response.status_code == 200:
                # Check if the response contains Oultic branding
                content = response.text
                if "Oultic Video Platform API" in content:
                    self.log_result("API Title - Oultic branding in docs", True, "Found 'Oultic Video Platform API' in API docs")
                elif "YouTube Clone API" in content:
                    self.log_result("API Title - Oultic branding in docs", False, "Still shows 'YouTube Clone API' instead of 'Oultic Video Platform API'")
                else:
                    self.log_result("API Title - Oultic branding in docs", False, "Could not find API title in docs")
            else:
                # Try OpenAPI JSON endpoint
                openapi_response = self.make_request("GET", "/openapi.json")
                if openapi_response.status_code == 200:
                    openapi_data = openapi_response.json()
                    api_title = openapi_data.get("info", {}).get("title", "")
                    if api_title == "Oultic Video Platform API":
                        self.log_result("API Title - Oultic branding in OpenAPI", True, f"API title correctly set to: {api_title}")
                    elif "YouTube Clone" in api_title:
                        self.log_result("API Title - Oultic branding in OpenAPI", False, f"API title still shows: {api_title}")
                    else:
                        self.log_result("API Title - Oultic branding in OpenAPI", False, f"Unexpected API title: {api_title}")
                else:
                    self.log_result("API Title - Oultic branding check", False, "Could not access API documentation endpoints")
        except Exception as e:
            self.log_result("API Title - Oultic branding check", False, f"Error: {str(e)}")
    
    def test_health_endpoint_branding(self):
        """Test that health endpoints return proper Oultic branding"""
        print("\n=== Testing Health Endpoint Branding ===")
        
        # Test root health endpoint
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                
                if "Oultic" in message:
                    self.log_result("Health Endpoint - Root Oultic branding", True, f"Message: {message}")
                elif "YouTube Clone" in message:
                    self.log_result("Health Endpoint - Root Oultic branding", False, f"Still shows YouTube Clone: {message}")
                else:
                    self.log_result("Health Endpoint - Root Oultic branding", False, f"Unexpected message: {message}")
            else:
                self.log_result("Health Endpoint - Root Oultic branding", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Health Endpoint - Root Oultic branding", False, f"Error: {str(e)}")
        
        # Test detailed health endpoint
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                service_name = data.get("service", "")
                
                if "oultic" in service_name.lower():
                    self.log_result("Health Endpoint - Service name Oultic branding", True, f"Service: {service_name}")
                elif "youtube" in service_name.lower():
                    self.log_result("Health Endpoint - Service name Oultic branding", False, f"Still shows YouTube: {service_name}")
                else:
                    self.log_result("Health Endpoint - Service name Oultic branding", False, f"Unexpected service name: {service_name}")
            else:
                self.log_result("Health Endpoint - Service name Oultic branding", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Health Endpoint - Service name Oultic branding", False, f"Error: {str(e)}")
    
    def test_core_endpoints_functionality(self):
        """Quick verification that all core endpoints are still functional"""
        print("\n=== Testing Core Endpoints Functionality ===")
        
        # Test videos endpoint
        try:
            response = self.make_request("GET", "/videos/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Core Endpoints - Videos API", True, f"Videos endpoint working, returned {len(data)} items")
                else:
                    self.log_result("Core Endpoints - Videos API", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Core Endpoints - Videos API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Core Endpoints - Videos API", False, f"Error: {str(e)}")
        
        # Test trending endpoint
        try:
            response = self.make_request("GET", "/videos/trending/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Core Endpoints - Trending API", True, f"Trending endpoint working, returned {len(data)} items")
                else:
                    self.log_result("Core Endpoints - Trending API", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Core Endpoints - Trending API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Core Endpoints - Trending API", False, f"Error: {str(e)}")
        
        # Test search endpoint
        try:
            response = self.make_request("GET", "/videos/search/", params={"q": "test"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Core Endpoints - Search API", True, f"Search endpoint working, returned {len(data)} items")
                else:
                    self.log_result("Core Endpoints - Search API", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Core Endpoints - Search API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Core Endpoints - Search API", False, f"Error: {str(e)}")
        
        # Test OAuth providers endpoint
        try:
            response = self.make_request("GET", "/oauth/providers")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Core Endpoints - OAuth API", True, f"OAuth endpoint working, returned {len(data)} providers")
                else:
                    self.log_result("Core Endpoints - OAuth API", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Core Endpoints - OAuth API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Core Endpoints - OAuth API", False, f"Error: {str(e)}")
        
        # Test 2FA info endpoint
        try:
            response = self.make_request("GET", "/2fa/info")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_result("Core Endpoints - 2FA API", True, "2FA endpoint working")
                else:
                    self.log_result("Core Endpoints - 2FA API", False, f"Expected dict, got: {type(data)}")
            else:
                self.log_result("Core Endpoints - 2FA API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Core Endpoints - 2FA API", False, f"Error: {str(e)}")
        
        # Test upload formats endpoint
        try:
            response = self.make_request("GET", "/upload/formats")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict):
                    self.log_result("Core Endpoints - Upload API", True, "Upload endpoint working")
                else:
                    self.log_result("Core Endpoints - Upload API", False, f"Expected dict, got: {type(data)}")
            else:
                self.log_result("Core Endpoints - Upload API", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Core Endpoints - Upload API", False, f"Error: {str(e)}")
    
    def run_oultic_rebranding_tests(self):
        """Run all Oultic rebranding verification tests"""
        print("🎯 Starting Oultic Rebranding Verification Tests")
        print(f"Testing against: {self.base_url}")
        
        # Test API title branding
        self.test_api_title_branding()
        
        # Test health endpoint branding
        self.test_health_endpoint_branding()
        
        # Test core endpoints functionality
        self.test_core_endpoints_functionality()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 OULTIC REBRANDING TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = OulticRebrandingTester()
    success = tester.run_oultic_rebranding_tests()
    sys.exit(0 if success else 1)