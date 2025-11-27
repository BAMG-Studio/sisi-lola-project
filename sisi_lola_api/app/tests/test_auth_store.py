import importlib
import os
import tempfile
import unittest
from pathlib import Path


def _fresh_store(tmp_path: Path):
    os.environ["AUTH_DB_PATH"] = str(tmp_path / "auth.db")
    os.environ.pop("RATE_LIMIT_PER_HOUR", None)
    import app.services.auth_store as auth_store

    importlib.reload(auth_store)
    auth_store.init_db()
    return auth_store


class AuthStoreTests(unittest.TestCase):
    def test_invite_redeem_and_validate(self):
        with tempfile.TemporaryDirectory() as td:
            store = _fresh_store(Path(td))
            code = store.create_invite("test@example.com", expires_at=9999999999, uses=1)
            api_key, creator_id = store.redeem_invite(code, "test@example.com", "Tester")
            self.assertTrue(api_key)
            self.assertTrue(creator_id)
            ctx = store.validate_api_key(api_key)
            self.assertEqual(ctx.email, "test@example.com")
            new_key = store.rotate_key(ctx.creator_id, "rotate")
            self.assertNotEqual(new_key, api_key)
            store.revoke_key(new_key)
            with self.assertRaises(Exception):
                store.validate_api_key(new_key)

    def test_usage_logging_and_limit(self):
        with tempfile.TemporaryDirectory() as td:
            store = _fresh_store(Path(td))
            os.environ["RATE_LIMIT_PER_HOUR"] = "2"
            importlib.reload(store)
            store.init_db()
            code = store.create_invite("log@example.com", expires_at=9999999999, uses=1)
            api_key, _ = store.redeem_invite(code, "log@example.com", None)
            ctx = store.validate_api_key(api_key)
            store.log_usage(ctx, "/videos/generate", "success", duration_ms=10)
            store.log_usage(ctx, "/videos/generate", "success", duration_ms=10)
            with self.assertRaises(Exception):
                store.enforce_rate_limit(ctx, "/videos/generate")


if __name__ == "__main__":
    unittest.main()
