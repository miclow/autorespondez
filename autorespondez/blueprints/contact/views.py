from flask import (Blueprint, flash, redirect, request, url_for, render_template)

from autorespondez.blueprints.contact.forms import ContactForm

contact = Blueprint('contact', __name__, template_folder='templates')


@contact.route("/contact", methods=['GET', 'POST'])
def index():
	form = ContactForm()

	if form.validate_on_submit():
		# this prevents circular imports
		from autorespondez.blueprints.contact.tasks import deliver_contact_email

		deliver_contact_email.delay(request.form.get('email'), request.form.get('message'))
