import scraperwiki
import lxml.html
import urllib2
import urllib
import re
from lxml import etree
from pyquery import PyQuery as pq

#scrape_url = "http://www.tripadvisor.com/RestaurantSearch?geo=187153"
scrape_url = "http://www.tripadvisor.com/Restaurants-g1221643-Villeneuve_les_Maguelone_Herault_Languedoc_Roussillon.html"

header = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.47 Safari/536.11',
           'Cookie': 'PHPSESSID=de45029e5e2fab4f6e5eef56515d6c1c; __utma=123692957.1658163614.1349740913.1349740913.1352756518.2; __utmb=204497347.1.10.1342787814; __utmc=204497347; __utmz=204497347.1341998344.1.1.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)' }

email_regex = re.compile(r'(\b[\w.]+@+[\w.]+.+[\w.]\b)')

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

def parse_list(root):
    """ Takes a listing page and indexes all the listings in it """
    for el in root(".listing a.property_title"):
        page_url = "http://www.tripadvisor.com" + el.get("href")
        page = get_url(page_url)
        
        email_raw = strip_tags(page(".sprite-grayEmail").next().attr("onclick"))
        email = email_regex.findall(email_raw)
        
        if email:
          email = email[0]
          print email

def scrape_activities_in_a_region(url):
    for el in url(".geo_image a"):
        sub_url = "http://www.tripadvisor.com" + el.get("href")
        
        # go to that sub location page
        sub_page = get_url(sub_url)
        
        # go to the activities page
        if sub_page(".filter#ATTR_CATEGORY_42"):
            sub_activities_url = "http://www.tripadvisor.com" + sub_page(".filter#ATTR_CATEGORY_42 a").attr("href")
            sub_activities_page = get_url(sub_activities_url)
        
            # go to the individual page (if it exists)
            for el in sub_activities_page(".element_wrap"):
                   sub_activities_adv_url = "http://www.tripadvisor.com" + sub_activities_page(".element_wrap a").attr("href")
                   sub_activities_adv_page = get_url(sub_activities_adv_url)
                   
                   print sub_activities_adv_url
               
                   # get the emails
                   #parse_list(sub_activities_adv_page)
        

scrape_url_page = get_url(scrape_url)
scrape_activities_in_a_region(scrape_url_page)


#parse_list(scrape_url_page)
