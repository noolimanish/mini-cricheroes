from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def authenticate_client(client):
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPassword123"
    )

    refresh = RefreshToken.for_user(user)

    client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}"
    )

    return user