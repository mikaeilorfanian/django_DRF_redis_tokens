from django.test import TestCase

from drf_redis_tokens.crypto import generate_new_hashed_token


class TestGenerateNewTokenClass(TestCase):

    def test_function_reutns_three_parts(self):
        res = generate_new_hashed_token()
        self.assertEqual(len(res), 3)
