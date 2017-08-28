# How to Install
First, download the package and install it using pip.   
Obviously, you'll need Django, Django REST Framework, and Redis. Also, your Django app needs to be able to use Redis, so you'll need a library like `django-redis` or `django-redis-cache`.
Follow the instructions here(http://django-redis-cache.readthedocs.io/en/latest/intro_quick_start.html) to setup Django with Redis.   
# How to Use It
## Create a Redis DB For Tokens
Once you're done with the installation step, make a Redis db for your tokens by putting something like this in your Django settings file:   
```python
CACHES = {
        ...
        # other Redis db definitions above

        # tokens db definition
        'tokens': {
            'BACKEND': 'redis_cache.RedisCache',
            'LOCATION': 'localhost:6379',
            'OPTIONS': {
                'DB': 2,
            }
        }
    }
```
*Note:* in the above definition, we're setting "tokens" as the name for the Redis db that will contains tokens.
```python
DRF_REDIS_MULTI_TOKENS = {
    'REDIS_DB_NAME': 'custom_redis_db_name_for_tokens',
}
```
Using the above config, you can specify which Redis db should be used to store your tokens.
## Set Up Token Authentication
There's a bit of logic involved in token authentication, but `Django REST framework(DRF)` comes with a "pluggable" authentication mechanism that supports token authentication.
It also allows `drf-redis-tokens` to change where we it tokens. To do that, add the following to your django settings module:
```python
REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'account.authentication.CachedTokenAuthentication',
        ),
        # your other DRF configurations goes below
        ...
    }
```
*Note: `MultiToken.get_user_from_token` takes one argument. This argument must be unique to each token because it's used as a `key` in Redis. `MultiToken.get_user_from_token` returns a `User` which is defined by `settings.AUTH_USER_MODEL` if you're using a custom `User` model or Django's default `User` model.*    
## Create New Tokens


