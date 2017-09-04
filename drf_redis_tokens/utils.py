
TOKEN_HASH_SEPARATOR = ':hash:'


def make_full_token(token, hash):
    return token + TOKEN_HASH_SEPARATOR + hash


def parse_full_token(full_token):
    token_hash = full_token.split(TOKEN_HASH_SEPARATOR)
    
    if len(token_hash) != 2:
        token_hash = ['wrong_token', 'wrong_hash']
    
    return token_hash
