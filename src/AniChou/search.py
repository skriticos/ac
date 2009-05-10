import urllib
import urllib2
import urlparse
import xml.dom.minidom
import re
import sys
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

def url(needle, typ = 1):
	"""
	Type:
	1	Anime only
	2	Manga only
	3	Anime & Manga
	"""
	# Template. Example taken from the site.
	tmpl = 'http://myanimelist.net/includes/masearch.inc.php?s=mazinger&stype=1'
	# Make tuple mutable.
	tmpl = list(urlparse.urlparse(tmpl))
	# New parameters.
	query = dict(s = needle, stype = typ)
	tmpl[4] = urllib.urlencode(query)
	# The modified template.
	return urlparse.urlunparse(tmpl)

def request(url):
	head = {
	# How masearch is called on the site.
	'Referer': 'http://myanimelist.net/addtolist.php',
	# Override 'Python-urllib'.
	'User-Agent': 'animecollector',
	# This is not necessary for GET and should be done automatically
	# by urlopen() for POST.
	#'Content-Type': 'application/x-www-form-urlencoded'
	}
	# BTW has_header is case-sensitive.
	return urllib2.Request(url, headers = head)

def fetch(req):
	response = urllib2.urlopen(req)
	# minidom.parse takes a file-like directly, but we have to do some
	# cleaning first, as Expat doesn't like beautified XML :(
	html = response.read()
	# Does this do anything?
	response.close()
	# In 2.6 we could use translate().
	html = html.replace("\t", '')
	html = html.replace("\n", '')
	# No translate for 'mismatched tags'.
	html = html.replace('<br>', '<br/>')
	# Ampersand is only allowed for escaping, even in URLs.
	# Not that Expat would know that's what they are.
	html = re.sub('&(?!amp;)', '&amp;', html)
	# We get an HTML fragment with multiple elements (div) at the top level;
	# XML only allows one.
	html = '<body>%s</body>' % html
	doc = xml.dom.minidom.parseString(html)
	return doc

def scrape(doc):
	# This is rather fragile, but I'm too lazy to use HTMLParser,
	# and it wouldn't help it much.
	for div in doc.getElementsByTagName('div'):
		a = div.getAttribute('id')
		m = re.match(r'arow(\d+)', a)
		if not m:
			continue
		malid = int(m.group(1))
		strong = div.getElementsByTagName('strong')
		assert len(strong) == 1
		titles = [None] * 2
		# or nodeValue
		titles[0] = strong[0].firstChild.data
		for span in div.getElementsByTagName('span'):
			which = span.getAttribute('title')
			if which == 'English':
				titles[1] = span.nextSibling.data
			elif which == 'Synonyms':
				raw = span.nextSibling.data
				titles.extend(raw.split('; '))
		print "\n", malid,
		# join dies on None :(
		for t in titles:
			print t,

scrape(fetch(request(url(sys.argv[1], 3))))
