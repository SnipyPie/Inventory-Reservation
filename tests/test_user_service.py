from argon2 import PasswordHasher

from tests.test_support import ServiceTestCase

from app.services import user_service, wallet_service


class UserServiceTests(ServiceTestCase):
    def test_register_normalizes_email_hashes_password_and_creates_customer_wallet(self):
        user = user_service.register_user("  Alice@Example.com ", "SecurePass123")

        self.assertEqual(user.email.lower(), "alice@example.com")
        self.assertNotEqual(user.password_hash, "SecurePass123")
        self.assertTrue(PasswordHasher().verify(user.password_hash, "SecurePass123"))
        self.assertEqual(user.role, "customer")
        self.assertEqual(str(wallet_service.get_wallet_balance(user.id)), "0.00")

    def test_register_rejects_invalid_email_short_password_and_duplicate(self):
        with self.assertRaises(ValueError):
            user_service.register_user("not-an-email", "SecurePass123")

        with self.assertRaisesRegex(ValueError, "at least 8"):
            user_service.register_user("person@example.com", "short")

        user_service.register_user("person@example.com", "SecurePass123")
        with self.assertRaisesRegex(ValueError, "already exists"):
            user_service.register_user("person@example.com", "AnotherPass123")

    def test_authenticate_success_wrong_password_and_unknown_email(self):
        created = user_service.register_user(
            "person@example.com",
            "SecurePass123",
        )

        authenticated, status = user_service.authenticate_user(
            "person@example.com",
            "SecurePass123",
        )
        self.assertEqual(status, "authenticated")
        self.assertEqual(authenticated.id, created.id)

        user, status = user_service.authenticate_user(
            "person@example.com",
            "WrongPassword123",
        )
        self.assertIsNone(user)
        self.assertEqual(status, "wrong_password")

        user, status = user_service.authenticate_user(
            "missing@example.com",
            "SecurePass123",
        )
        self.assertIsNone(user)
        self.assertEqual(status, "not_found")
