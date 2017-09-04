
TOKEN_HASH_SEPARATOR = ':hash:'


def make_full_token(token, hash):
    return token + TOKEN_HASH_SEPARATOR + hash


def parse_full_token(full_token):
    return full_token.split(TOKEN_HASH_SEPARATOR)
