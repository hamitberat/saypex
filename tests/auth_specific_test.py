#!/usr/bin/env python3
"""
SAYPEX Authentication System Specific Tests
Focus on authentication endpoints as requested in the review
"""

import requests
import json
import sys
import os
from typing import Dict, Any, Optional

# Get backend URL from environment
BACKEND_URL = "https://clean-dependencies-1.preview.emergentagent.com/api"

class SAYPEXAuthTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
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
    
    def test_user_registration_comprehensive(self):
        """Test user registration with comprehensive validation"""
        print("\n=== Testing User Registration API (/api/users/register) ===")
        
        # Test 1: Valid registration
        user_data = {
            "username": "saypex_testuser",
            "email": "saypex_test@example.com",
            "password": "SecurePassword123!",
            "full_name": "SAYPEX Test User"
        }
        
        try:
            response = self.make_request("POST", "/users/register", json=user_data)
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "username" in data and "email" in data:
                    self.test_user_id = data["id"]
                    self.log_result("User registration with valid data", True, 
                                  f"User created: {data['username']} ({data['email']})")
                    
                    # Verify password is not returned
                    if "password" not in data and "password_hash" not in data:
                        self.log_result("Password security check", True, "Password not exposed in response")
                    else:
                        self.log_result("Password security check", False, "Password data exposed in response")
                else:
                    self.log_result("User registration with valid data", False, f"Missing required fields: {data}")
            elif response.status_code == 400:
                # User might already exist from previous tests
                self.log_result("User registration with valid data", True, 
                              "User already exists (expected for repeated tests)")
            else:
                self.log_result("User registration with valid data", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User registration with valid data", False, f"Error: {str(e)}")
        
        # Test 2: Duplicate email handling
        try:
            duplicate_email_data = {
                "username": "different_username",
                "email": "saypex_test@example.com",  # Same email
                "password": "AnotherPassword123!",
                "full_name": "Another User"
            }
            response = self.make_request("POST", "/users/register", json=duplicate_email_data)
            if response.status_code == 400:
                self.log_result("Duplicate email handling", True, "Correctly rejected duplicate email")
            else:
                self.log_result("Duplicate email handling", False, 
                              f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Duplicate email handling", False, f"Error: {str(e)}")
        
        # Test 3: Duplicate username handling
        try:
            duplicate_username_data = {
                "username": "saypex_testuser",  # Same username
                "email": "different_email@example.com",
                "password": "AnotherPassword123!",
                "full_name": "Another User"
            }
            response = self.make_request("POST", "/users/register", json=duplicate_username_data)
            if response.status_code == 400:
                self.log_result("Duplicate username handling", True, "Correctly rejected duplicate username")
            else:
                self.log_result("Duplicate username handling", False, 
                              f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("Duplicate username handling", False, f"Error: {str(e)}")
        
        # Test 4: Required fields validation
        try:
            incomplete_data = {
                "username": "incomplete_user",
                # Missing email and password
            }
            response = self.make_request("POST", "/users/register", json=incomplete_data)
            if response.status_code == 422:  # FastAPI validation error
                self.log_result("Required fields validation", True, "Correctly rejected incomplete data")
            else:
                self.log_result("Required fields validation", False, 
                              f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Required fields validation", False, f"Error: {str(e)}")
    
    def test_user_login_comprehensive(self):
        """Test user login with comprehensive scenarios"""
        print("\n=== Testing User Login API (/api/users/login) ===")
        
        # Test 1: Login with existing demo account
        demo_login_data = {
            "email": "codemaster@example.com",
            "password": "password123"
        }
        
        try:
            response = self.make_request("POST", "/users/login", json=demo_login_data)
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data and "token_type" in data and "user" in data:
                    self.auth_token = data["access_token"]
                    user_data = data["user"]
                    self.log_result("Demo account login", True, 
                                  f"Token received for user: {user_data.get('username')}")
                    
                    # Verify token format
                    if data["token_type"] == "bearer":
                        self.log_result("JWT token format", True, "Bearer token format correct")
                    else:
                        self.log_result("JWT token format", False, f"Unexpected token type: {data['token_type']}")
                    
                    # Verify user data structure
                    required_fields = ["id", "username", "email", "role", "status"]
                    missing_fields = [field for field in required_fields if field not in user_data]
                    if not missing_fields:
                        self.log_result("User data structure", True, "All required user fields present")
                    else:
                        self.log_result("User data structure", False, f"Missing fields: {missing_fields}")
                else:
                    self.log_result("Demo account login", False, f"Missing auth data: {data}")
            else:
                self.log_result("Demo account login", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Demo account login", False, f"Error: {str(e)}")
        
        # Test 2: Invalid credentials handling
        try:
            invalid_login_data = {
                "email": "codemaster@example.com",
                "password": "wrongpassword"
            }
            response = self.make_request("POST", "/users/login", json=invalid_login_data)
            if response.status_code == 401:
                self.log_result("Invalid password handling", True, "Correctly rejected invalid password")
            else:
                self.log_result("Invalid password handling", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Invalid password handling", False, f"Error: {str(e)}")
        
        # Test 3: Non-existent user handling
        try:
            nonexistent_login_data = {
                "email": "nonexistent@example.com",
                "password": "anypassword"
            }
            response = self.make_request("POST", "/users/login", json=nonexistent_login_data)
            if response.status_code == 401:
                self.log_result("Non-existent user handling", True, "Correctly rejected non-existent user")
            else:
                self.log_result("Non-existent user handling", False, 
                              f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Non-existent user handling", False, f"Error: {str(e)}")
        
        # Test 4: Missing credentials validation
        try:
            incomplete_login_data = {
                "email": "test@example.com"
                # Missing password
            }
            response = self.make_request("POST", "/users/login", json=incomplete_login_data)
            if response.status_code == 422:  # FastAPI validation error
                self.log_result("Login credentials validation", True, "Correctly rejected incomplete credentials")
            else:
                self.log_result("Login credentials validation", False, 
                              f"Expected 422, got {response.status_code}")
        except Exception as e:
            self.log_result("Login credentials validation", False, f"Error: {str(e)}")
    
    def test_protected_routes_comprehensive(self):
        """Test protected routes with comprehensive JWT validation"""
        print("\n=== Testing Protected Routes ===")
        
        # Test 1: Access with valid JWT token
        if self.auth_token:
            try:
                response = self.make_request("GET", "/users/me")
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "username" in data and "email" in data:
                        self.log_result("Protected route with valid token", True, 
                                      f"Successfully accessed profile: {data.get('username')}")
                    else:
                        self.log_result("Protected route with valid token", False, 
                                      f"Missing user data: {data}")
                else:
                    self.log_result("Protected route with valid token", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("Protected route with valid token", False, f"Error: {str(e)}")
        else:
            self.log_result("Protected route with valid token", False, "No auth token available")
        
        # Test 2: Access without authentication
        try:
            # Temporarily remove auth token
            temp_token = self.auth_token
            self.auth_token = None
            
            response = self.make_request("GET", "/users/me")
            if response.status_code == 401:
                self.log_result("Protected route without token", True, "Correctly rejected unauthenticated request")
            else:
                self.log_result("Protected route without token", False, 
                              f"Expected 401, got {response.status_code}")
            
            # Restore auth token
            self.auth_token = temp_token
        except Exception as e:
            self.log_result("Protected route without token", False, f"Error: {str(e)}")
        
        # Test 3: Access with invalid JWT token
        try:
            # Use invalid token
            temp_token = self.auth_token
            self.auth_token = "invalid.jwt.token"
            
            response = self.make_request("GET", "/users/me")
            if response.status_code == 401:
                self.log_result("Protected route with invalid token", True, "Correctly rejected invalid token")
            else:
                self.log_result("Protected route with invalid token", False, 
                              f"Expected 401, got {response.status_code}")
            
            # Restore auth token
            self.auth_token = temp_token
        except Exception as e:
            self.log_result("Protected route with invalid token", False, f"Error: {str(e)}")
        
        # Test 4: Access with malformed token
        try:
            # Use malformed token
            temp_token = self.auth_token
            self.auth_token = "malformed-token"
            
            response = self.make_request("GET", "/users/me")
            if response.status_code == 401:
                self.log_result("Protected route with malformed token", True, "Correctly rejected malformed token")
            else:
                self.log_result("Protected route with malformed token", False, 
                              f"Expected 401, got {response.status_code}")
            
            # Restore auth token
            self.auth_token = temp_token
        except Exception as e:
            self.log_result("Protected route with malformed token", False, f"Error: {str(e)}")
    
    def test_database_integration(self):
        """Test database integration and user data persistence"""
        print("\n=== Testing Database Integration ===")
        
        # Test 1: User data persistence after registration
        if self.test_user_id:
            try:
                # Try to get the user profile using the public endpoint
                response = self.make_request("GET", f"/users/{self.test_user_id}")
                if response.status_code == 200:
                    data = response.json()
                    if "id" in data and "username" in data:
                        self.log_result("User data persistence", True, 
                                      f"User data persisted correctly: {data.get('username')}")
                    else:
                        self.log_result("User data persistence", False, f"Incomplete user data: {data}")
                else:
                    self.log_result("User data persistence", False, 
                                  f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("User data persistence", False, f"Error: {str(e)}")
        else:
            self.log_result("User data persistence", False, "No test user ID available")
        
        # Test 2: User lookup by email (indirect test through login)
        try:
            # This indirectly tests database user lookup
            login_data = {
                "email": "codemaster@example.com",
                "password": "password123"
            }
            response = self.make_request("POST", "/users/login", json=login_data)
            if response.status_code == 200:
                self.log_result("User lookup by email", True, "Successfully found user by email")
            else:
                self.log_result("User lookup by email", False, 
                              f"Failed to find user: {response.status_code}")
        except Exception as e:
            self.log_result("User lookup by email", False, f"Error: {str(e)}")
        
        # Test 3: User data structure validation
        if self.auth_token:
            try:
                response = self.make_request("GET", "/users/me")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check required fields
                    required_fields = ["id", "username", "email", "role", "status", "created_at"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        self.log_result("User data structure validation", True, "All required fields present")
                    else:
                        self.log_result("User data structure validation", False, 
                                      f"Missing fields: {missing_fields}")
                    
                    # Check data types
                    if isinstance(data.get("stats"), dict):
                        self.log_result("User stats structure", True, "User stats object present")
                    else:
                        self.log_result("User stats structure", False, "User stats missing or invalid")
                else:
                    self.log_result("User data structure validation", False, 
                                  f"Failed to get user data: {response.status_code}")
            except Exception as e:
                self.log_result("User data structure validation", False, f"Error: {str(e)}")
    
    def run_authentication_tests(self):
        """Run all authentication-specific tests"""
        print("🔐 Starting SAYPEX Authentication System Tests")
        print(f"Testing against: {self.base_url}")
        
        # Run authentication tests in order
        self.test_user_registration_comprehensive()
        self.test_user_login_comprehensive()
        self.test_protected_routes_comprehensive()
        self.test_database_integration()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("="*60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests * 100)
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 FAILED TESTS:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = SAYPEXAuthTester()
    success = tester.run_authentication_tests()
    sys.exit(0 if success else 1)