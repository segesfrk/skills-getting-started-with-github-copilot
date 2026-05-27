"""
FastAPI tests for Mergington High School Management System

Tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and client
- Act: Execute the endpoint
- Assert: Verify response and state changes
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to clean state before each test"""
    activities.clear()
    activities.update({
        "Math Club": {"name": "Math Club", "participants": []},
        "Science Fair": {"name": "Science Fair", "participants": []},
        "Drama Club": {"name": "Drama Club", "participants": []},
    })
    yield
    activities.clear()


# ============================================================================
# GET /activities Tests
# ============================================================================

def test_get_activities_returns_list(client):
    """Test GET /activities returns all activities"""
    # ARRANGE
    # (activities are pre-populated by reset_activities fixture)
    
    # ACT
    response = client.get("/activities")
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert "Math Club" in data
    assert "Science Fair" in data
    assert "Drama Club" in data
    assert len(data) == 3


def test_get_activities_returns_empty_participants(client):
    """Test GET /activities shows empty participants list initially"""
    # ARRANGE
    # (activities are pre-populated with empty participants)
    
    # ACT
    response = client.get("/activities")
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert data["Math Club"]["participants"] == []
    assert data["Science Fair"]["participants"] == []


# ============================================================================
# POST /activities/{activity_name}/signup Tests
# ============================================================================

def test_post_signup_new_email_success(client):
    """Test POST signup with valid activity and new email"""
    # ARRANGE
    activity_name = "Math Club"
    email = "student1@school.edu"
    
    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_post_signup_multiple_emails(client):
    """Test POST signup allows multiple different emails for same activity"""
    # ARRANGE
    activity_name = "Science Fair"
    email1 = "student1@school.edu"
    email2 = "student2@school.edu"
    
    # ACT - First signup
    response1 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email1}
    )
    
    # ACT - Second signup
    response2 = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email2}
    )
    
    # ASSERT
    assert response1.status_code == 200
    assert response2.status_code == 200
    assert len(activities[activity_name]["participants"]) == 2
    assert email1 in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]


def test_post_signup_duplicate_email_returns_400(client):
    """Test POST signup returns 400 for duplicate email on same activity"""
    # ARRANGE
    activity_name = "Drama Club"
    email = "student@school.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # ACT
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_post_signup_invalid_activity_returns_404(client):
    """Test POST signup returns 404 for non-existent activity"""
    # ARRANGE
    invalid_activity = "Nonexistent Club"
    email = "student@school.edu"
    
    # ACT
    response = client.post(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# ============================================================================
# DELETE /activities/{activity_name}/signup Tests
# ============================================================================

def test_delete_signup_removes_participant(client):
    """Test DELETE signup removes participant from activity"""
    # ARRANGE
    activity_name = "Math Club"
    email = "student@school.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # ACT
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_signup_nonexistent_activity_returns_404(client):
    """Test DELETE signup returns 404 for non-existent activity"""
    # ARRANGE
    invalid_activity = "Nonexistent Club"
    email = "student@school.edu"
    
    # ACT
    response = client.delete(
        f"/activities/{invalid_activity}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_signup_nonexistent_participant_returns_404(client):
    """Test DELETE signup returns 404 for non-existent participant"""
    # ARRANGE
    activity_name = "Science Fair"
    email = "nonexistent@school.edu"
    # (email not signed up for activity)
    
    # ACT
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )
    
    # ASSERT
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_delete_signup_only_removes_specific_email(client):
    """Test DELETE signup only removes the specified email"""
    # ARRANGE
    activity_name = "Drama Club"
    email1 = "student1@school.edu"
    email2 = "student2@school.edu"
    client.post(f"/activities/{activity_name}/signup", params={"email": email1})
    client.post(f"/activities/{activity_name}/signup", params={"email": email2})
    
    # ACT
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email1}
    )
    
    # ASSERT
    assert response.status_code == 200
    assert email1 not in activities[activity_name]["participants"]
    assert email2 in activities[activity_name]["participants"]
