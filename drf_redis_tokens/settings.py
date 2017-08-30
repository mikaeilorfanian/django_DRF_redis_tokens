from django.conf import settings


DEFAULT_DRF_REDIS_SETTINGS = {
    'DRF_REDIS_MULTI_TOKENS':
        {
            'REDIS_DB_NAME': 'tokens',
        }
}


class DRFRedisMultipleTokensrSettings:
    def __init__(self, defaults):
        self.defaults = defaults
        self.overrides = getattr(settings, 'DRF_REDIS_MULTI_TOKENS', {})
        self.overrides.update({'AUTH_USER_MODEL': settings.AUTH_USER_MODEL})

    def __getattr__(self, item):
        try:
            return self.overrides[item]
        except KeyError:
            return self.defaults[item]


drf_redis_tokens_settings = DRFRedisMultipleTokensrSettings(DEFAULT_DRF_REDIS_SETTINGS)
