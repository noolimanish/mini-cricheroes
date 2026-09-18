from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class MatchAuthenticationAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="manish",
            email="manish@example.com",
            password="StrongPassword123"
        )

    def get_access_token(self):
        refresh = RefreshToken.for_user(
            self.user
        )

        return str(refresh.access_token)

    def test_create_match_without_token_is_rejected(self):
        response = self.client.post(
            "/matches/",
            {},
            format="json"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    def test_authenticated_request_is_allowed(self):
        access_token = self.get_access_token()

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.post(
            "/matches/",
            {
                "match_id": "M100",
                "team1": "IND",
                "team2": "AUS",
                "ground": "Hyderabad",
                "ball_type": "leather",
                "overs": 20,
            },
            format="json"
        )

        self.assertNotEqual(
            response.status_code,
            401
        )