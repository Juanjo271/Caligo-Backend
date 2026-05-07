import pytest


class TestPOIsPublic:
    """Tests for public POI endpoints."""

    def test_get_pois_returns_list(self, client):
        """GET /api/pois should return a list of POIs."""
        response = client.get("/api/pois")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # We have 2 test POIs

    def test_get_pois_contains_required_fields(self, client):
        """Each POI should have required fields."""
        response = client.get("/api/pois")
        assert response.status_code == 200
        pois = response.json()
        for poi in pois:
            assert "id" in poi
            assert "nombre" in poi
            assert "categoria" in poi
            assert "lat" in poi
            assert "lon" in poi
            assert "radio_metros" in poi
            assert "es_legendario" in poi

    def test_get_poi_detail(self, client):
        """GET /api/pois/{id} should return POI details."""
        response = client.get("/api/pois/1")
        assert response.status_code == 200
        poi = response.json()
        assert poi["id"] == 1
        assert poi["nombre"] == "Iglesia La Ermita"

    def test_get_poi_not_found(self, client):
        """GET /api/pois/{id} with invalid ID should return 404."""
        response = client.get("/api/pois/9999")
        assert response.status_code == 404

    def test_root_endpoint(self, client):
        """GET / should return welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "mensaje" in data
        assert "version" in data

    def test_health_endpoint(self, client):
        """GET /health should return healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
