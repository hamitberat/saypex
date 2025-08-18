#!/usr/bin/env python3
"""
YouTube Clone Backend API Test Suite
Tests all backend endpoints for functionality and error handling
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = "https://saypex-stream.preview.emergentagent.com/api"

class YouTubeCloneAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_video_id = None
        self.test_comment_id = None
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
    
    def test_health_check(self):
        """Test health check endpoints"""
        print("\n=== Testing Health Check Endpoints ===")
        
        # Test root endpoint
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "YouTube Clone API" in data["message"]:
                    self.log_result("Health check root endpoint", True)
                else:
                    self.log_result("Health check root endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health check root endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Health check root endpoint", False, f"Error: {str(e)}")
        
        # Test health endpoint
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                if "status" in data and data["status"] == "healthy":
                    self.log_result("Health check /health endpoint", True)
                else:
                    self.log_result("Health check /health endpoint", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health check /health endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Health check /health endpoint", False, f"Error: {str(e)}")
    
    def test_user_registration(self):
        """Test user registration"""
        print("\n=== Testing User Registration ===")
        
        user_data = {
            "username": "testuser_youtube",
            "email": "testuser@youtube.com",
            "password": "SecurePass123!",
            "full_name": "Test User YouTube"
        }
        
        try:
            response = self.make_request("POST", "/users/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "username" in data:
                    self.test_user_id = data["id"]
                    self.log_result("User registration", True, f"User ID: {self.test_user_id}")
                else:
                    self.log_result("User registration", False, f"Missing user data: {data}")
            else:
                # Check if user already exists
                if response.status_code == 400:
                    self.log_result("User registration", True, "User already exists (expected for repeated tests)")
                else:
                    self.log_result("User registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User registration", False, f"Error: {str(e)}")
    
    def test_user_login(self):
        """Test user login"""
        print("\n=== Testing User Login ===")
        
        # Try with existing user from populate script first
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
                    self.log_result("User login", True, "Token received")
                    return
                else:
                    self.log_result("User login", False, f"No access token: {data}")
            else:
                # Try with test user if existing user fails
                login_data = {
                    "email": "testuser@youtube.com",
                    "password": "SecurePass123!"
                }
                response = self.make_request("POST", "/users/login", json=login_data)
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.auth_token = data["access_token"]
                        self.log_result("User login", True, "Token received")
                    else:
                        self.log_result("User login", False, f"No access token: {data}")
                else:
                    self.log_result("User login", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User login", False, f"Error: {str(e)}")
    
    def test_get_current_user(self):
        """Test get current user profile"""
        print("\n=== Testing Get Current User Profile ===")
        
        if not self.auth_token:
            self.log_result("Get current user profile", False, "No auth token available")
            return
        
        try:
            response = self.make_request("GET", "/users/me")
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "username" in data:
                    self.test_user_id = data["id"]
                    self.log_result("Get current user profile", True, f"User: {data.get('username')}")
                else:
                    self.log_result("Get current user profile", False, f"Missing user data: {data}")
            else:
                self.log_result("Get current user profile", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get current user profile", False, f"Error: {str(e)}")
    
    def test_get_videos(self):
        """Test get videos for home page"""
        print("\n=== Testing Get Videos (Home Page) ===")
        
        try:
            response = self.make_request("GET", "/videos/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    if len(data) > 0:
                        # Store first video ID for later tests
                        self.test_video_id = data[0].get("id")
                        self.log_result("Get videos (home page)", True, f"Retrieved {len(data)} videos")
                    else:
                        self.log_result("Get videos (home page)", True, "No videos found (empty database)")
                else:
                    self.log_result("Get videos (home page)", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Get videos (home page)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get videos (home page)", False, f"Error: {str(e)}")
    
    def test_search_videos(self):
        """Test video search"""
        print("\n=== Testing Video Search ===")
        
        try:
            response = self.make_request("GET", "/videos/search", params={"q": "test"})
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Video search", True, f"Search returned {len(data)} results")
                else:
                    self.log_result("Video search", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Video search", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Video search", False, f"Error: {str(e)}")
    
    def test_get_trending_videos(self):
        """Test get trending videos"""
        print("\n=== Testing Get Trending Videos ===")
        
        try:
            response = self.make_request("GET", "/videos/trending")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get trending videos", True, f"Retrieved {len(data)} trending videos")
                else:
                    self.log_result("Get trending videos", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Get trending videos", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get trending videos", False, f"Error: {str(e)}")
    
    def test_get_specific_video(self):
        """Test get specific video by ID"""
        print("\n=== Testing Get Specific Video ===")
        
        if not self.test_video_id:
            self.log_result("Get specific video", False, "No video ID available for testing")
            return
        
        try:
            response = self.make_request("GET", f"/videos/{self.test_video_id}")
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "title" in data:
                    self.log_result("Get specific video", True, f"Video: {data.get('title')}")
                else:
                    self.log_result("Get specific video", False, f"Missing video data: {data}")
            else:
                self.log_result("Get specific video", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get specific video", False, f"Error: {str(e)}")
    
    def test_get_video_recommendations(self):
        """Test get video recommendations"""
        print("\n=== Testing Get Video Recommendations ===")
        
        if not self.test_video_id:
            self.log_result("Get video recommendations", False, "No video ID available for testing")
            return
        
        try:
            response = self.make_request("GET", f"/videos/{self.test_video_id}/recommendations")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_result("Get video recommendations", True, f"Retrieved {len(data)} recommendations")
                else:
                    self.log_result("Get video recommendations", False, f"Expected list, got: {type(data)}")
            else:
                self.log_result("Get video recommendations", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get video recommendations", False, f"Error: {str(e)}")
    
    def test_get_video_comments(self):
        """Test get video comments"""
        print("\n=== Testing Get Video Comments ===")
        
        if not self.test_video_id:
            self.log_result("Get video comments", False, "No video ID available for testing")
            return
        
        try:
            response = self.make_request("GET", f"/comments/video/{self.test_video_id}")
            if response.status_code == 200:
                data = response.json()
                if "comments" in data and isinstance(data["comments"], list):
                    self.log_result("Get video comments", True, f"Retrieved {len(data['comments'])} comments")
                else:
                    self.log_result("Get video comments", False, f"Unexpected response structure: {data}")
            else:
                self.log_result("Get video comments", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Get video comments", False, f"Error: {str(e)}")
    
    def test_create_comment(self):
        """Test create comment"""
        print("\n=== Testing Create Comment ===")
        
        if not self.auth_token:
            self.log_result("Create comment", False, "No auth token available")
            return
        
        if not self.test_video_id:
            self.log_result("Create comment", False, "No video ID available for testing")
            return
        
        comment_data = {
            "video_id": self.test_video_id,
            "content": "This is a test comment for the YouTube clone API testing!"
        }
        
        try:
            response = self.make_request("POST", "/comments", json=comment_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "content" in data:
                    self.test_comment_id = data["id"]
                    self.log_result("Create comment", True, f"Comment created: {data.get('content')[:50]}...")
                else:
                    self.log_result("Create comment", False, f"Missing comment data: {data}")
            else:
                self.log_result("Create comment", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Create comment", False, f"Error: {str(e)}")
    
    def test_modular_upload_module(self):
        """Test Upload Module - Modular Monolith Architecture"""
        print("\n=== Testing Upload Module (Modular Architecture) ===")
        
        # Test supported formats endpoint
        try:
            response = self.make_request("GET", "/upload/formats")
            if response.status_code == 200:
                data = response.json()
                if "video_formats" in data and "thumbnail_formats" in data:
                    self.log_result("Upload Module - Get supported formats", True, f"Formats: {len(data['video_formats'])} video, {len(data['thumbnail_formats'])} thumbnail")
                else:
                    self.log_result("Upload Module - Get supported formats", False, f"Missing format data: {data}")
            else:
                self.log_result("Upload Module - Get supported formats", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Upload Module - Get supported formats", False, f"Error: {str(e)}")
        
        # Test my-videos endpoint (requires auth)
        if self.auth_token:
            try:
                response = self.make_request("GET", "/upload/my-videos")
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_result("Upload Module - Get my videos", True, f"Retrieved {len(data)} user videos")
                    else:
                        self.log_result("Upload Module - Get my videos", False, f"Expected list, got: {type(data)}")
                else:
                    self.log_result("Upload Module - Get my videos", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Upload Module - Get my videos", False, f"Error: {str(e)}")
        else:
            self.log_result("Upload Module - Get my videos", False, "No auth token available")
    
    def test_modular_oauth_module(self):
        """Test OAuth Module - Modular Monolith Architecture"""
        print("\n=== Testing OAuth Module (Modular Architecture) ===")
        
        # Test OAuth providers endpoint
        try:
            response = self.make_request("GET", "/oauth/providers")
            if response.status_code == 200:
                data = response.json()
                if "providers" in data and isinstance(data["providers"], list):
                    providers = [p["name"] for p in data["providers"]]
                    expected_providers = ["google", "facebook"]
                    if all(provider in providers for provider in expected_providers):
                        self.log_result("OAuth Module - Get providers", True, f"Providers: {providers}")
                    else:
                        self.log_result("OAuth Module - Get providers", False, f"Missing expected providers. Got: {providers}")
                else:
                    self.log_result("OAuth Module - Get providers", False, f"Invalid response structure: {data}")
            else:
                self.log_result("OAuth Module - Get providers", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("OAuth Module - Get providers", False, f"Error: {str(e)}")
        
        # Test OAuth login initiation (Google)
        try:
            response = self.make_request("GET", "/oauth/google/login", params={"redirect_uri": "https://example.com/callback"})
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data and "provider" in data:
                    self.log_result("OAuth Module - Google login initiation", True, f"Provider: {data['provider']}")
                else:
                    self.log_result("OAuth Module - Google login initiation", False, f"Missing auth data: {data}")
            else:
                self.log_result("OAuth Module - Google login initiation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("OAuth Module - Google login initiation", False, f"Error: {str(e)}")
        
        # Test OAuth login initiation (Facebook)
        try:
            response = self.make_request("GET", "/oauth/facebook/login", params={"redirect_uri": "https://example.com/callback"})
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data and "provider" in data:
                    self.log_result("OAuth Module - Facebook login initiation", True, f"Provider: {data['provider']}")
                else:
                    self.log_result("OAuth Module - Facebook login initiation", False, f"Missing auth data: {data}")
            else:
                self.log_result("OAuth Module - Facebook login initiation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("OAuth Module - Facebook login initiation", False, f"Error: {str(e)}")
    
    def test_modular_2fa_module(self):
        """Test 2FA Module - Modular Monolith Architecture"""
        print("\n=== Testing 2FA Module (Modular Architecture) ===")
        
        # Test 2FA information endpoint
        try:
            response = self.make_request("GET", "/2fa/info")
            if response.status_code == 200:
                data = response.json()
                if "supported_methods" in data and "issuer" in data:
                    methods = [method["name"] for method in data["supported_methods"]]
                    expected_methods = ["totp", "backup_codes"]
                    if all(method in methods for method in expected_methods):
                        self.log_result("2FA Module - Get 2FA info", True, f"Methods: {methods}, Issuer: {data['issuer']}")
                    else:
                        self.log_result("2FA Module - Get 2FA info", False, f"Missing expected methods. Got: {methods}")
                else:
                    self.log_result("2FA Module - Get 2FA info", False, f"Invalid response structure: {data}")
            else:
                self.log_result("2FA Module - Get 2FA info", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("2FA Module - Get 2FA info", False, f"Error: {str(e)}")
        
        # Test 2FA status endpoint (requires auth)
        if self.auth_token:
            try:
                response = self.make_request("GET", "/2fa/status")
                if response.status_code == 200:
                    data = response.json()
                    if "enabled" in data:
                        self.log_result("2FA Module - Get 2FA status", True, f"2FA enabled: {data['enabled']}")
                    else:
                        self.log_result("2FA Module - Get 2FA status", False, f"Missing status data: {data}")
                else:
                    self.log_result("2FA Module - Get 2FA status", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("2FA Module - Get 2FA status", False, f"Error: {str(e)}")
        else:
            self.log_result("2FA Module - Get 2FA status", False, "No auth token available")
        
        # Test 2FA verify-login endpoint (informational)
        try:
            response = self.make_request("POST", "/2fa/verify-login", json={"code": "123456"})
            if response.status_code == 200:
                data = response.json()
                if "supported_methods" in data:
                    self.log_result("2FA Module - Verify login endpoint", True, f"Methods: {data['supported_methods']}")
                else:
                    self.log_result("2FA Module - Verify login endpoint", False, f"Missing method data: {data}")
            else:
                self.log_result("2FA Module - Verify login endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("2FA Module - Verify login endpoint", False, f"Error: {str(e)}")
    
    def test_modular_architecture_boundaries(self):
        """Test Modular Architecture Boundaries and Integration"""
        print("\n=== Testing Modular Architecture Boundaries ===")
        
        # Test that modules are independently accessible
        modules_tested = []
        
        # Upload module independence
        try:
            response = self.make_request("GET", "/upload/formats")
            if response.status_code == 200:
                modules_tested.append("upload")
        except:
            pass
        
        # OAuth module independence
        try:
            response = self.make_request("GET", "/oauth/providers")
            if response.status_code == 200:
                modules_tested.append("oauth")
        except:
            pass
        
        # 2FA module independence
        try:
            response = self.make_request("GET", "/2fa/info")
            if response.status_code == 200:
                modules_tested.append("2fa")
        except:
            pass
        
        # Core modules (users, videos)
        try:
            response = self.make_request("GET", "/")
            if response.status_code == 200:
                modules_tested.append("core")
        except:
            pass
        
        if len(modules_tested) >= 3:
            self.log_result("Modular Architecture - Module Independence", True, f"Modules accessible: {modules_tested}")
        else:
            self.log_result("Modular Architecture - Module Independence", False, f"Only {len(modules_tested)} modules accessible: {modules_tested}")
        
        # Test single deployment unit (all modules in same API)
        try:
            base_response = self.make_request("GET", "/")
            upload_response = self.make_request("GET", "/upload/formats")
            oauth_response = self.make_request("GET", "/oauth/providers")
            tfa_response = self.make_request("GET", "/2fa/info")
            
            all_same_host = all(
                response.url.split('/api')[0] == base_response.url.split('/api')[0]
                for response in [upload_response, oauth_response, tfa_response]
                if response.status_code == 200
            )
            
            if all_same_host:
                self.log_result("Modular Architecture - Single Deployment Unit", True, "All modules deployed together")
            else:
                self.log_result("Modular Architecture - Single Deployment Unit", False, "Modules appear to be deployed separately")
        except Exception as e:
            self.log_result("Modular Architecture - Single Deployment Unit", False, f"Error: {str(e)}")
    
    def test_error_cases(self):
        """Test error handling"""
        print("\n=== Testing Error Cases ===")
        
        # Test invalid video ID
        try:
            response = self.make_request("GET", "/videos/invalid-video-id")
            if response.status_code == 404:
                self.log_result("Error handling - Invalid video ID", True, "Correctly returned 404")
            else:
                self.log_result("Error handling - Invalid video ID", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("Error handling - Invalid video ID", False, f"Error: {str(e)}")
        
        # Test unauthorized access to protected endpoint
        try:
            # Temporarily remove auth token
            temp_token = self.auth_token
            self.auth_token = None
            
            response = self.make_request("GET", "/users/me")
            if response.status_code == 401:
                self.log_result("Error handling - Unauthorized access", True, "Correctly returned 401")
            else:
                self.log_result("Error handling - Unauthorized access", False, f"Expected 401, got {response.status_code}")
            
            # Restore auth token
            self.auth_token = temp_token
        except Exception as e:
            self.log_result("Error handling - Unauthorized access", False, f"Error: {str(e)}")
        
        # Test invalid login credentials
        try:
            invalid_login = {
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
            response = self.make_request("POST", "/users/login", json=invalid_login)
            if response.status_code == 401:
                self.log_result("Error handling - Invalid login", True, "Correctly returned 401")
            else:
                self.log_result("Error handling - Invalid login", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Error handling - Invalid login", False, f"Error: {str(e)}")
        
        # Test invalid OAuth provider
        try:
            response = self.make_request("GET", "/oauth/invalid-provider/login", params={"redirect_uri": "https://example.com"})
            if response.status_code == 400:
                self.log_result("Error handling - Invalid OAuth provider", True, "Correctly returned 400")
            else:
                self.log_result("Error handling - Invalid OAuth provider", False, f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Error handling - Invalid OAuth provider", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting YouTube Clone Backend API Tests")
        print(f"Testing against: {self.base_url}")
        
        # Run tests in order
        self.test_health_check()
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        self.test_get_videos()
        self.test_search_videos()
        self.test_get_trending_videos()
        self.test_get_specific_video()
        self.test_get_video_recommendations()
        self.test_get_video_comments()
        self.test_create_comment()
        self.test_error_cases()
        
        # Print summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📈 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = YouTubeCloneAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)