#!/usr/bin/python3

import sys
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd


# get url from input
def get_data(url, params, next_page_tag):

    # create object to contain raw data
    raw_data = ''

    # headers for data pulling
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', }

    page_count = 1
    while True:

        # pull data from the internet
        response = requests.get(url, params=params, headers=headers)

        # extract content
        text = response.text

        soup = BeautifulSoup(text, 'html.parser')
        raw_data += str(soup)

        print("Page %d" % page_count)
        
        # check if results are split in multiple pages
        next_page = soup.find(next_page_tag[0], {next_page_tag[1]: next_page_tag[2]})

        if next_page:
            try:
                next_url = next_page['href']
                if ('http' not in next_url):
                    next_url = 'https://de.indeed.com' + next_url

                if next_url:
                    url = next_url
                    page_count += 1
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
def get_results(data, desc=None, loc=None, **kwargs):
    # get parsing tags
    job_listing_tag     = kwargs['job_listing_tag']
    job_description_tag = kwargs['job_description_tag']
    company_name_tag    = kwargs['company_name_tag']
    location_tag        = kwargs['location_tag']
    pub_data_tag        = kwargs['pub_data_tag']

    # find the Html tag with find() and convert into string
    header = ['Listing name', 'Company name', 'Location', 'Age']
    results = []
    for job in data.find_all(job_listing_tag[0], {job_listing_tag[1]: job_listing_tag[2]}):

        # description of job
        job_description = '-'
        if hasattr(job.find(job_description_tag[0], {job_description_tag[1]: job_description_tag[2]}), job_description_tag[3]):
            job_description = job.find(job_description_tag[0], {job_description_tag[1]: job_description_tag[2]}).h2.text.strip().replace(',', '-')
            if (' ' in desc):
                desc = desc.split()
            if any(item in job_description.lower() for item in desc):
                job_url_nolink = 'https://www.stepstone.de' + job.find(job_description_tag[0], {job_description_tag[1]: job_description_tag[2]})['href'].strip()
                job_url = '<a href="' + job_url_nolink + '">' + job_description + '</a>'
                # pass
            else:
                break

        # name of company
        company_name = '-'
        if hasattr(job.find(company_name_tag[0], {company_name_tag[1]: company_name_tag[2]}), 'text'):
            company_name = job.find(company_name_tag[0], {company_name_tag[1]: company_name_tag[2]}).text.strip().replace(',', '-')

        # location of job
        location = '-'
        if hasattr(job.find(location_tag[0], {location_tag[1]: location_tag[2]}), 'text'):
            location = job.find(location_tag[0], {location_tag[1]: location_tag[2]}).text.strip().replace(',', '-')

        # time of posting
        pub_data = '-'
        if hasattr(job.find(pub_data_tag[0], {pub_data_tag[1]: pub_data_tag[2]}), 'text'):
            pub_data = convert_time(job.find(pub_data_tag[0], {pub_data_tag[1]: pub_data_tag[2]}).text)

        # # website for job listing
        # job_url = '-'
        # if job.find('a', {'data-at': job_description_tag})['href'] is not None:
        #     job_url_nolink = 'https://www.stepstone.de' + job.find('a', {'data-at': job_description_tag})['href'].strip()
        #     job_url = '<a href="' + job_url_nolink + '">' + job_url_nolink + '</a>'
        #
        results.append([job_url, company_name, location, pub_data])

    df = pd.DataFrame(results, columns=header)

    return df.sort_values(by='Company name', ascending=True)


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
    description = ' '.join(['ingenieur', 'engineer', 'modelica', 'simulation'])
    location    = 'Berlin'                                          #sys.argv[1]
    age         = '1'                                               #sys.argv[2]

    # create url
    site = 'stepstone'
    if (site == 'stepstone'):
        # extra input
        radius = '30'
        contract = '222'
        worktime = '80001'

        url    = site_info[site]['url']
        params = {'ke': description, 'ws': location, 'radius': radius, 'ag': 'age_' + age, 'ct': contract, 'wt': worktime}
        next_page_tag = site_info[site]['next_page_tag']
    
    elif (site == 'indeed'):
        # extra input
        contract = 'fulltime'

        url    = site_info[site]['url']
        params = {'q': description, 'l': location, 'fromage': age, 'jt': contract}
        next_page_tag = site_info[site]['next_page_tag']

    # obtain html code
    data = get_data(url, params, next_page_tag)
    print('\n1/3 Data was pulled')

    # with open( 'indeed.html' , 'r' ) as f:
    #     data = f.read()
 
    # results array
    data = BeautifulSoup(data, 'html.parser')
    results = get_results(data, description, location, **site_info[site])
    print('2/3 Job data was extracted')

    # create html page with results
    results_html = results.to_html(justify='center', escape=False, table_id='sortable')
    filename = location + '.html'
    with open(filename, 'w') as f:
        f.write(
                '''<!DOCTYPE html>
<html lang="en"/>

<head>

    <link href="style.css" rel="stylesheet">

</head>

<script src="sorttable.js"></script>
<script src="function.js"></script>
<script src="hotkeys.js"></script>
<script src="key_shortcuts.js"></script>

<body>

    <section class="container">

        <h1>Table Filter</h1>

        <input type="search" class="light-table-filter" data-table="table-info" placeholder="Filter/Search">
            '''
        )
        f.write(results_html.replace('class="dataframe"', 'class="table-info table"'))
        f.write(
                '''
    </section>

</body>

</html>
            '''
        )
    print('3/3 HTML File saved')

    # # create csv file with results
    # results.to_csv( 'results.csv', sep=',', encoding='utf-8' )
    # print( 'CSV File saved' )
