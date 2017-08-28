import binascii
import os

from django.conf import settings
from django.core.cache import caches


TOKENS_CACHE = caches['tokens']
User = settings.AUTH_USER_MODEL


class MultiToken:

    def __init__(self, key, user):
        self.key = key
        self.user = user

    @staticmethod
    def create(user):
        created = False
        token = binascii.hexlify(os.urandom(20)).decode()
        tokens = TOKENS_CACHE.get(user.pk)

        if not tokens:
            tokens = [token]
            created = True
        else:
            tokens.append(token)

        TOKENS_CACHE.set(str(user.pk), tokens)
        TOKENS_CACHE.set(token, str(user.pk))

        return MultiToken(token, user), created

    @staticmethod
    def get_user_from_token(token):
        return User.objects.get(pk=TOKENS_CACHE.get(token))

    @staticmethod
    def expire_token(token):
        user_pk = TOKENS_CACHE.get(token.key)
        tokens = TOKENS_CACHE.get(user_pk)
        tokens.remove(token.key)
        TOKENS_CACHE.set(str(user_pk), tokens)
        TOKENS_CACHE.delete(token.key)
