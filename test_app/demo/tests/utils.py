from django.contrib.auth import get_user_model

from drf_redis_tokens.tokens_auth import MultiToken, TOKENS_CACHE


User = get_user_model()


def create_test_user(username='tester'):
    return User.objects.create_user(username=username)


class SetupTearDownForMultiTokenTests:

    def setUp(self):
        TOKENS_CACHE.clear()
        self.user = create_test_user()
        self.token, self.first_device = MultiToken.create_token(self.user)

    def tearDown(self):
        # cleanup Redis after tests
        TOKENS_CACHE.clear()
