import unittest
import json
import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from starlette.testclient import TestClient
import main
import api.index


class TestCloudScaleApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(main.app)
        cls.vercel_client = TestClient(api.index.app)

    def test_01_root_endpoint(self):
        """GET / should return 200 and serve HTML or status JSON"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_02_api_root(self):
        """GET /api should return healthy service descriptor"""
        response = self.client.get("/api")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("service"), "cloudscale-api")

    def test_03_health_endpoints(self):
        """GET /api/health and /health should return 200 OK"""
        for path in ["/api/health", "/api/health/", "/health", "/health/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual(data.get("status"), "healthy")

    def test_04_metrics_endpoint(self):
        """GET /api/metrics should return telemetry data with history"""
        response = self.client.get("/api/metrics")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for field in ["cpu", "memory", "requests", "latency", "instances", "autoscaling", "history"]:
            self.assertIn(field, data, f"Missing required telemetry field: {field}")
        self.assertIsInstance(data["history"], list)

    def test_05_resources_endpoint(self):
        """GET /api/resources should return array of active compute nodes"""
        response = self.client.get("/api/resources")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first_node = data[0]
        self.assertIn("id", first_node)
        self.assertIn("status", first_node)
        self.assertIn("cpu", first_node)

    def test_06_autoscaling_policy(self):
        """GET and POST /api/autoscaling should retrieve and update scaling configuration"""
        # GET policy
        get_res = self.client.get("/api/autoscaling")
        self.assertEqual(get_res.status_code, 200)
        policy = get_res.json()
        self.assertIn("enabled", policy)

        # POST update policy
        new_policy = {
            "enabled": True,
            "min_instances": 2,
            "max_instances": 6,
            "scale_up_threshold": 80.0,
            "scale_down_threshold": 25.0
        }
        post_res = self.client.post("/api/autoscaling", json=new_policy)
        self.assertEqual(post_res.status_code, 200)
        result = post_res.json()
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("max_instances"), 6)

    def test_07_load_test_toggle(self):
        """POST /api/load-test should activate and deactivate synthetic load"""
        res_start = self.client.post("/api/load-test", json={"enabled": True})
        self.assertEqual(res_start.status_code, 200)
        self.assertTrue(res_start.json().get("load_test"))

        res_stop = self.client.post("/api/load-test", json={"enabled": False})
        self.assertEqual(res_stop.status_code, 200)
        self.assertFalse(res_stop.json().get("load_test"))

    def test_08_activity_and_insights(self):
        """GET /api/activity and /api/insights should return audit logs and recommendations"""
        act_res = self.client.get("/api/activity")
        self.assertEqual(act_res.status_code, 200)
        self.assertIsInstance(act_res.json(), list)

        ins_res = self.client.get("/api/insights")
        self.assertEqual(ins_res.status_code, 200)
        self.assertIn("severity", ins_res.json())
        self.assertIn("title", ins_res.json())

    # =========================================================================
    # Vercel Specific Deployment & Routing Tests
    # =========================================================================

    def test_09_direct_api_index_file_check(self):
        """Direct checks to /api/index.py MUST return 200 OK (never 404)"""
        for path in ["/api/index.py", "/api/index.py/", "/index.py"]:
            with self.subTest(path=path):
                res = self.client.get(path)
                self.assertEqual(res.status_code, 200, f"{path} returned {res.status_code} instead of 200")
                data = res.json()
                self.assertEqual(data.get("status"), "healthy")

    def test_10_api_index_subpaths(self):
        """Direct checks to /api/index.py subpaths must route cleanly"""
        endpoints = [
            ("/api/index.py/health", "status"),
            ("/api/index.py/metrics", "cpu"),
            ("/api/index.py/resources", None),
            ("/api/index.py/activity", None),
            ("/api/index.py/insights", "title")
        ]
        for path, expected_key in endpoints:
            with self.subTest(path=path):
                res = self.client.get(path)
                self.assertEqual(res.status_code, 200, f"{path} failed with {res.status_code}")
                if expected_key:
                    self.assertIn(expected_key, res.json())

    def test_11_vercel_rewrite_simulation_x_matched_path(self):
        """Simulate Vercel rewriting /api/metrics to /api/index.py via x-matched-path"""
        # When Vercel receives /api/metrics, it rewrites to /api/index.py and provides x-matched-path
        headers = {"x-matched-path": "/api/metrics"}
        res = self.client.get("/api/index.py", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("cpu", data, "Failed to resolve x-matched-path: /api/metrics")
        self.assertIn("requests", data)

    def test_12_vercel_rewrite_simulation_x_forwarded_uri(self):
        """Simulate Vercel forwarding original URI via x-forwarded-uri"""
        headers = {"x-forwarded-uri": "/api/resources"}
        res = self.client.get("/api/index.py", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_13_api_index_module_export(self):
        """Verify api/index.py exports both app and handler conforming to Vercel standards"""
        self.assertTrue(hasattr(api.index, "app"))
        self.assertTrue(hasattr(api.index, "handler"))
        res = self.vercel_client.get("/api/health")
        self.assertEqual(res.status_code, 200)

    def test_14_vercel_json_validity(self):
        """Verify vercel.json is valid and contains essential function & rewrite declarations"""
        vercel_json_path = os.path.join(PROJECT_ROOT, "vercel.json")
        self.assertTrue(os.path.exists(vercel_json_path))
        with open(vercel_json_path, "r") as f:
            config = json.load(f)
        self.assertIn("rewrites", config)
        has_api_rewrite = any(
            r.get("source") in ["/api/(.*)", "/api/:match*"] and "api/index.py" in r.get("destination", "")
            for r in config["rewrites"]
        )
        self.assertTrue(has_api_rewrite, "vercel.json missing rewrite from /api to api/index.py")


if __name__ == "__main__":
    unittest.main()
