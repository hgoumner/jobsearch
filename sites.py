#!usr/bin/env python3

import json
import requests
import bs4

# parse html code
def html_code( data ):

    return bs4.BeautifulSoup( data, 'html.parser' )

# get url from input
def get_data( url ):
    
    while True:
        # pull data from the internet
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',}
        response = requests.get( url, headers=headers )

        # extract content
        text = response.text

        # create object to contain raw data
        raw_data = text

        # check if results are split in multiple pages
        soup = html_code( text )
        count = 0
        next_page = soup.find("a", {"title": "Nächste"})
        # print(next_page)

        if next_page:
            # next_url = next_page.find("a", href=True)
            next_url = next_page['href']
            print(next_url)

            if next_url:
                url = next_url
            else:
                break
        else:
            break

    # check_pages
    return raw_data

# filter job data using
# find_all function
def job_data(soup):
    
    # find the Html tag
    # with find()
    # and convert into string
    data_str = ""
    for item in soup.find_all("a", class_="sc-qapaw ERzaP"):
        data_str = data_str + item.get_text()
    result_1 = data_str.split("\n")

    return(result_1)


# # filter company_data using
# # find_all function
# def company_data(soup):
#   
#     # find the Html tag
#     # with find()
#     # and convert into string
#     data_str = ""
#     result = ""
#     for item in soup.find_all("div", class_="sc-qapaw ERzaP"):
#         data_str = data_str + item.get_text()
#     result_1 = data_str.split("\n")
#   
#     res = []
#     for i in range(1, len(result_1)):
#         if len(result_1[i]) > 1:
#             res.append(result_1[i])
#     return(res)

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

    # obtain html code
    data =  get_data( url )
    # print(data)

    # job_res = job_data( soup )
    # com_res = company_data( soup )
    # print(job_res)
    #
    # temp = 0
    # for i in range( 1, len( job_res )):
    #     j = temp
    #     for j in range( temp, 2+temp ):
    #         print( "Company Name and Address:" + com_res[j])
    #
    #     temp = j
    #     print( "Job: " + job_res[i])
    #     print("--------------------------")
