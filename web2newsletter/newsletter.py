import typer
import configparser
import csv
import os
import jinja2
import time
import smtplib

from .webpost import WebPostSource, get_content
from .nlp import summarise
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = typer.Typer()

config = configparser.ConfigParser()

def generate_html(template, sources_with_posts, config):
	templateLoader = jinja2.FileSystemLoader(searchpath="./templates/")
	templateEnv = jinja2.Environment(loader=templateLoader)
	template = templateEnv.get_template(template)
	jinja_dict = {}
	for source in sources_with_posts:
		jinja_dict[source.title] = {}
		for idx, post in enumerate(source.get_sorted_posts()):
			jinja_dict[source.title][idx] = {
			"title": post.title,
			"url": post.url,
			"date": time.ctime(time.mktime(post.date)),
			"content": summarise(post.content)
			}

	return template.render(content=jinja_dict,config=config)
	
def send_email(config,html):
	s = smtplib.SMTP(config["SMTP_EMAIL"]["Server"],config["SMTP_EMAIL"]["Port"])
	s.starttls()
	s.login(config["SMTP_EMAIL"]["User"],config["SMTP_EMAIL"]["Password"])
	msg = MIMEMultipart('alternative')
	msg['To'] = ", ".join(config["NEWSLETTER"]["SendTo"].split())
	msg['From'] = config["SMTP_EMAIL"]["Email"]
	msg['Subject'] = config["NEWSLETTER"]["Title"]
	msg.attach(MIMEText(html,"html"))
	try:
		print('sending email xxx')
		s.sendmail(config["SMTP_EMAIL"]["Email"], ", ".join(config["NEWSLETTER"]["SendTo"].split()), msg.as_string())
	except Exception as e:
		print('Error sending email')
		print(e)
	finally:
		s.quit()

@app.command()
def generate(file_path: str, email: bool = False, return_html: bool = True, debug: bool = False):
	typer.echo(f"Reading config from: {file_path}")
	config.read(file_path)

	sources = []

	csv_input = []
	with open(config["FEEDS"]["WebsiteURLs"]) as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			csv_input.append(row)
			
			for feed_title,link in csv_input[1:]:
				feed = WebPostSource(feed_title)
				if debug:
					print(f"Getting pages for {feed_title}")
				get_content(link,config,feed,debug)
				sources.append(feed)
	"""
	for source in sources:
		for post in source.get_sorted_posts():
			print(post.title)
			print(post.url)
			print(post.date)
			print(summarise(post.content))
	"""
	if email:
		send_email(config,generate_html(config["NEWSLETTER"]["Theme"],sources,config))
	if return_html:
		print(generate_html(config["NEWSLETTER"]["Theme"],sources,config))
if __name__ == "__main__":
	app()