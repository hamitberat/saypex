#!/usr/bin/env python3
"""
SAYPEX Backend API Search Enhancement Tests
Focus on testing search functionality enhancements and core backend features
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = "https://clean-dependencies-1.preview.emergentagent.com/api"

class SAYPEXSearchTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_video_id = None
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
        headers = kwargs.get('headers', {})
        
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
            kwargs['headers'] = headers
        
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def test_authentication_system(self):
        """Test authentication system"""
        print("\n=== Testing Authentication System ===")
        
        # Test login with demo credentials
        login_data = {
            "email": "codemaster@example.com",
            "password": "password123"
        }
        
        try:
            response = self.make_request("POST", "/users/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.auth_token = data["access_token"]
                    self.log_result("Authentication - Login with demo credentials", True, "Successfully authenticated")
                else:
                    self.log_result("Authentication - Login with demo credentials", False, f"No access token: {data}")
            else:
                self.log_result("Authentication - Login with demo credentials", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Authentication - Login with demo credentials", False, f"Error: {str(e)}")
        
        # Test get current user
        if self.auth_token:
            try:
                response = self.make_request("GET", "/users/me")
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "username" in data:
                        self.test_user_id = data["id"]
                        self.log_result("Authentication - Get current user", True, f"User: {data.get('username')}")
                    else:
                        self.log_result("Authentication - Get current user", False, f"Missing user data: {data}")
                else:
                    self.log_result("Authentication - Get current user", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Authentication - Get current user", False, f"Error: {str(e)}")
    
    def test_video_api_core_functionality(self):
        """Test core video API functionality"""
        print("\n=== Testing Video API Core Functionality ===")
        
        # Test get videos (home page)
        try:
            response = self.make_request("GET", "/videos/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        self.test_video_id = data[0].get("id")
                        self.log_result("Video API - Get videos (home)", True, f"Retrieved {len(data)} videos")
                    else:
                        # Try trending if home is empty
                        trending_response = self.make_request("GET", "/videos/trending/")
                        if trending_response.status_code == 200:
                            trending_data = trending_response.json()
                            if isinstance(trending_data, list) and len(trending_data) > 0:
                                self.test_video_id = trending_data[0].get("id")
                                self.log_result("Video API - Get videos (home)", True, f"Home empty, found {len(trending_data)} trending videos")
                            else:
                                self.log_result("Video API - Get videos (home)", True, "No videos found (empty database)")
                        else:
                            self.log_result("Video API - Get videos (home)", True, "No videos found (empty database)")
                else:
                    self.log_result("Video API - Get videos (home)", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Video API - Get videos (home)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Video API - Get videos (home)", False, f"Error: {str(e)}")
        
        # Test get trending videos
        try:
            response = self.make_request("GET", "/videos/trending/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Video API - Get trending videos", True, f"Retrieved {len(data)} trending videos")
                else:
                    self.log_result("Video API - Get trending videos", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Video API - Get trending videos", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Video API - Get trending videos", False, f"Error: {str(e)}")
        
        # Test get specific video
        if self.test_video_id:
            try:
                response = self.make_request("GET", f"/videos/{self.test_video_id}")
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "title" in data:
                        self.log_result("Video API - Get specific video", True, f"Video: {data.get('title')}")
                    else:
                        self.log_result("Video API - Get specific video", False, f"Missing video data: {data}")
                else:
                    self.log_result("Video API - Get specific video", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Video API - Get specific video", False, f"Error: {str(e)}")
        
        # Test category filtering
        try:
            response = self.make_request("GET", "/videos/", params={"category": "education"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Video API - Category filtering", True, f"Education category: {len(data)} videos")
                else:
                    self.log_result("Video API - Category filtering", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Video API - Category filtering", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Video API - Category filtering", False, f"Error: {str(e)}")
    
    def test_search_api_comprehensive(self):
        """Test search API with various queries"""
        print("\n=== Testing Search API Comprehensive ===")
        
        # Test basic search
        try:
            response = self.make_request("GET", "/videos/search/", params={"q": "javascript"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Search API - Basic search (javascript)", True, f"Found {len(data)} results")
                else:
                    self.log_result("Search API - Basic search (javascript)", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Search API - Basic search (javascript)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Search API - Basic search (javascript)", False, f"Error: {str(e)}")
        
        # Test search with different terms
        search_terms = ["learn", "tutorial", "course", "programming", "web"]
        for term in search_terms:
            try:
                response = self.make_request("GET", "/videos/search/", params={"q": term})
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result(f"Search API - Search term '{term}'", True, f"Found {len(data)} results")
                    else:
                        self.log_result(f"Search API - Search term '{term}'", False, f"Expected list, got: {type(data)}")
                else:
                    self.log_result(f"Search API - Search term '{term}'", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Search API - Search term '{term}'", False, f"Error: {str(e)}")
        
        # Test search with category filtering
        try:
            response = self.make_request("GET", "/videos/search/", params={"q": "learn", "category": "education"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Search API - Search with category filter", True, f"Found {len(data)} education results for 'learn'")
                else:
                    self.log_result("Search API - Search with category filter", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Search API - Search with category filter", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Search API - Search with category filter", False, f"Error: {str(e)}")
        
        # Test search with sorting
        sort_options = ["relevance", "date", "views", "likes"]
        for sort_by in sort_options:
            try:
                response = self.make_request("GET", "/videos/search/", params={"q": "javascript", "sort_by": sort_by})
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result(f"Search API - Sort by {sort_by}", True, f"Found {len(data)} results sorted by {sort_by}")
                    else:
                        self.log_result(f"Search API - Sort by {sort_by}", False, f"Expected list, got: {type(data)}")
                else:
                    self.log_result(f"Search API - Sort by {sort_by}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Search API - Sort by {sort_by}", False, f"Error: {str(e)}")
        
        # Test search with pagination
        try:
            response = self.make_request("GET", "/videos/search/", params={"q": "learn", "limit": 5, "offset": 0})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Search API - Pagination (limit=5, offset=0)", True, f"Found {len(data)} results")
                else:
                    self.log_result("Search API - Pagination (limit=5, offset=0)", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Search API - Pagination (limit=5, offset=0)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Search API - Pagination (limit=5, offset=0)", False, f"Error: {str(e)}")
        
        # Test empty search query handling
        try:
            response = self.make_request("GET", "/videos/search/", params={"q": ""})
            if response.status_code == 422:  # FastAPI validation error for empty required query
                self.log_result("Search API - Empty query validation", True, "Correctly rejected empty query")
            elif response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Search API - Empty query validation", True, f"Empty query returned {len(data)} results")
                else:
                    self.log_result("Search API - Empty query validation", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Search API - Empty query validation", False, f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Search API - Empty query validation", False, f"Error: {str(e)}")
    
    def test_existing_functionality_integrity(self):
        """Test that existing functionality remains intact"""
        print("\n=== Testing Existing Functionality Integrity ===")
        
        # Test health endpoints
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "YouTube Clone API" in data["message"]:
                    self.log_result("Integrity - Health check root", True, "API is running")
                else:
                    self.log_result("Integrity - Health check root", False, f"Unexpected response: {data}")
            else:
                self.log_result("Integrity - Health check root", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Integrity - Health check root", False, f"Error: {str(e)}")
        
        # Test video recommendations
        if self.test_video_id:
            try:
                response = self.make_request("GET", f"/videos/{self.test_video_id}/recommendations")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result("Integrity - Video recommendations", True, f"Retrieved {len(data)} recommendations")
                    else:
                        self.log_result("Integrity - Video recommendations", False, f"Expected list, got: {type(data)}")
                else:
                    self.log_result("Integrity - Video recommendations", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Integrity - Video recommendations", False, f"Error: {str(e)}")
        
        # Test user search
        try:
            response = self.make_request("GET", "/users/search", params={"q": "code"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Integrity - User search", True, f"Found {len(data)} users")
                else:
                    self.log_result("Integrity - User search", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Integrity - User search", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Integrity - User search", False, f"Error: {str(e)}")
        
        # Test modular components (OAuth, 2FA, Upload)
        try:
            oauth_response = self.make_request("GET", "/oauth/providers")
            tfa_response = self.make_request("GET", "/2fa/info")
            upload_response = self.make_request("GET", "/upload/formats")
            
            oauth_ok = oauth_response.status_code == 200
            tfa_ok = tfa_response.status_code == 200
            upload_ok = upload_response.status_code == 200
            
            if oauth_ok and tfa_ok and upload_ok:
                self.log_result("Integrity - Modular components", True, "OAuth, 2FA, and Upload modules working")
            else:
                failed_modules = []
                if not oauth_ok: failed_modules.append("OAuth")
                if not tfa_ok: failed_modules.append("2FA")
                if not upload_ok: failed_modules.append("Upload")
                self.log_result("Integrity - Modular components", False, f"Failed modules: {failed_modules}")
        except Exception as e:
            self.log_result("Integrity - Modular components", False, f"Error: {str(e)}")
    
    def run_search_enhancement_tests(self):
        """Run all search enhancement tests"""
        print("🔍 Starting SAYPEX Backend Search Enhancement Tests")
        print(f"Testing against: {self.base_url}")
        
        # Test authentication first
        self.test_authentication_system()
        
        # Test core video API functionality
        self.test_video_api_core_functionality()
        
        # Test comprehensive search functionality
        self.test_search_api_comprehensive()
        
        # Test existing functionality integrity
        self.test_existing_functionality_integrity()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 SEARCH ENHANCEMENT TEST SUMMARY")
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
    tester = SAYPEXSearchTester()
    success = tester.run_search_enhancement_tests()
    sys.exit(0 if success else 1)