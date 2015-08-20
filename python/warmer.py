#!/usr/bin/python
import sys
import requests
import xml.etree.ElementTree as Et
from urllib2 import urlopen
import pycurl
from multiprocessing import Pool
from StringIO import StringIO
import argparse
from datetime import datetime
import time

startTime = datetime.now()


def curl_url(requesturl):
    """
    Main GET request via cURL
    :param requesturl:
    :return:
    """
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, requesturl)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    status = c.getinfo(pycurl.HTTP_CODE)
    effective_url = c.getinfo(pycurl.EFFECTIVE_URL)
    c.close()
    print status, effective_url


def load_batch_file(file):
    """
    Load Batch file as String
    :param file:
    :return:
    """
    f = open(file)
    lines = [i.rstrip() for i in f.readlines()]
    return lines


def get_site_map(requesturl):
    """
    Load sitemap.xml
    :param requesturl:
    :return:
    """
    current_url_list = []
    try:
        # Check string
        if requesturl.startswith('http://'):
            url = requesturl + "/sitemap.xml"
        elif requesturl.startswith('https://'):
            url = requesturl + "/sitemap.xml"
        else:
            url = "http://" + requesturl + "/sitemap.xml"
        print url
        # XML ElementTree
        tree = Et.parse(urlopen(url))
        root = tree.getroot()
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Loop through namespaced sitemap XML
        for url in root.findall('sitemap:url', ns):
            loc = url.find('sitemap:loc', ns)

            # Build fresh list
            current_url_list.append(loc.text)
    except:
        # log error
        print "error: " + url
    return current_url_list
#
# Main functionality
#
if __name__ == '__main__':
    # Add CLI helpers
    parser = argparse.ArgumentParser(description='HTTP CACHE WARMER :: Lets warm things up a bit...')
    parser.add_argument('--url', help='The URL to test')
    parser.add_argument('--file', help='The batch file of URLs to process')
    args = parser.parse_args()
    # Setup Multiprocessing
    p = Pool(64)
    # FILE - Check for Batch file
    current_url_list = []
    count = len(current_url_list)
    if args.file:
        print "file = " + args.file
        # Load and parse each line of the file as URLs
        data = load_batch_file(args.file)
        for url in data:
            current_url_list = get_site_map(url)
            # Map List
            p.map(curl_url, current_url_list)
            # Count URLs from sitemap
            print "URL COUNT : ", count
            time.sleep(2)
    # URL STRING - Default to provided URL (full)
    else:
        print "Requesting URL : " + args.url
        url = args.url + "/sitemap.xml"
        tree = Et.parse(urlopen(url))
        root = tree.getroot()
        ns = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        # Loop throught namespaced sitemap XML
        for url in root.findall('sitemap:url', ns):
            loc = url.find('sitemap:loc', ns)
            # Build fresh list
            current_url_list.append(loc.text)
        # Map List
        p.map(curl_url, current_url_list)
        # Count URLs from sitemap
        print "URL COUNT : ", count
        print datetime.now() - startTime
