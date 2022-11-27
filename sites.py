#!/usr/bin/python3

from os.path  import exists
from json     import load
from requests import get
from bs4      import BeautifulSoup
from pandas   import DataFrame

# load site parameters
def load_parameters():
    
    if exists('./site_info.json'):
        with open('./site_info.json', 'r') as f:
            site_info = load(f)
    else:
        raise FileNotFoundError("The parameter file was not found.")

    return site_info


# get url from input
def get_data(search_criteria: dict, site_params: dict):
    
    url = site_params["url"]
    parameter_names = site_params["search_parameters"]
    parameter_values = search_criteria
    if "age" in parameter_names.keys():
        params = {
            parameter_names["description"]: parameter_values['description'],
            parameter_names['location']: parameter_values['location'],
            parameter_names['radius']: parameter_values['radius'],
            parameter_names['age']: 'age_' + parameter_values['age'],
            parameter_names['contract']: parameter_names['contract_type'],
            parameter_names['worktime']: parameter_names['worktime_type']
        }
    else:
        params = {
            parameter_names["description"]: parameter_values['description'],
            parameter_names['location']: parameter_values['location'],
            parameter_names['radius']: parameter_values['radius'],
            parameter_names['contract']: parameter_names['contract_type'],
            parameter_names['worktime']: parameter_names['worktime_type']
        }
    next_page_tag = parameter_names["next_page_tag"]

    # create object to contain raw data
    raw_data = ''

    # headers for data pulling
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36', }

    page_count = 1
    while True:

        # pull data from the internet
        response = get(url, params=params, headers=headers)

        # extract content
        text = response.text

        soup = BeautifulSoup(text, 'html.parser')
        raw_data += str(soup)

        # check if results are split in multiple pages
        next_page = soup.find(next_page_tag[0], {next_page_tag[1]: next_page_tag[2]})

        if next_page:
            try:
                next_url = next_page['href']
                if next_url and (url != next_url):
                    url = next_url
                    params = None
                    page_count += 1
                else:
                    break
            except Exception as e:
                break
        else:
            break

    # check_pages
    raw_data = BeautifulSoup(raw_data, 'html.parser')

    return raw_data


def convert_time(time_job):
    time_pub = time_job.split()[1:]
    if ('Tag' in time_pub[1]):
        return time_pub[0] + ' days'
    else:
        return '0 days'


# filter job data using
# find_all function
def get_results(data: BeautifulSoup, search_criteria: dict, job_parameters: dict):
    # get parsing tags
    description = search_criteria["description"]
    location = search_criteria["location"]
    job_listing_tag     = job_parameters['job_listing_tag']
    job_description_tag = job_parameters['job_description_tag']
    company_name_tag    = job_parameters['company_name_tag']
    location_tag        = job_parameters['location_tag']
    pub_data_tag        = job_parameters['pub_data_tag']

    # find the Html tag with find() and convert into string
    header = ['Listing name', 'Company name']
    results = []
    for job in data.find_all(job_listing_tag[0], {job_listing_tag[1]: job_listing_tag[2]}):

        # description of job
        job_description = '-'
        if hasattr(job.find(job_description_tag[0], {job_description_tag[1]: job_description_tag[2]}), job_description_tag[3]):
            job_description = job.find(job_description_tag[0], {job_description_tag[1]: job_description_tag[2]}).text.strip().replace(',', '-')
            if (' ' in description):
                description = description.split()
            if any(item in job_description.lower() for item in description):
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

        results.append([job_url, company_name])

    df = DataFrame(results, columns=header)
    df = df.sort_values(by='Company name', ascending=True)

    return df

def write_output(filename: str, results: str):

    with open(filename, 'w') as f:
        f.write(
                '''<!DOCTYPE html>
<html lang="en"/>

<head>

    <link href="style.css" rel="stylesheet">

</head>

<script src="sorttable.js"></script>
<script src="function.js"></script>

<body>

    <section class="container">

        <h1>Table Filter</h1>

        <input type="search" class="light-table-filter" data-table="table-info" placeholder="Filter/Search">
            '''
        )
        f.write(results.replace('class="dataframe"', 'class="table-info table"'))
        f.write(
                '''
    </section>

</body>

</html>
            '''
        )
