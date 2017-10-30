import jwt

import urllib.request
import json
import jsonschema

from jose import jwk
from jose import jws

from functools import wraps
from flask import request, jsonify, _app_ctx_stack, current_app

from app import db
from app.models import WifiNetwork


from config import config

auth0_url = config.get("development").AUTH0_URL

def handle_error(error, status_code):
		resp = jsonify(error)
		resp.status_code = status_code
		return resp

"""
		This is what a decoded auth token looks like:
		('_app_ctx_stack.top.current_user: ', {
				u'iss': u'https://cjohnson6382.auth0.com/',
				u'iat': 1484031557,
				u'sub': u'auth0|58702f50ef793e559a07c56d',
				u'exp': 1484067557,
				u'aud': u'01TFwGUcUScthq1bPqjiF4Z4rKxd2zU7'
		})
"""

def requires_auth(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		if request.path.strip("/") in auth_whitelist: return f(*args, **kwargs)
		#	the auth0_url gets the public key for our auth0 domain
		#		https://cjohnson6382.auth0.com/.well-known/jwks.json
		resp = urllib.request.urlopen(auth0_url)
		data = json.loads(resp.read().decode('utf-8'))

		#	get the access_token that the client sent with their request
		auth = request.headers.get('Authorization', None)

		#	if there is no access_token, or if the token is improperly formatted, error out
		if not auth:
				return handle_error({
						'code': 'authorization_header_missing',
						'description': 'Authorization header is expected'
				}, 401)

		#	auth is in the format 'Bearer <Access_Token>'
		parts = auth.split()

		if parts[0].lower() != 'bearer':
				return handle_error({
						'code': 'invalid_header',
						'description':'Authorization header must start with Bearer'
				}, 401)
		elif len(parts) == 1:
				return handle_error({
						'code': 'invalid_header',
						'description': 'Token not found'
				}, 401)
		elif len(parts) > 2:
				return handle_error({
						'code': 'invalid_header',
						'description': 'Authorization header must be Bearer + \s + token'
				}, 401)

		#	get the access_token portion of auth
		token = parts[1]

		#	use the auth0 public key to decode the access_token that was encrypted with the user's key on the client side
		#		error out if decryption does not work for one reason or another
		try:
				payload = jws.verify(
						token,
						data,
						algorithms='[RS256]'
				)
		except jwt.ExpiredSignature:
				return handle_error({
						'code': 'token_expired',
						'description': 'token is expired'
				}, 401)
		except jwt.InvalidAudienceError:
				return handle_error({
						'code': 'invalid_audience',
						'description': 'incorrect audience, expected: ' + client_id
				}, 401)
		except jwt.DecodeError:
				return handle_error({
						'code': 'token_invalid_signature',
						'description': 'token signature is invalid'
				}, 401)
		except Exception as e:
				return handle_error({
						'code': 'invalid_header',
						'description': 'Unable to parse authentication token. %r' % e
				}, 400)

		user = json.loads(payload.decode())

		#	add the decrypted contents of the token to the server app's state so that it is available
		#		to any functions down the request-processing pipeline
		#		(see the format of the token just above this function definition)
		_app_ctx_stack.top.current_user = user
		return f(*args, **kwargs)

	return decorated
