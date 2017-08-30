from django.core.cache import caches
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .crypto import generate_new_hashed_token, verify_token
from .settings import drf_redis_tokens_settings as drt_settings
from .utils import parse_full_token


TOKENS_CACHE = caches[drt_settings.DRF_REDIS_MULTI_TOKENS['REDIS_DB_NAME']]
User = drt_settings.AUTH_USER_MODEL


class MultiToken:

    def __init__(self, key, user):
        self.key = key
        self.user = user

    @classmethod
    def create_token(cls, user):
        created = False
        token, hash, full_token = generate_new_hashed_token()
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
        token, hash = parse_full_token(full_token)
        if verify_token(token, hash):
            user = User.objects.get(pk=TOKENS_CACHE.get(hash))
            
            if drt_settings.RESET_TOKEN_TTL_ON_USER_LOG_IN:
                cls.reset_tokens_ttl(user.pk)
            
            return user
        else:
            raise User.DoesNotExist

    @classmethod
    def expire_token(cls, full_token):
        token, hash = parse_full_token(full_token.key)
        user_pk = TOKENS_CACHE.get(hash)
        tokens = TOKENS_CACHE.get(user_pk)

        if tokens and request.auth.key in tokens:
            tokens.remove(hash)
            TOKENS_CACHE.set(str(user_pk), tokens)
        
        TOKENS_CACHE.delete(hash)

    @classmethod
    def expire_all_tokens(cls, user):
        hashed_tokens = TOKENS_CACHE.get(user.pk)
        for h in hashed_tokens:
            TOKENS_CACHE.delete(h)

        TOKENS_CACHE.delete(user.pk)

    @classmethod
    def reset_tokens_ttl(cls, user_pk):
        cls._reset_token_ttl(user.pk)

        hashed_tokens = TOKENS_CACHE.get(user.pk)
        for h in hashed_tokens:
            cls._reset_token_ttl(h)


    @classmethod
    def _reset_token_ttl(cls, key):
        if TOKENS_CACHE.tll(key) is None:
            if drt_settings.OVERWRITE_NONE_TTL:
                TOKENS_CACHE.expire(key, drt_settings.OVERWRITE_NONE_TTL)
        else:
            TOKENS_CACHE.expire(key, drt_settings.OVERWRITE_NONE_TTL)        


class CachedTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            user = MultiToken.get_user_from_token(key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, MultiToken(key, user))
