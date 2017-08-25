# How to Install
First, download the package and install it using pip.   
Obviously, you'll need Django and Redis. Also, your Django app needs to be able to use Redis, so you'll need a library like `django-redis` or `django-redis-cache`.   
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
## Set Up Token Authentication
There's a bit of logic involved in token authentication, so many frameworks come with a token authentication mechanism. For example, `Django REST framework(DRF)` comes with a "pluggable" authentication mechanism that supports token authentication.    
You can use `django-redis-multiple-tokens` with any authentication framework that allows you to change where tokens are stored.   
Let's modify Django REST framework's Token Authentication to make it work with `django-redis-multiple-tokens`. First, you need to enable the DRF's `TokenAuthentication` by following the instructions here(http://www.django-rest-framework.org/api-guide/authentication/). But, don't do the migrations suggested by the guide there because those migrations will use your relational database for storing tokens whereas we want to use Redis.   
Then, you subclass the default `TokenAuthentication` class and change how it retrieves tokens:    
```python
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication


class CachedTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        try:
            user = MultiToken.get_user_from_token(key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, Token(key, user))
```
Finally, you tell DRF to use the above custom authentication class instead of the default one.   
```python
# put this in your Django settings file
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


