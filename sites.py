#!usr/bin/env python3

import json
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

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
def get_results( data, desc='', loc=''):
    
    # find the Html tag with find() and convert into string
    results = []
    for job in data.find_all( 'div', class_ = 'Wrapper-sc-11673k2-0 fpBevf' ):

        # description of job
        job_description = '-'
        if hasattr( job.find( 'h2', class_ = 'sc-qapaw ERzaP' ), 'text' ):
            job_description = job.find( 'h2', class_ = 'sc-qapaw ERzaP' ).text.strip()

        # name of company
        company_name = '-'
        if hasattr( job.find( 'div', class_ = 'sc-pZBmh gelbdv' ), 'text' ):
            company_name = job.find( 'div', class_ = 'sc-pZBmh gelbdv' ).text.strip()

        # location of job
        location = '-'
        if hasattr( job.find( 'li', class_ = 'sc-pBzUF izAMeo sc-pRtAn iAUIOa' ), 'text' ):
            location = job.find( 'li', class_ = 'sc-pBzUF izAMeo sc-pRtAn iAUIOa' ).text.strip()
            if loc in location:
                location = loc

        # time of posting
        pub_data = '-'
        if hasattr( job.find( 'time', class_ = 'sc-oTNDV gmBWot' ), 'text' ):
            pub_data = job.find( 'time', class_ = 'sc-oTNDV gmBWot' ).text.strip()

        # website for job listing
        job_url = '-'
        if job.find( 'a', target = '_blank' )['href'] is not None:
            job_url = 'https://www.stepstone.de' + job.find( 'a', target = '_blank' )['href'].strip() 
        
        results.append( [job_description, company_name, location, pub_data, job_url] )

    return results

if __name__ == '__main__':

    # profile information
    with open( 'logins.json', 'r' ) as f:
        logins = json.load( f )

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
    age         = 'age_7'
    contract    = '222'
    worktime    = '80001'

    # create url
    url = logins['sites']['stepstone']['url'] + \
          '?' + 'ke=' + description + \
          '&' + 'ws=' + location + \
          '&' + 'radius=' + radius + \
          '&' + 'ag=' + age + \
          '&' + 'ct=' + contract + \
          '&' + 'wt=' + worktime

    # # obtain html code
    # data =  get_data( url )
    # print( 'Data was pulled...' )

    with open( 'test.html' , 'r' ) as f:
        data = f.read()

    # results array
    data = BeautifulSoup( data, 'html.parser' )
    results = get_results( data, description, location ) 
    print( 'Job data was extracted...' )

    # create html page with results
    with open( 'results.html', 'w' ) as f:
        f.write( tabulate( results, tablefmt='html' ) )
    print( ' HTML File saved' )

    # create csv file with results
    with open( 'results.csv', 'w' ) as f:
        for job in results:
            print( ','.join(job) )

            f.write( ','.join(job[:]) + '\n' )
    print( ' CSV File saved' )
