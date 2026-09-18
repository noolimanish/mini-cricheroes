from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class JWTAuthenticationAPITestCase(APITestCase):

    def setUp(self):
        self.username = "manish"
        self.password = "StrongPassword123"

        User.objects.create_user(
            username=self.username,
            email="manish@example.com",
            password=self.password
        )

    def test_login_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            "/auth/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            "access",
            response.data
        )

        self.assertIn(
            "refresh",
            response.data
        )

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            "/auth/login/",
            {
                "username": self.username,
                "password": "WrongPassword123",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    def test_refresh_token_returns_new_access_token(self):
        login_response = self.client.post(
            "/auth/login/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json"
        )

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/auth/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIn(
            "access",
            response.data
        )

    def test_login_with_unknown_user_fails(self):
        response = self.client.post(
            "/auth/login/",
            {
                "username": "unknown_user",
                "password": "StrongPassword123",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )