"""
Tests for the Mergington High School Activities API

Tests cover all API endpoints using the AAA (Arrange-Act-Assert) pattern:
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
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == expected_status
        assert response.headers["location"] == expected_location


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self):
        """Test that GET /activities returns all activities"""
        # Arrange
        expected_status = 200
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == expected_status
        assert isinstance(activities, dict)
        assert len(activities) > 0
        assert expected_activity in activities
        
        # Verify structure of an activity
        activity = activities[expected_activity]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        test_email = "testuser_signup@mergington.edu"
        activity = "Debate Team"
        expected_status = 200

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        result = response.json()

        # Assert
        assert response.status_code == expected_status
        assert "message" in result
        assert test_email in result["message"]
        assert activity in result["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity returns 404"""
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "student@mergington.edu"
        expected_status = 404
        expected_detail = "Activity not found"

        # Act
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": test_email}
        )
        result = response.json()

        # Assert
        assert response.status_code == expected_status
        assert expected_detail in result["detail"]

    def test_signup_duplicate_registration(self):
        """Test that duplicate signup returns 400 error"""
        # Arrange
        test_email = "michael@mergington.edu"  # Already registered in Chess Club
        activity = "Chess Club"
        expected_status = 400
        expected_detail = "already signed up"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        result = response.json()

        # Assert
        assert response.status_code == expected_status
        assert expected_detail in result["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # Arrange
        test_email = "testuser_unregister@mergington.edu"
        activity = "Science Club"
        expected_signup_status = 200
        expected_unregister_status = 200

        # Act - First sign up a user
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        
        # Act - Now unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": test_email}
        )
        result = unregister_response.json()

        # Assert
        assert signup_response.status_code == expected_signup_status
        assert unregister_response.status_code == expected_unregister_status
        assert "message" in result
        assert test_email in result["message"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity returns 404"""
        # Arrange
        fake_activity = "Fake Activity"
        test_email = "student@mergington.edu"
        expected_status = 404
        expected_detail = "Activity not found"

        # Act
        response = client.delete(
            f"/activities/{fake_activity}/unregister",
            params={"email": test_email}
        )
        result = response.json()

        # Assert
        assert response.status_code == expected_status
        assert expected_detail in result["detail"]

    def test_unregister_not_registered(self):
        """Test unregister for student not registered returns 400"""
        # Arrange
        test_email = "notregistered@mergington.edu"
        activity = "Chess Club"
        expected_status = 400
        expected_detail = "not registered"

        # Act
        response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": test_email}
        )
        result = response.json()

        # Assert
        assert response.status_code == expected_status
        assert expected_detail in result["detail"]
