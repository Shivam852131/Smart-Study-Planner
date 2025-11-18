#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class StudyPlannerAPITester:
    def __init__(self, base_url="https://studysmartly.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'subjects': [],
            'sessions': [],
            'tasks': [],
            'goals': []
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json() if response.text else {}
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        test_user = f"testuser_{datetime.now().strftime('%H%M%S')}"
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@example.com"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "username": test_user,
                "email": test_email,
                "password": "TestPass123!"
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            print(f"   Registered user: {test_user}")
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        # First register a user
        test_email = f"login_test_{datetime.now().strftime('%H%M%S')}@example.com"
        
        # Register
        self.run_test(
            "Pre-register for login test",
            "POST", 
            "auth/register",
            200,
            data={
                "username": "logintest",
                "email": test_email,
                "password": "TestPass123!"
            }
        )
        
        # Now test login
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login", 
            200,
            data={
                "email": test_email,
                "password": "TestPass123!"
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            return True
        return False

    def test_subjects_crud(self):
        """Test subjects CRUD operations"""
        # Create subject
        subject_data = {
            "name": "Mathematics",
            "difficulty": "hard",
            "priority": 5,
            "color": "#3B82F6"
        }
        
        success, response = self.run_test(
            "Create Subject",
            "POST",
            "subjects",
            200,
            data=subject_data
        )
        
        if not success:
            return False
            
        subject_id = response.get('id')
        self.created_resources['subjects'].append(subject_id)
        
        # Get subjects
        success, response = self.run_test(
            "Get Subjects",
            "GET", 
            "subjects",
            200
        )
        
        if not success or not isinstance(response, list):
            return False
            
        # Update subject
        updated_data = {
            "name": "Advanced Mathematics",
            "difficulty": "hard",
            "priority": 4,
            "color": "#3B82F6"
        }
        
        success, response = self.run_test(
            "Update Subject",
            "PUT",
            f"subjects/{subject_id}",
            200,
            data=updated_data
        )
        
        return success

    def test_study_sessions_crud(self):
        """Test study sessions CRUD operations"""
        # Create session
        session_data = {
            "subject_id": str(uuid.uuid4()),
            "subject_name": "Physics",
            "date": datetime.now().date().isoformat(),
            "start_time": "09:00",
            "end_time": "11:00", 
            "duration": 120,
            "notes": "Quantum mechanics review"
        }
        
        success, response = self.run_test(
            "Create Study Session",
            "POST",
            "study-sessions",
            200,
            data=session_data
        )
        
        if not success:
            return False
            
        session_id = response.get('id')
        self.created_resources['sessions'].append(session_id)
        
        # Get sessions
        success, response = self.run_test(
            "Get Study Sessions",
            "GET",
            "study-sessions", 
            200
        )
        
        if not success:
            return False
            
        # Complete session
        success, response = self.run_test(
            "Complete Study Session",
            "PATCH",
            f"study-sessions/{session_id}/complete",
            200
        )
        
        return success

    def test_tasks_crud(self):
        """Test tasks CRUD operations"""
        # Create task
        task_data = {
            "title": "Complete Physics Assignment",
            "subject_name": "Physics",
            "deadline": (datetime.now() + timedelta(days=7)).isoformat(),
            "priority": "high"
        }
        
        success, response = self.run_test(
            "Create Task",
            "POST",
            "tasks",
            200,
            data=task_data
        )
        
        if not success:
            return False
            
        task_id = response.get('id')
        self.created_resources['tasks'].append(task_id)
        
        # Get tasks
        success, response = self.run_test(
            "Get Tasks",
            "GET",
            "tasks",
            200
        )
        
        if not success:
            return False
            
        # Complete task
        success, response = self.run_test(
            "Complete Task",
            "PATCH",
            f"tasks/{task_id}/complete",
            200,
            params={"completed": "true"}
        )
        
        return success

    def test_goals_crud(self):
        """Test goals CRUD operations"""
        # Create goal
        goal_data = {
            "title": "Study 20 hours this week",
            "target_hours": 20,
            "deadline": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        success, response = self.run_test(
            "Create Goal",
            "POST",
            "goals",
            200,
            data=goal_data
        )
        
        if not success:
            return False
            
        goal_id = response.get('id')
        self.created_resources['goals'].append(goal_id)
        
        # Get goals
        success, response = self.run_test(
            "Get Goals",
            "GET",
            "goals",
            200
        )
        
        return success

    def test_ai_schedule_generation(self):
        """Test AI schedule generation"""
        schedule_data = {
            "subjects": [
                {"name": "Mathematics", "difficulty": "hard", "exam_date": "2025-02-15"},
                {"name": "Physics", "difficulty": "medium", "exam_date": "2025-02-20"}
            ],
            "available_hours_per_day": 4,
            "study_preferences": "I prefer studying difficult subjects in the morning"
        }
        
        success, response = self.run_test(
            "AI Schedule Generation",
            "POST",
            "generate-schedule",
            200,
            data=schedule_data
        )
        
        return success

    def test_analytics_endpoints(self):
        """Test analytics endpoints"""
        # Dashboard analytics
        success1, response1 = self.run_test(
            "Dashboard Analytics",
            "GET",
            "analytics/dashboard",
            200
        )
        
        # Progress analytics
        success2, response2 = self.run_test(
            "Progress Analytics", 
            "GET",
            "analytics/progress",
            200
        )
        
        return success1 and success2

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 Cleaning up test resources...")
        
        # Delete goals
        for goal_id in self.created_resources['goals']:
            self.run_test(f"Delete Goal {goal_id}", "DELETE", f"goals/{goal_id}", 200)
            
        # Delete tasks  
        for task_id in self.created_resources['tasks']:
            self.run_test(f"Delete Task {task_id}", "DELETE", f"tasks/{task_id}", 200)
            
        # Delete sessions
        for session_id in self.created_resources['sessions']:
            self.run_test(f"Delete Session {session_id}", "DELETE", f"study-sessions/{session_id}", 200)
            
        # Delete subjects
        for subject_id in self.created_resources['subjects']:
            self.run_test(f"Delete Subject {subject_id}", "DELETE", f"subjects/{subject_id}", 200)

def main():
    print("🚀 Starting Smart Study Planner API Tests")
    print("=" * 50)
    
    tester = StudyPlannerAPITester()
    
    # Test authentication
    if not tester.test_user_registration():
        print("❌ Registration failed, stopping tests")
        return 1
        
    if not tester.test_user_login():
        print("❌ Login failed, stopping tests")
        return 1
    
    # Test CRUD operations
    test_results = []
    test_results.append(("Subjects CRUD", tester.test_subjects_crud()))
    test_results.append(("Study Sessions CRUD", tester.test_study_sessions_crud()))
    test_results.append(("Tasks CRUD", tester.test_tasks_crud()))
    test_results.append(("Goals CRUD", tester.test_goals_crud()))
    test_results.append(("Analytics Endpoints", tester.test_analytics_endpoints()))
    test_results.append(("AI Schedule Generation", tester.test_ai_schedule_generation()))
    
    # Clean up
    tester.cleanup_resources()
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())