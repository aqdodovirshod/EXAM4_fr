from rest_framework_simplejwt.tokens import RefreshToken, AccessToken


class CustomAccessToken(AccessToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['role'] = user.role
        return token


class CustomRefreshToken(RefreshToken):
    access_token_class = CustomAccessToken
    
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        token['role'] = user.role
        return token

