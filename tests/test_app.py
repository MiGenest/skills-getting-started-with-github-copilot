"""
Tests for the Mergington High School Activities API

Tests cover all API endpoints:
- GET / (root redirect)
- GET /activities (get all activities)
- POST /activities/{activity_name}/signup (sign up for activity)
- DELETE /activities/{activity_name}/unregister (unregister from activity)
"""

from fastapi.testclient import TestClient
from src.app import app

# Create a test client for the FastAPI app
client = TestClient(app)


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirect(self):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        
        # Verify that activities exist
        assert len(activities) > 0
        
        # Verify structure of an activity
        assert "Chess Club" in activities
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Use a unique test email to avoid conflicts
        test_email = "testuser_signup@mergington.edu"
        activity = "Debate Team"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert activity in result["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Fake Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_signup_duplicate_registration(self):
        """Test that duplicate signup returns 400 error"""
        # Use an existing participant in Chess Club
        test_email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # First sign up a user
        test_email = "testuser_unregister@mergington.edu"
        activity = "Science Club"
        
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == 200
        
        # Now unregister
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": test_email}
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Fake Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_not_registered(self):
        """Test unregister for student not registered returns 400"""
        test_email = "notregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": test_email}
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "not registered" in result["detail"]
