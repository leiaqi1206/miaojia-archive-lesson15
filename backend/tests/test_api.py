import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


class CatArchiveApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "cats.sqlite3"
        self.original_db_path = os.environ.get("MIAOJIA_DB_PATH")
        os.environ["MIAOJIA_DB_PATH"] = str(self.database_path)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        if self.original_db_path is None:
            os.environ.pop("MIAOJIA_DB_PATH", None)
        else:
            os.environ["MIAOJIA_DB_PATH"] = self.original_db_path
        self.temp_dir.cleanup()

    def test_health_and_message_endpoints(self) -> None:
        self.assertEqual(self.client.get("/api/health").json(), {"status": "ok"})
        self.assertEqual(
            self.client.get("/api/message").json(),
            {"message": "喵家档案后端连接成功"},
        )

    def test_create_list_and_get_cat(self) -> None:
        response = self.client.post(
            "/api/cats",
            json={"name": " 小橘 ", "breed": "中华田园猫", "birthday": "2024-03-12"},
        )
        self.assertEqual(response.status_code, 201)
        cat = response.json()
        self.assertEqual(cat["name"], "小橘")
        self.assertEqual(cat["breed"], "中华田园猫")
        self.assertTrue(cat["id"])
        self.assertTrue(cat["createdAt"])
        self.assertEqual(self.client.get("/api/cats").json(), [cat])
        self.assertEqual(self.client.get(f"/api/cats/{cat['id']}").json(), cat)

    def test_photo_and_notes_are_persisted(self) -> None:
        response = self.client.post(
            "/api/cats",
            json={"name": "奶盖", "photo": "data:image/jpeg;base64,ZmFrZQ==", "notes": "爱晒太阳"},
        )
        self.assertEqual(response.status_code, 201)
        cat_id = response.json()["id"]
        saved = self.client.get(f"/api/cats/{cat_id}").json()
        self.assertEqual(saved["photo"], "data:image/jpeg;base64,ZmFrZQ==")
        self.assertEqual(saved["notes"], "爱晒太阳")

    def test_update_preserves_creation_time(self) -> None:
        created = self.client.post("/api/cats", json={"name": "小橘"}).json()
        updated_response = self.client.put(
            f"/api/cats/{created['id']}", json={"name": "小橘", "personality": "亲人"}
        )
        self.assertEqual(updated_response.status_code, 200)
        updated = updated_response.json()
        self.assertEqual(updated["createdAt"], created["createdAt"])
        self.assertEqual(updated["personality"], "亲人")

    def test_records_survive_a_new_client(self) -> None:
        created = self.client.post("/api/cats", json={"name": "小橘"}).json()
        with TestClient(app) as reopened_client:
            saved = reopened_client.get(f"/api/cats/{created['id']}").json()
        self.assertEqual(saved["name"], "小橘")

    def test_blank_name_is_rejected(self) -> None:
        response = self.client.post("/api/cats", json={"name": "   "})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/api/cats").json(), [])

    def test_missing_cat_returns_404_and_delete_returns_204(self) -> None:
        self.assertEqual(self.client.get("/api/cats/missing").status_code, 404)
        created = self.client.post("/api/cats", json={"name": "小橘"}).json()
        self.assertEqual(self.client.delete(f"/api/cats/{created['id']}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/cats/{created['id']}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
