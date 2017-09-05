from django.contrib.auth import get_user_model
from django.test import TestCase

from .utils import create_test_user, SetupTearDownForMultiTokenTests
from drf_redis_tokens.tokens_auth import MultiToken, TOKENS_CACHE


User = get_user_model()


class TestCreateToken(SetupTearDownForMultiTokenTests, TestCase):

    def test_new_token_has_attributes_required_by_DRF(self):
        self.assertTrue(hasattr(self.token, 'key'))
        self.assertTrue(hasattr(self.token, 'user'))
        self.assertEqual(self.token.user.pk, self.user.pk)

    def test_first_token_for_user_is_flagged_correctly_as_first_device_getting_a_token(self):
        self.assertTrue(self.first_device)

    def test_second_token_for_user_is_flagged_correctly_as_not_the_first_device_getting_a_token(self):
        second_token, first_device = MultiToken.create_token(self.user)
        self.assertFalse(first_device)

    def test_token_is_saved_correctly_in_redis(self):
        self.assertIsNotNone(TOKENS_CACHE.get(self.user.pk))

        hashes = TOKENS_CACHE.get(self.user.pk)
        self.assertEqual(len(hashes), 1)
        self.assertIsNotNone(TOKENS_CACHE.get(hashes[0]))

    def test_only_token_hash_is_saved_in_redis(self):
        hash = TOKENS_CACHE.get(self.user.pk)[0]
        self.assertIsNotNone(TOKENS_CACHE.get(hash))
        self.assertIsNone(TOKENS_CACHE.get(self.token.key))

    def test_second_hash_is_saved_in_redis_alongside_the_first_one(self):
        first_hash = TOKENS_CACHE.get(self.user.pk)[0]
        second_token, first_device = MultiToken.create_token(self.user)
        second_hash = TOKENS_CACHE.get(self.user.pk)[1]

        self.assertEqual(len(TOKENS_CACHE.get(self.user.pk)), 2)
        self.assertIn(first_hash, TOKENS_CACHE.get(self.user.pk))
        self.assertIn(second_hash, TOKENS_CACHE.get(self.user.pk))
        self.assertIsNotNone(TOKENS_CACHE.get(first_hash))
        self.assertIsNotNone(TOKENS_CACHE.get(second_hash))


class TestGetUserFromTokenMethod(SetupTearDownForMultiTokenTests, TestCase):

    def test_correct_user_is_found_for_correct_token(self):
        user = MultiToken.get_user_from_token(self.token.key)
        self.assertEqual(user.pk, self.user.pk)

    def test_exception_is_raised_for_wrong_token(self):
        wrong_token = self.token.key[:-1]
        self.assertRaises(User.DoesNotExist, MultiToken.get_user_from_token, wrong_token)

        wrong_token = self.token.key[1:]
        self.assertRaises(User.DoesNotExist, MultiToken.get_user_from_token, wrong_token)
