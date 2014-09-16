from django.core.mail import mail_admins
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_email(subject, content, email):
	subject = subject
	html_content = content
	msg = EmailMultiAlternatives(subject, html_content ,'', [email])
	msg.attach_alternative(html_content, "text/html")
	msg.content_subtype = "html"
	msg.send()