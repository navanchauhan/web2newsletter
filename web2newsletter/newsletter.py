import typer
import configparser
import csv

from .webpost import WebPostSource, get_content

app = typer.Typer()

config = configparser.ConfigParser()

@app.command()
def generate(file_path: str):
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
		get_content(link,config,feed)
		sources.append(feed)

	for source in sources:
		for post in source.get_sorted_posts():
			print(post.title)
			print(post.url)
			print(post.date)
			print(post.content)

if __name__ == "__main__":
	app()