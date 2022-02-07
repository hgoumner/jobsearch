#!usr/bin/env python3

import json
import requests
import bs4

# parse html code
def html_code( data ):

    soup = bs4.BeautifulSoup( data, 'html.parser' )

    return soup

# get url from input
def get_data( url ):
    
    # create string object to contain raw data
    raw_data = ''

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',}
    s = requests.Session()
    response = s.post( url, headers=headers )
    text = response.text
    html_text = html_code( text )

    raw_data += str( html_text )

    new_page = html_text.find_all( 'a', {'class' : 'PageLink-sc-1v4g7my-0 gwcKwa'} )
    new_page = new_page[0]

    count = 0
    while (new_page['href'] != '') and (count < 70):
        response = s.post( new_page['href'], headers=headers )
        text = response.text
        html_text = html_code( text )

        raw_data += str(html_text)
        # print(count)
        count += 1

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
    location    = 'München'
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
    print(data)

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
