from flask import url_for

class TestPage(object):
	def test_home_page(self,client):
		""" Home page should respond with a success 200 """
		response = client.get(url_for('page.home'))
		assert response.status_code == 200

	def test_terms_page(self,client):
		""" Home page should respond with a success 200 """
		response = client.get(url_for('page.terms'))
		assert response.status_code == 200

	def test_privacy_page(self,client):
		""" Home page should respond with a success 200 """
		response = client.get(url_for('page.privacy'))
		assert response.status_code == 200

	def test_title_html(self,client):
		""" If title tag exists, it should return true """
		response = client.get(url_for('page.home'))
		html = str(response.data)
		assert '<title>' in html
	