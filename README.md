# What Is drf-redis-tokens
`drf-redis-tokens` is a plugin for DRF and Django that allows you to create multiple tokens for each user(one per device) and store then in Redis.    
Here's why you may want to use this plugin:
- Your users have multiple devices and a log out from one device(or browser) should not log the user out on other devices(or browsers)
- Token retrieval, validation, and updates should be fast. This plugin uses Redis so you can't go faster than that!
- Security is important to you. This plugin encrypts users' tokens so even if an attacker gets access to all your token they would not be able to do anything with them.
*Note: device in this document means a physical one or a browser.*
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
            },
            'TIMEOUT': None,
        }
    }
```
**Notes**
- In the above definition, we're setting "tokens" as the name for the Redis db that will contain tokens. You can change this, see below.
- `TIMEOUT` is the ttl on your tokens. `None` here means that Redis will never expire your tokens. Warning: the default Django ttl is 5 minutes if you don't set `TIMEOUT` like above.
## Custom Settings
```python
DRF_REDIS_MULTI_TOKENS = {
    'REDIS_DB_NAME': 'custom_redis_db_name_for_tokens',
    'RESET_TOKEN_TTL_ON_USER_LOG_IN': True,
    'OVERWRITE_NONE_TTL': True,
}
```
Put the above config in your Django settings module to customize the behavior of `drf-redis-tokens`:    
- `RESET_TOKEN_TTL_ON_USER_LOG_IN` extends the life of tokens by `TIMEOUT`(set above) seconds.
- `OVERWRITE_NONE_TTL` will overwrite the previous ttl of `None`(which means Redis will never expire your token) set on a token. So, if your `TIMEOUT` is not `None` and you set `OVERWRITE_NONE_TTL` to `True` then your tokens will have a ttl.
- If you set `OVERWRITE_NONE_TTL` to `False`, the ttl of tokens with ttl `None` will not change. They will never expire.
## Set Up Token Authentication
There's complicated logic involved in token authentication, but `Django REST framework(DRF)` comes with a "pluggable" authentication system that supports token authentication.   
It also allows `drf-redis-tokens` to change where it stores tokens. We want our tokens to be stored in Redis, so we have to change the default authentication class:
```python
REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'drf_redis_tokens.tokens_auth.CachedTokenAuthentication',
        ),
        # your other DRF configurations goes below
        ...
    }
```
**Note**    
With this setting, we ask DFR to use `CachedTokenAuthentication` to check if users have the right token whenever they log in. 
## Create New Tokens
Usually, you want to create a new token whenever a user logs in from a new device:
```python
from drf_redis_tokens.tokens_auth import MultiToken

# create new token in your login logic
def login_handler(request):
    token, _ = MultiToken.create_token(request.user) # request object in DRF has a user attribute
						                             # _ variable is a boolean that denotes whether
						                             # this is the first token created for this user
    ...
```
**Notes**
- DRF checks to see if your user has a valid token. If not, then usually the login_handler is invoked. 
- `MultiToken.create_token` takes an instance of `settings.AUTH_USER_MODEL`.
- The `_` variable - when it is `True` - basically tells you whether the user is logged in on another device.
- The `token` object has two attributes: `key` and `user`. DRF expects custom tokens to have these attributes. `key` is the string user receives as their token and `user` is an instance of `settings.AUTH_USER_MODEL` model.
## Expiring Tokens
When a user logs out, you usually expire the token associated with that device. 
```python
from drf_redis_tokens.tokens_auth import MultiToken

def logout_handler(request):
    # DFR request object has an auth object which is of type MultiToken
    MultiToken.expire_token(request.auth)
    ...
```
Sometime, you want to expire all tokens from a user. For example, you may want to force log out on all devices:
```python
from drf_redis_tokens.tokens_auth import MultiToken

# user changes password and the new should be used to log in
def password_changed_handler(user):
    MultiToken.expire_all_tokens(request.user)
    ...
```
## Get User From Token
When you have access to user's token, you can get the `user` associated with that token:
```python
MultiToken.get_user_from_token(key)
```
**Notes**
- Then `key` here is `token.key` which is a `str` object, so `get_user_from_token` method expects a string.   
- `MultiToken.get_user_from_token` returns a `User` which is defined by `settings.AUTH_USER_MODEL`.
