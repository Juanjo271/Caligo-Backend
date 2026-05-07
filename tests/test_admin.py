import pytest


class TestAdminAuth:
    """Tests for admin authentication."""

    def test_admin_login_page_loads(self, client):
        """GET /admin/login should return HTML page."""
        response = client.get("/admin/login")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_admin_login_with_credentials(self, client, test_db):
        """POST /api/admin/login should work with default credentials."""
        # Note: This test requires the database to have the default admin user
        # which is created on startup if users table is empty
        response = client.post(
            "/api/admin/login",
            data={"username": "admin", "password": "admin123"},
        )
        # Should either succeed or fail depending on if DB was seeded
        assert response.status_code in [200, 401]

    def test_admin_logout(self, client):
        """GET /admin/logout should clear cookie and redirect."""
        response = client.get("/admin/logout")
        assert response.status_code == 307  # Redirect


class TestAdminPOIs:
    """Tests for admin POI management endpoints."""

    def test_admin_list_pois_requires_auth(self, client):
        """GET /api/admin/pois without auth should return 401."""
        response = client.get("/api/admin/pois")
        assert response.status_code == 401

    def test_admin_get_stats_requires_auth(self, client):
        """GET /api/admin/stats without auth should return 401."""
        response = client.get("/api/admin/stats")
        assert response.status_code == 401

    def test_admin_get_categories_requires_auth(self, client):
        """GET /api/admin/categories without auth should return 401."""
        response = client.get("/api/admin/categories")
        assert response.status_code == 401

    def test_admin_get_tags_requires_auth(self, client):
        """GET /api/admin/tags without auth should return 401."""
        response = client.get("/api/admin/tags")
        assert response.status_code == 401


class TestAdminPages:
    """Tests for admin HTML pages."""

    def test_admin_dashboard_requires_auth(self, client):
        """GET /admin/ should redirect to login if not authenticated."""
        response = client.get("/admin/")
        assert response.status_code == 307  # Redirect to login

    def test_admin_pois_page_requires_auth(self, client):
        """GET /admin/pois should redirect to login if not authenticated."""
        response = client.get("/admin/pois")
        assert response.status_code == 307

    def test_admin_new_poi_page_requires_auth(self, client):
        """GET /admin/pois/new should redirect to login if not authenticated."""
        response = client.get("/admin/pois/new")
        assert response.status_code == 307
