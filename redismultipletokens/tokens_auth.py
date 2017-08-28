import binascii
import os

from django.conf import settings
from django.core.cache import caches
from passlib.hash import pbkdf2_sha256


TOKENS_CACHE = caches['tokens']
User = settings.AUTH_USER_MODEL


class MultiToken:

    TOKEN_HASH_SEPARATOR = ':hash:'

    def __init__(self, key, user):
        self.key = key
        self.user = user

    @classmethod
    def create(cls, user):
        created = False
        token = binascii.hexlify(os.urandom(20)).decode()
        hash = pbkdf2_sha256.hash(token)
        full_token = cls._make_full_token(token, hash)
        tokens = TOKENS_CACHE.get(user.pk)

        if not tokens:
            tokens = [hash]
            created = True
        else:
            tokens.append(hash)

        TOKENS_CACHE.set(str(user.pk), tokens)
        TOKENS_CACHE.set(hash, str(user.pk))

        return MultiToken(full_token, user), created

    @classmethod
    def get_user_from_token(cls, full_token):
        token, hash = cls._parse_full_token(full_token)
        if pbkdf2_sha256.verify(token, hash):
            return User.objects.get(pk=TOKENS_CACHE.get(hash))
        else:
            raise User.DoesNotExist

    @classmethod
    def expire_token(cls, full_token):
        token, hash = cls._parse_full_token(full_token.key)
        user_pk = TOKENS_CACHE.get(hash)
        tokens = TOKENS_CACHE.get(user_pk)
        tokens.remove(hash)
        TOKENS_CACHE.set(str(user_pk), tokens)
        TOKENS_CACHE.delete(hash)

    @classmethod
    def _make_full_token(cls, token, hash):
        return token + cls.TOKEN_HASH_SEPARATOR + hash

    @classmethod
    def _parse_full_token(cls, full_token):
        return full_token.split(cls.TOKEN_HASH_SEPARATOR)
