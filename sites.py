#!usr/bin/env python3

import json
import requests
from bs4 import BeautifulSoup
import pandas as pd


# get url from input
def get_data(url, params):
    # create object to contain raw data
    raw_data = ''

    while True:

        # pull data from the internet
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', }
        response = requests.get(url, params=params, headers=headers)

        # extract content
        text = response.text

        soup = BeautifulSoup(text, 'html.parser')
        raw_data += str(soup)

        # check if results are split in multiple pages
        next_page = soup.find("a", {"title": "Nächste"})

        if next_page:
            try:
                next_url = next_page['href']

                if next_url:
                    url = next_url
                else:
                    break
            except Exception as e:
                break
        else:
            break

    # check_pages
    return raw_data


def convert_time(time_job):
    time_pub = time_job.split()[1:]
    if ('Tag' in time_pub[1]):
        return time_pub[0] + ' days'
    else:
        return '0 days'


# filter job data using
# find_all function
def get_results(data, desc='', loc='', **kwargs):
    # get parsing tags
    job_listing_tag     = kwargs['job_listing_tag']
    job_description_tag = kwargs['job_description_tag']
    company_name_tag    = kwargs['company_name_tag']
    location_tag        = kwargs['location_tag']
    pub_data_tag        = kwargs['pub_data_tag']

    # find the Html tag with find() and convert into string
    header = ['Listing name', 'Company name', 'Location', 'Age', 'Link']
    results = []
    for job in data.find_all('div', {'class': job_listing_tag}):

        # description of job
        job_description = '-'
        if hasattr(job.find('a', {'data-at': job_description_tag}), 'h2'):
            job_description = job.find('a', {'data-at': job_description_tag}).h2.text.strip().replace(',', '-')

        # name of company
        company_name = '-'
        if hasattr(job.find('div', {'data-at': company_name_tag}), 'text'):
            company_name = job.find('div', {'data-at': company_name_tag}).text.strip().replace(',', '-')

        # location of job
        location = '-'
        if hasattr(job.find('li', {'data-at': location_tag}), 'text'):
            location = job.find('li', {'data-at': location_tag}).text.strip().replace(',', '-')

        # time of posting
        pub_data = '-'
        if hasattr(job.find('li', {'data-at': pub_data_tag}), 'text'):
            pub_data = convert_time(job.find('li', {'data-at': pub_data_tag}).text)

        # website for job listing
        job_url = '-'
        if job.find('a', {'data-at': job_description_tag})['href'] is not None:
            job_url_nolink = 'https://www.stepstone.de' + job.find('a', {'data-at': job_description_tag})['href'].strip()
            job_url = '<a href="' + job_url_nolink + '">' + job_url_nolink + '</a>'

        results.append([job_description, company_name, location, pub_data, job_url])

    df = pd.DataFrame(results, columns=header)

    return df


if __name__ == '__main__':
    # profile information
    with open('site_info.json', 'r') as f:
        site_info = json.load(f)

    # job information
    '''
        https://www.stepstone.de/5/ergebnisliste.html?ke=Ingenieurwesen%20Data%20Science
        &ws=Berlin
        &radius=30
        &ag=age_7
        &ct=222
        &wt=80001

        https://de.indeed.com/jobs?q=Ingenieur%20data%20science
        &l=Berlin
        &jt=fulltime
        &fromage=7
    '''

    # basic input
    description = ' '.join(['ingenieur', 'data', 'science'])
    location = 'Muenchen' # München
    age = '1'

    # create url
    site = 'stepstone'
    if (site == 'stepstone'):
        # extra input
        radius = '30'
        contract = '222'
        worktime = '80001'

        url    = site_info['sites']['stepstone']['url']
        params = {'ke': description, 'ws': location, 'radius': radius, 'ag': 'age_' + age, 'ct': contract, 'wt': worktime}
    
    elif (site == 'indeed'):
        url    = site_info['sites']['indeed']['url']
        params = {'': description, 'l': location, 'fromage': age, 'jt': contract}

    # obtain html code
    data = get_data(url, params)
    print('Data was pulled...')

    # with open( 'test.html' , 'r' ) as f:
    #     data = f.read()

    # results array
    data = BeautifulSoup(data, 'html.parser')
    results = get_results(data, description, location, **site_info['sites']['stepstone'])
    print('Job data was extracted...')

    # create html page with results
    results_html = results.to_html(justify='left', escape=False, table_id='sortable')
    filename = location + '.html'
    with open(filename, 'w') as f:
        f.write('<script src="sorttable.js"></script>\n\n')
        f.write(results_html)
    print('HTML File saved')

    # # create csv file with results
    # results.to_csv( 'results.csv', sep=',', encoding='utf-8' )
    # print( 'CSV File saved' )
