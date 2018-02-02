"""Utility functions for portier login."""
from base64 import urlsafe_b64decode
from datetime import timedelta
import re

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

import jwt

import redis

from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient
import tornado.web

from dokomoforms.options import options


redis_kv = redis.StrictRedis.from_url(options.redis_url)


def b64dec(string):
    """Decode unpadded URL-safe Base64 strings.

    Base64 values in JWTs and JWKs have their padding '=' characters stripped
    during serialization. Before decoding, we must re-append padding characters
    so that the encoded value's final length is evenly divisible by 4.

    Taken from
    github.com/portier/demo-rp/blob/6aee99fe126eceda527cae1f6da3f02a68401b6e
    /server.py#L176-L184
    """
    padding = '=' * ((4 - len(string) % 4) % 4)
    return urlsafe_b64decode(string + padding)


async def get_verified_email(token):
    """Validate an Identity Token (JWT) and return its subject (email address).

    In Portier, the subject field contains the user's verified email address.

    This functions checks the authenticity of the JWT with the following steps:

    1. Verify that the JWT has a valid signature from a trusted broker.
    2. Validate that all claims are present and conform to expectations:

        * ``aud`` (audience) must match this website's origin.
        * ``iss`` (issuer) must match the broker's origin.
        * ``exp`` (expires) must be in the future.
        * ``iat`` (issued at) must be in the past.
        * ``sub`` (subject) must be an email address.
        * ``nonce`` (cryptographic nonce) must not have been seen previously.

    3. If present, verify that the ``nbf`` (not before) claim is in the past.

    Timestamps are allowed a few minutes of leeway to account for clock skew.

    This demo relies on the `PyJWT`_ library to check signatures and validate
    all claims except for ``sub`` and ``nonce``. Those are checked separately.

    .. _PyJWT: https://github.com/jpadilla/pyjwt

    Taken from
    github.com/portier/demo-rp/blob/6aee99fe126eceda527cae1f6da3f02a68401b6e
    /server.py#L240-L296
    """
    keys = await discover_keys('https://broker.portier.io')
    raw_header, _, _ = token.partition('.')
    header = json_decode(b64dec(raw_header))
    try:
        pub_key = keys[header['kid']]
    except KeyError:
        raise tornado.web.HTTPError(400)
    try:
        payload = jwt.decode(
            token, pub_key,
            algorithms=['RS256'],
            audience=options.minigrid_website_url,
            issuer='https://broker.portier.io',
            leeway=3 * 60,
        )
    except Exception as exc:
        raise tornado.web.HTTPError(400)
    if not re.match('.+@.+', payload['sub']):
        raise tornado.web.HTTPError(400)
    if not redis_kv.delete(payload['nonce']):
        raise tornado.web.HTTPError(400)
    return payload['sub']


def jwk_to_rsa(key):
    """Convert a deserialized JWK into an RSA Public Key instance.

    Taken from
    github.com/portier/demo-rp/blob/6aee99fe126eceda527cae1f6da3f02a68401b6e
    /server.py#L233-L237
    """
    e = int.from_bytes(b64dec(key['e']), 'big')
    n = int.from_bytes(b64dec(key['n']), 'big')
    return rsa.RSAPublicNumbers(e, n).public_key(default_backend())


async def discover_keys(broker):
    """Discover and return a Broker's public keys.

    Returns a dict mapping from Key ID strings to Public Key instances.

    Portier brokers implement the `OpenID Connect Discovery`_ specification.
    This function follows that specification to discover the broker's current
    cryptographic public keys:

    1. Fetch the Discovery Document from ``/.well-known/openid-configuration``.
    2. Parse it as JSON and read the ``jwks_uri`` property.
    3. Fetch the URL referenced by ``jwks_uri`` to retrieve a `JWK Set`_.
    4. Parse the JWK Set as JSON and extract keys from the ``keys`` property.

    Portier currently only supports keys with the ``RS256`` algorithm type.

    .. _OpenID Connect Discovery:
        https://openid.net/specs/openid-connect-discovery-1_0.html
    .. _JWK Set: https://tools.ietf.org/html/rfc7517#section-5

    Taken from
    github.com/portier/demo-rp/blob/6aee99fe126eceda527cae1f6da3f02a68401b6e
    /server.py#L187-L206
    """
    cache_key = 'jwks:' + broker
    raw_jwks = redis_kv.get(cache_key)
    if not raw_jwks:
        http_client = AsyncHTTPClient()
        url = broker + '/.well-known/openid-configuration'
        response = await http_client.fetch(url)
        discovery = json_decode(response.body)
        if 'jwks_uri' not in discovery:
            raise tornado.web.HTTPError(400)
        raw_jwks = (await http_client.fetch(discovery['jwks_uri'])).body
        redis_kv.setex(cache_key, timedelta(minutes=5), raw_jwks)
    jwks = json_decode(raw_jwks)
    if 'keys' not in jwks:
        raise tornado.web.HTTPError(400)
    return {
        key['kid']: jwk_to_rsa(key)
        for key in jwks['keys']
        if key['alg'] == 'RS256'
    }
