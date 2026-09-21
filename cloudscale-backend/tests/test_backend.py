import unittest
import os
import sys

# Ensure cloudscale-backend is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from starlette.testclient import TestClient
import main


class TestCloudScaleBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)

    def test_01_root_endpoint(self):
        """GET / should return 200 and API service descriptor"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "cloudscale-api")
        self.assertIn("docs", data)

    def test_02_favicon(self):
        """GET /favicon.ico should return 204 No Content"""
        response = self.client.get("/favicon.ico")
        self.assertEqual(response.status_code, 204)

    def test_03_health_endpoints(self):
        """GET /api/health and /health should return 200 OK with healthy status"""
        for path in ["/api/health", "/api/health/", "/health", "/health/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data.get("status"), "healthy")
                self.assertEqual(data.get("service"), "cloudscale-api")

    def test_04_metrics_endpoint(self):
        """GET /api/metrics should return telemetry metrics and history"""
        response = self.client.get("/api/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        required_fields = ["cpu", "memory", "requests", "latency", "instances", "autoscaling", "load_test", "history"]
        for field in required_fields:
            self.assertIn(field, data, f"Missing metric field: {field}")
        self.assertIsInstance(data["history"], list)
        self.assertGreater(len(data["history"]), 0)

    def test_05_resources_endpoint(self):
        """GET /api/resources should return list of virtual compute nodes"""
        response = self.client.get("/api/resources")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        node = data[0]
        self.assertIn("id", node)
        self.assertIn("status", node)
        self.assertIn("cpu", node)
        self.assertIn("memory", node)
        self.assertIn("region", node)
        self.assertIn("type", node)

    def test_06_autoscaling_policy(self):
        """GET and POST /api/autoscaling should retrieve and update policy"""
        # GET initial policy
        res_get = self.client.get("/api/autoscaling")
        self.assertEqual(res_get.status_code, 200)
        policy = res_get.json()
        self.assertIn("enabled", policy)
        self.assertIn("min_instances", policy)
        self.assertIn("max_instances", policy)

        # POST updated policy
        update_payload = {
            "enabled": True,
            "min_instances": 2,
            "max_instances": 8,
            "scale_up_threshold": 80.0,
            "scale_down_threshold": 25.0
        }
        res_post = self.client.post("/api/autoscaling", json=update_payload)
        self.assertEqual(res_post.status_code, 200)
        result = res_post.json()
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("max_instances"), 8)
        self.assertEqual(result.get("min_instances"), 2)

    def test_07_load_test_toggle(self):
        """POST /api/load-test should activate and deactivate synthetic load"""
        # Enable load test
        res_on = self.client.post("/api/load-test", json={"enabled": True})
        self.assertEqual(res_on.status_code, 200)
        self.assertTrue(res_on.json().get("load_test"))

        # Disable load test
        res_off = self.client.post("/api/load-test", json={"enabled": False})
        self.assertEqual(res_off.status_code, 200)
        self.assertFalse(res_off.json().get("load_test"))

    def test_08_activity_and_insights(self):
        """GET /api/activity and /api/insights should return audit logs and recommendations"""
        res_act = self.client.get("/api/activity")
        self.assertEqual(res_act.status_code, 200)
        self.assertIsInstance(res_act.json(), list)

        res_ins = self.client.get("/api/insights")
        self.assertEqual(res_ins.status_code, 200)
        data = res_ins.json()
        self.assertIn("severity", data)
        self.assertIn("title", data)
        self.assertIn("message", data)

    def test_09_docs_endpoint(self):
        """GET /docs should serve Swagger UI HTML"""
        res = self.client.get("/docs")
        self.assertEqual(res.status_code, 200)
        self.assertIn("swagger-ui", res.text.lower())

    def test_10_cors_headers(self):
        """CORS headers should allow local dev origins and all Vercel origins"""
        headers_local = {"Origin": "http://localhost:3000"}
        res_local = self.client.get("/api/health", headers=headers_local)
        self.assertEqual(res_local.status_code, 200)
        self.assertEqual(res_local.headers.get("access-control-allow-origin"), "http://localhost:3000")

        headers_vercel = {"Origin": "https://cloud-scale-ten.vercel.app"}
        res_vercel = self.client.get("/api/health", headers=headers_vercel)
        self.assertEqual(res_vercel.status_code, 200)
        self.assertEqual(res_vercel.headers.get("access-control-allow-origin"), "https://cloud-scale-ten.vercel.app")


if __name__ == "__main__":
    unittest.main()
