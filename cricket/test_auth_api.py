from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class UserRegistrationAPITestCase(APITestCase):

    def test_user_can_register(self):
        response = self.client.post(
            "/auth/register/",
            {
                "username": "manish",
                "email": "manish@example.com",
                "password": "StrongPassword123",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            response.data["message"],
            "User registered successfully."
        )

        self.assertEqual(
            response.data["username"],
            "manish"
        )

        self.assertTrue(
            User.objects.filter(
                username="manish"
            ).exists()
        )

    def test_password_is_hashed(self):
        password = "StrongPassword123"

        self.client.post(
            "/auth/register/",
            {
                "username": "hashuser",
                "email": "hash@example.com",
                "password": password,
            },
            format="json"
        )

        user = User.objects.get(
            username="hashuser"
        )

        self.assertNotEqual(
            user.password,
            password
        )

        self.assertTrue(
            user.check_password(password)
        )

    def test_duplicate_username_is_rejected(self):
        User.objects.create_user(
            username="manish",
            email="old@example.com",
            password="StrongPassword123"
        )

        response = self.client.post(
            "/auth/register/",
            {
                "username": "manish",
                "email": "new@example.com",
                "password": "StrongPassword123",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_short_password_is_rejected(self):
        response = self.client.post(
            "/auth/register/",
            {
                "username": "shortuser",
                "email": "short@example.com",
                "password": "123",
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            400
        )