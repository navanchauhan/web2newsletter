import logging
import requests
import feedparser
import time
import datetime
import re
import html2text


from usp.tree import sitemap_tree_for_homepage
from urllib.parse import urlparse
from tqdm import tqdm
#from readability import Document
from newspaper import Article

logging.getLogger("usp.fetch_parse").setLevel(logging.FATAL)
logging.getLogger("usp.helpers").setLevel(logging.FATAL)
logging.getLogger("usp.tree").setLevel(logging.FATAL)

feedparser.USER_AGENT = "curl/7.37.0"

headers = {
    'User-Agent': 'curl/7.37.0' # Just so we are not served the cached version by Sucuri/Cloudproxy
}

class WebPost:
	def __init__(self, title, url, date, content, content_type: str = "plain"):
		self.title = title
		self.url = url
		self.date = date
		self.content = content
		self.content_type = content_type
	def __str__(self):
		return f"Post: {self.title}\nPublished on {self.date} at {self.url}"

class WebPostSource:
	def __init__(self, title):
		self.title = title
		self.web_posts = []

	def add_post(self, post: WebPost):
		self.web_posts.append(post)

	def get_sorted_posts(self):
		return sorted(self.web_posts, key = lambda x: time.mktime(x.date), reverse=True)

def get_content(link,config,website: WebPostSource, debug: bool = False):
	res = requests.head(link,headers=headers)
	"""TODO
	Custom Exceptions
	"""
	content_type = res.headers["Content-Type"]
	if debug:
		print(res.headers)
	if ("application/rss+xml" in content_type) or ("application/xml" in content_type):
		feed = feedparser.parse(link)
		t1 = time.time()
		for entry in tqdm(feed["entries"]):
			t2 = time.mktime(entry.updated_parsed)
			if datetime.timedelta(seconds=t1-t2).days > int(config["FEEDS"]["LastNDays"]):
				continue
			else:
				post = WebPost(entry.title,entry.link,entry.updated_parsed,entry.summary)
				website.add_post(post)
	elif "text/html" in content_type:
		t1 = time.time()
		tree = sitemap_tree_for_homepage(link)
		posts_to_search = {}
		for page in tqdm(tree.all_pages()):
			if datetime.timedelta(seconds=t1-page.last_modified.timestamp()).days > int(config["FEEDS"]["LastNDays"]):
				continue
			else:
				if any(ignore in page.url for ignore in config["MISC_SITEMAP"]["IgnoreIfInURL"].split()):
					continue
				else:
					a = urlparse(page.url)
					if f"{a.scheme}://{a.netloc}/"==page.url:
						continue
					else:
						posts_to_search[page.url] = page.last_modified
		if posts_to_search != {}:
			h = html2text.HTML2Text()
			h.ignore_links = True
			for url in tqdm(posts_to_search):
				#res = requests.get(url)
				#doc = Document(res.text)
				#doc_text = html2text.html2text(doc.summary())
				article = Article(url)
				article.download()
				article.parse()
				article.nlp()
				post = WebPost(article.title,url,posts_to_search[url].timetuple(),article.summary)
				website.add_post(post)
	else:
		print("Not Supported")


