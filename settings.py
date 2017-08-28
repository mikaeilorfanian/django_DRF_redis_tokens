from django.conf import settings

DRF_REDIS_MULTI_TOKENS = {
    'REDS_DB_NAME': 'tokens',
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


drf_reds_tokens_settings = DRFRedisMultipleTokensrSettings(DRF_REDIS_MULTI_TOKENS)