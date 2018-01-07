import pytest

from autorespondez.app import create_app


@pytest.yield_fixture(scope='session')
def app():
	"""
	setup our fask test app, this only gets executed once
	:return: Flask app

	"""
	params = {
		'DEBUG': False,
		'TESTING': True,
		}

	_app = create_app(setting_override=params)

	# Establish an application context before running test

	ctx = _app.app_context()
	ctx.push()

	yield _app

	ctx.pop()


@pytest.yield_fixture(scope='function')
def client(app):
	"""
	setup an app client, this gets executed for each test function
	:return: Flask app client

	"""

	yield app.test_client()

