import scraperwiki
import lxml.html
import urllib2
import urllib
import re
from lxml import etree
from pyquery import PyQuery as pq

#scrape_url = "http://www.tripadvisor.com/RestaurantSearch?geo=187153"
scrape_url = "http://www.tripadvisor.com/RestaurantSearch?geo=1221643"

header = { 'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.47 Safari/536.11',
           'Cookie': 'TASession=%1%V2ID.25F62354D4F10DF7FFE74EAFC0FF81E3*SQ.2*LS.UserReviewController*GR.34*TCPAR.13*TBR.55*EXEX.39*ABTR.73*PPRP.83*PHTB.6*FS.76*CPU.50*HS.popularity*ES.popularity*AS.popularity*DS.5*SAS.popularity*FPS.oldFirst*DF.0*LP.%2FRestaurantSearch%3Fgeo%3D1221643*MS.19*RMS.-1*TRA.true*LD.1221643*FBH.2; SessionTest=true; CommercePopunder=SuppressUnload; ServerPool=X; TATravelInfo=V2*A.2*MG.-1*HP.2*FL.3*RS.-1; CM=%1%HanaPersist%2C%2C-1%7Cpu_vr2%2C%2C-1%7Ct4b-pc%2C%2C-1%7CHanaSession%2C%2C-1%7CFtrSess%2C%2C-1%7CRCPers%2C%2C-1%7CHomeAPers%2C%2C-1%7C+r_lf_1%2C%2C-1%7CWShadeSeen%2C%2C-1%7CRCSess%2C%2C-1%7C+r_lf_2%2C%2C-1%7Cpu_vr1%2C%2C-1%7CFtrPers%2C%2C-1%7CHomeASess%2C%2C-1%7CBPPers%2C1%2C1431507941%7CBPSess%2C1%2C-1%7CPU_quick1%2C%2C-1%7CPU_quick2%2C%2C-1%7Cvr_npu2%2C%2C-1%7CLastPopunderId%2C94-610-34217%2C-1%7Cpssamex%2C%2C-1%7Cvr_npu1%2C%2C-1%7Cbrandsess%2C%2C-1%7CCCPers%2C%2C-1%7CCCSess%2C%2C-1%7CWAR_RESTAURANT_FOOTER_SESSION%2C%2C-1%7Cbrandpers%2C%2C-1%7Csesssticker%2C%2C-1%7C%24%2C%2C-1%7Ct4b-sc%2C%2C-1%7Cviator_2%2C%2C-1%7CWarPopunder_Session%2C%2C-1%7Csess_rev%2C%2C-1%7Csessamex%2C%2C-1%7Cviator_1%2C%2C-1%7CWarPopunder_Persist%2C%2C-1%7CSaveFtrPers%2C%2C-1%7Cr_ta_2%2C%2C-1%7Cr_ta_1%2C%2C-1%7CSaveFtrSess%2C%2C-1%7Cpers_rev%2C%2C-1%7CRBASess%2C%2C-1%7Cperssticker%2C%2C-1%7CMetaFtrSess%2C%2C-1%7CRBAPers%2C%2C-1%7CWAR_RESTAURANT_FOOTER_PERSISTANT%2C%2C-1%7CMetaFtrPers%2C%2C-1%7C; TASSK=enc%3ARNniFej67m%2BOS2WmzABITVIvwBRyE34H5yY%2FWEDeRgajeI4bPVxeHAdUPz3chjcM; TAUnique=%1%enc%3AIhZfEIVqUMIbljTEYWK8objYfixl0BnB06b1atePIxQ2jHwltRJPGQ%3D%3D; roybatty=AAABTSh5M36KsTYAzgyHlHu%2BCh%2BGxCeEiP6F8w%3D%3D%2C1'}

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
        print "Url: %s" % page_url
        page = get_url(page_url)

        name = strip_tags(page("#HEADING_GROUP h1").html())
        ranking = strip_tags(page(".slim_ranking").html())
        #activity = strip_tags(page(".row-fluid  *[itemprop=title]").html())
        address = strip_tags(page(".format_address").html())
        #url = strip_tags(page(".row-fluid .row-fluid *[itemprop=url] a").attr("href"))
        telephone = strip_tags(page(".sprite-grayPhone").next().html())
	email_raw = strip_tags(page(".sprite-grayEmail").next().attr("onclick"))
        emails_parsed = email_regex.findall(email_raw)  
        if emails_parsed:
            email = emails_parsed[0]
	else:
	    email = ""
	print email
        description = strip_tags(page(".listing_details").html())
	print description
        
        data = {
            'name': name,
            'source_url': page_url,
            #'url': url,
            'ranking': ranking,
            'email': email,
            #'activity': activity,
            'address': address,
            'telephone': telephone,
            'description': description,
        }
        scraperwiki.sqlite.save(unique_keys=['name'], data=data, table_name="tripadvisor")
        #scraperwiki.sqlite.save_var('lastindex', index)

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
                   parse_list(sub_activities_adv_page)
        

scrape_url_page = get_url(scrape_url)
scrape_activities_in_a_region(scrape_url_page)

parse_list(scrape_url_page)

