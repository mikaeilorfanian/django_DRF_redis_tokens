from django.conf import settings


DEFAULT_DRF_REDIS_SETTINGS = {
    'DRF_REDIS_MULTI_TOKENS':
        {
            'REDIS_DB_NAME': 'tokens',
            'RESET_TOKEN_TTL_ON_USER_LOG_IN': True,
            'OVERWRITE_NONE_TTL': True,
            'TOKEN_TTL_IN_SECONDS': 1200000,
        }
}


class DRFRedisMultipleTokensrSettings:
    def __init__(self, defaults):
        self.defaults = defaults
        self.overrides = getattr(settings, 'DRF_REDIS_MULTI_TOKENS', {})

    def __getattr__(self, item):
        try:
            return self.overrides[item]
        except KeyError:
            return self.defaults[item]


drf_redis_tokens_settings = DRFRedisMultipleTokensrSettings(
    DEFAULT_DRF_REDIS_SETTINGS['DRF_REDIS_MULTI_TOKENS']
)
