#!usr/bin/env python3

import json
import requests
from bs4 import BeautifulSoup
# from tabulate import tabulate
import pandas as pd

# get url from input
def get_data( url ):
    
    # create object to contain raw data
    raw_data = ''

    while True:

        # pull data from the internet
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',}
        response = requests.get( url, headers=headers )

        # extract content
        text = response.text

        soup = BeautifulSoup( text, 'html.parser' )
        raw_data += str( soup )

        # check if results are split in multiple pages
        next_page = soup.find("a", {"title": "Nächste"})

        if next_page:
            try:
                next_url = next_page['href']

                if next_url:
                    url = next_url
                else:
                    break
            except:
                break
        else:
            break

    # check_pages
    return raw_data

# filter job data using
# find_all function
def get_results( data, desc='', loc='', **kwargs ):
    
    # get parsing tags
    job_listing_tag     = kwargs['job_listing_tag']
    job_description_tag = kwargs['job_description_tag']
    company_name_tag    = kwargs['company_name_tag']
    location_tag        = kwargs['location_tag']
    pub_data_tag        = kwargs['pub_data_tag']
    job_url_tag         = kwargs['job_url_tag']

    # find the Html tag with find() and convert into string
    header = ['Listing name', 'Company name', 'Location', 'Publication Date', 'Link']
    results = []
    for job in data.find_all( 'div', class_ = job_listing_tag ):

        # description of job
        job_description = '-'
        if hasattr( job.find( 'h2', class_ = job_description_tag ), 'text' ):
            job_description = job.find( 'h2', class_ = job_description_tag ).text.strip().replace(',', '-')

        # name of company
        company_name = '-'
        if hasattr( job.find( 'div', class_ = company_name_tag ), 'text' ):
            company_name = job.find( 'div', class_ = company_name_tag ).text.strip().replace(',', '-')

        # location of job
        location = '-'
        if hasattr( job.find( 'li', class_ = location_tag ), 'text' ):
            location = job.find( 'li', class_ = location_tag ).text.strip().replace(',', '-')
            if loc.lower() not in location.lower():
                break

        # time of posting
        pub_data = '-'
        if hasattr( job.find( 'time', class_ = pub_data_tag ), 'text' ):
            pub_data = job.find( 'time', class_ = pub_data_tag ).text.strip().replace(',', '-')

        # website for job listing
        job_url = '-'
        if job.find( 'a', target = job_url_tag )['href'] is not None:
            job_url_nolink = 'https://www.stepstone.de' + job.find( 'a', target = job_url_tag )['href'].strip() 
            job_url = '<a href="' + job_url_nolink + '">' + job_url_nolink + '</a>'
        
        results.append( [job_description, company_name, location, pub_data, job_url] )

    df = pd.DataFrame( results, columns=header )

    return df

if __name__ == '__main__':

    # profile information
    with open( 'site_info.json', 'r' ) as f:
        site_info = json.load( f )

    # job information
    '''
        https://www.stepstone.de/5/ergebnisliste.html?ke=Ingenieurwesen%20Data%20Science
        &ws=Berlin
        &radius=30
        &ag=age_7
        &ct=222
        &wt=80001
    '''   

    description = '%20'.join(['ingenieur','data','science'])
    location    = 'Berlin'
    radius      = '30'
    age         = 'age_1'
    contract    = '222'
    worktime    = '80001'

    # create url
    url = site_info['sites']['stepstone']['url'] + \
          '?' + 'ke=' + description + \
          '&' + 'ws=' + location + \
          '&' + 'radius=' + radius + \
          '&' + 'ag=' + age + \
          '&' + 'ct=' + contract + \
          '&' + 'wt=' + worktime

    # obtain html code
    data =  get_data( url )
    print( 'Data was pulled...' )

    # with open( 'test.html' , 'r' ) as f:
    #     data = f.read()

    # results array
    data = BeautifulSoup( data, 'html.parser' )
    results = get_results( data, description, location, **site_info['sites']['stepstone'] ) 
    print( 'Job data was extracted...' )

    # create html page with results
    results_html = results.to_html( justify='left', escape=False )
    with open( 'results.html', 'w' ) as f:
        f.write( results_html )
    print( 'HTML File saved' )

    # # create csv file with results
    # results.to_csv( 'results.csv', sep=',', encoding='utf-8' )
    # print( 'CSV File saved' )
