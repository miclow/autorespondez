import datetime
from collections import OrderedDict
from hashlib import md5

import pytz
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer, \
	TimedJSONWebSignatureSerializer

from lib.util_sqlachemy import ResourceMixin, AwareDateTime
from autorespondez.extensions import db	

class User(UserMixin,ResourceMixin, db.Model):
	ROLE = OrderedDict([
		('member', 'Member'),
		('admin', 'Admin')
	])

	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)

	# Authentication.
	role = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False),
					 index=True, nullable=False, server_default='member')
	active = db.Column('is_active', db.Boolean(), nullable=False, 
						server_default='1')
	username = db.Column(db.String(24), unique=True, index=True)
	email = db.Column(db.String(255), unique=True, index=True, nullable=False,
					  server_default='')
	password = db.Column(db.String(128), nullable=False, server_default='')

	# Activity tracking
	sign_in_count = db.Column(db.Integer, nullable=False, default=0)
	current_sign_in_on = db.Column(AwareDateTime())
	current_sign_in_ip = db.Column(db.String(45))
	last_sign_in_on = db.Column(AwareDateTime())
	last_sign_in_ip = db.Column(db.String(45))

	def __init__(self, **kwargs):
		# Call Flask-SQLAlchemy's constructor.
		super(User, self).__init__(**kwargs)

		self.password = User.encrypt_password(kwargs.get('password', ''))

	@classmethod
	def find_by_identity(cls, identity):
		"""
		Find a user by email or username
		:param identity: Email or username
		:type identity: str
		:return: User instance
		"""
		return User.query.filter(
			(User.email == identity) | (User.username == identity)).first()	

	@classmethod
	def encrypt_password(cls, plaintext_password):
		"""
		Hash a plaintext string using PBKDF2. This is good enough according
		to the NIST (National Institute of Standards and Technology).
		In other words while bcrypt might be superior in practice, if you use
		PBKDF2 properly (which we are), then your passwords are safe.

		:param plaintext_password: Password in plain text
		:type plaintext_password: str
		:return: str
		"""

		if plaintext_password:
			return generate_password_hash(plaintext_password)

		return None


	@classmethod
	def deserialize_token(cls, token):
		"""
		Obtain a user from de-serializing a signed token
		:param token: signed token
		:type token: str
		:return: User instance or None
		"""	
		private_key = TimedJSONWebSignatureSerializer(
			current_app.config['SECRET_KEY'])
		try:
			decoded_payload = private_key.loads(token)

			return User.find_by_identity(decoded_payload.get('user_email'))
		except Exception:
			return None

	@classmethod
	def initialize_password_reset(cls, identity):
		"""
		Generate a token to reset the password for a specific user

		:param identity: User email address or username
		:type identity: str
		:return: User instance
		"""
		u = User.find_by_identity(identity)
		reset_token = u.serialize_token()

		# This prevents circular imports.
		from autorespondez.blueprints.user.tasks import (
			deliver_password_reset_email)
		deliver_password_reset_email.delay(u.id, reset_token)

		return u

	def is_active(self):
		"""
		return whether or not the user account is active, this satisfies
		Flask-Login by overwriting the default value.

		:return: bool
		"""	
		return self.active

	def get_auth_token(self):
		"""
		Return the user's auth token. Use their password as part of the token
		because if the user changes their password we wil want to invalidate 
		all of their logins across devices. It's completely fine to use
		md5 here as nothing leaks.

		This satisfies Flask-Login by providing a mean to create a token.

		:return: str
		"""	
		private_key = current_app.config['SECRET_KEY']

		serializer = URLSafeTimedSerializer(private_key)
		data = [str(self.id), md5(self.password.encode('utf-8')).hexdigest()]

		return serializer.dumps(data)

	def authenticated(self, with_password=True, password=''):
		"""
		Ensure a user is authenticated, and optionally check their password
		:param with_password: optionally check their password
		:type with_password: bool
		:type password: str
		:return: bool
		"""	
		if with_password:
			return check_password_hash(self.password, password)

		return True

	def serialize_token(self, expiration=3600):
		"""
		Sign and create a token that can be used for things such as resetting
		a password or other tasks that involve one off token.

		:param expiration: seconds until it expires,default to 1 hour
		:type expiration: int
		:return: JSON
		"""
		private_key = current_app.config['SECRET_KEY']

		serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
		return serializer.dumps({'user_email': self.email}).decode('utf-8')

	def update_activity_tracking(self, ip_address):
		"""
		Update various fields on the user that's related to meta data on their account,
		such as the sign in count and ip address, etc..

		:param ip_address: IP address
		:type ip_address: str 
		:return: SQLAlchemy commit results
		"""
		self.sign_in_count += 1

		self.last_sign_in_on = self.current_sign_in_on
		self.last_sign_in_ip = self.current_sign_in_ip

		self.current_sign_in_on = datetime.datetime.now(pytz.utc)
		self.current_sign_in_ip = ip_address

		return self.save()
					