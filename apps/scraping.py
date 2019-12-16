#!/usr/bin/env python
# coding: utf-8

# import dependencies
from splinter import Browser
from bs4 import BeautifulSoup


def scrape_all():
	import datetime as dt
	# initiate headless driver for deployment
	browser = Browser("chrome", executable_path="chromedriver", headless=True)
	news_title, news_paragraph = mars_news(browser)

	# collect list of hemisphere images
	hemi_img_list = hemisphere_images(browser)

	# run all scraping functions and store results in dictionary
	data = {
	      "news_title": news_title,
	      "news_paragraph": news_paragraph,
	      "featured_image": featured_image(browser),
	      "hemisphere_image_1": hemi_img_list[0],
	      "hemisphere_image_2": hemi_img_list[1],
	      "hemisphere_image_3": hemi_img_list[2],
	      "hemisphere_image_4": hemi_img_list[3],
	      "facts": mars_facts(),
	      "last_modified": dt.datetime.now()
	}
	return data


# ## Article Scraping
def mars_news(browser):
	# visit the mars nasa news site
	url = 'https://mars.nasa.gov/news/'
	browser.visit(url)

	# optional delay for loading the page (wait a sec before searching)
	browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

	# set up HTML parser
	html = browser.html
	news_soup = BeautifulSoup(html, 'html.parser')
	try:
		slide_elem = news_soup.select_one('ul.item_list li.slide')

		# use the parent element to find the first `a` tag and save it as `news_title`
		news_title = slide_elem.find("div", class_='content_title').get_text()

		# Use the parent element to find the paragraph text
		news_p = slide_elem.find('div', class_="article_teaser_body").get_text()
	except AttributeError:
		return None, None

	return news_title, news_p


# ## Image Scraping
def featured_image(browser):
	# Visit URL
	url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
	browser.visit(url)

	# Find and click the full image button
	full_image_elem = browser.find_by_id('full_image')
	full_image_elem.click()

	# Find the more info button and click that
	browser.is_element_present_by_text('more info', wait_time=1)
	more_info_elem = browser.links.find_by_partial_text('more info')
	more_info_elem.click()

	# Parse the resulting html with soup
	html = browser.html
	img_soup = BeautifulSoup(html, 'html.parser')

	try:
		# Find the relative image url
		img_url_rel = img_soup.select_one('figure.lede a img').get("src") 
	except AttributeError:
		return None

	# Use the base URL to create an absolute URL
	img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

	return img_url


def hemisphere_images(browser):
	base_url = 'https://astrogeology.usgs.gov'
	# Visit URL
	url = f'{base_url}/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
	browser.visit(url)

	# set up HTML parser
	html = browser.html
	news_soup = BeautifulSoup(html, 'html.parser')

	# Find the links and titles of each hemisphere image
	img_list = []
	for item in (news_soup.find_all('div', class_='item')):
		img_dict = {}

		try:
			img_title = item.find_all('a', class_='itemLink')[1].find('h3').get_text()
			img_page = item.find('a')['href']

			# Vist image-spectic page to get link for full-size image
			browser.visit(f'{base_url}{img_page}')
			img_url = browser.find_by_css('li a').first['href']

			img_dict['img_url'] = img_url
			img_dict['title'] = img_title.rsplit(' ', 1)[0]
			img_list.append(img_dict)
		except AttributeError:
			img_list.append(None)

	return img_list


def mars_facts():
	import pandas as pd
	try:
		# Use pandas to extract table from webpage
		df = pd.read_html('http://space-facts.com/mars/')[0]
	except BaseException:
		return None
	# assign columns and set index
	df.columns=['description', 'value']
	df.set_index('description', inplace=True)

	# convert dataframe into HTML format
	return df.to_html(classes=['table-bordered', 'table-hover', 'table-dark'])


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())





