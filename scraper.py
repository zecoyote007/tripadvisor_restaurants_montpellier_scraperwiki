#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime
import scraperwiki
import lxml.html
import urllib2
import urllib
import re
import HTMLParser
from lxml import etree
from pyquery import PyQuery as pq

#area = "187153"	#Montpellier
#area = "1221643"	#Villeneuve-Les-Maguelone
#area = "187169"	#Castres
#area = "665880"	#Carnon

#area = "187149"	#Languedoc-Roussillon (7613)

area = "2462549"	#Aude (1107)
#area = "2462552"	#Lozère (199/204)
#area = "1774988"	#Pyrénées-Orientales (1429)
#area = "2431928"	#Hérault (3028)
#area = "2431943"	#Gard (1509)

scrape_url = "http://www.tripadvisor.fr/RestaurantSearch?geo=" + area + "&o=a%s&sortOrder=popularity"

header = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.47 Safari/536.11',
           'Cookie': ''}

email_regex = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')
h = HTMLParser.HTMLParser()

def clean(input):
    input = make_unicode(input)
    input = input.strip(' \t\n\r')
    return input

def make_unicode(input):
    if type(input) != unicode:
	input = h.unescape(input)
	input = input.encode('utf-8')
    else:
	input = h.unescape(input)
    return input

def print_ascii(input):
    if input:
	print input.encode('ascii', 'ignore')

def get_url(url):
    req = urllib2.Request(url, None, header)
    response = urllib2.urlopen(req)
    root = pq(response.read().decode('utf-8'))
    return root

def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    if value:
        return re.sub(r'<[^>]*?>', '', value)
    return ""

def parse_page(root):
    page_records = 0
    """ Takes a listing page and indexes all the listings in it """
    for el in root(".listing a.property_title"):
        page_url = "http://www.tripadvisor.fr" + el.get("href")
        page = get_url(page_url)
	name = clean(strip_tags(page("#HEADING_GROUP h1").html()))
	rating = strip_tags(page(".sprite-rating_rr_fill").attr("alt"))
        ranking = strip_tags(page(".slim_ranking").html())
	hours = strip_tags(page(".hoursOverlay").html())
        #activity = strip_tags(page(".row-fluid  *[itemprop=title]").html())
        address = clean(strip_tags(page(".format_address").html()))
        #url = strip_tags(page(".row-fluid .row-fluid *[itemprop=url] a").attr("href"))
        telephone = strip_tags(page(".sprite-grayPhone").next().html())
	email_raw = strip_tags(page(".sprite-grayEmail").next().attr("onclick"))
        emails_parsed = email_regex.findall(email_raw)  
        if emails_parsed:
            email = clean(emails_parsed[0])
	else:
	    email = ""
	description = clean(strip_tags(page(".listing_details").html()))

	print ">>> PROCESSING RECORD"
        print page_url
	print_ascii(name)
	print_ascii(email)
	print_ascii(telephone)
	print_ascii(address)
	print_ascii(description)
	print "-" * 40
        
        data = {
            'name': name,
            'source_url': page_url,
            #'url': url,
	    'rating' : rating,
            'ranking': ranking,
	    'hours' : hours,
            'email': email,
            #'activity': activity,
            'address': address,
            'telephone': telephone,
            'description': description,
        }
        scraperwiki.sqlite.save(unique_keys=['source_url'], data=data, table_name="tripadvisor")
        #scraperwiki.sqlite.save_var('lastindex', index)

	page_records = page_records + 1
    return page_records

def parse_listing_pages(start_url):
    start_time = datetime.now()
    print start_time
    # not iterate over the pages
    currentPage = 1
    total_records = 0
    while True:
	if currentPage == 1:
            url = start_url
        print "PROCESSING PAGE %s" % url
	print "-" * 40
        page = get_url(url)

        # this will parse the first listing page
        nb_records = parse_page(page)
        total_records = total_records + nb_records

	print "FINISHED PAGE %s" % currentPage

	#Look for next page link
	next_page_url = page('.current').next().attr('href')
	if next_page_url:
		url = 'http://www.tripadvisor.fr' + next_page_url
		currentPage = currentPage + 1
	else:
		print "END OF LISTING REACHED AT PAGE %s" % currentPage
		break
    end_time = datetime.now()
    delta_time = end_time - start_time
    print "PROCESSING DURATION %s" % delta_time
    print "RECORDS PROCESSED %s" % total_records
    average_time_per_record = delta_time.seconds / total_records
    print "SECONDS PER RECORD = %s" % average_time_per_record

def parse_page_links(scrape_url):
	page = get_url(scrape_url)
	next_page_url = page('.current').next().attr('href')
        if next_page_url:
                print 'http://www.tripadvisor.fr' + next_page_url
	else:
                print "END OF LISTING REACHED"

def test_ip_address():
        page = get_url('http://checkip.dyndns.org')
	print page("body").html()

test_ip_address()

# Parse only the first page (30 records)
#scrape_url_page = get_url(scrape_url)
#parse_page(scrape_url_page)

# Parse next pages URLs
#parse_page_links(scrape_url)

# Parse all the records
parse_listing_pages(scrape_url)
