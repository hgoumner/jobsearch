#!/usr/bin/env python3

# import modules
from sites import load_parameters, get_data, get_results, write_output
from pandas import DataFrame, concat

# main function
def main():

    '''
        --- job information ---

        https://www.stepstone.de/5/ergebnisliste.html?ke=Ingenieurwesen%20Data%20Science
        &ws=Berlin
        &radius=30
        &ag=age_7
        &ct=222
        &wt=80001

        https://www.kimeta.de/search?q=simulation
        &loc=Berlin
        &r=20
        &pf=besch%C3%A4ftigungsart%40Festanstellung
        &pf=zeitintensit%C3%A4t%40Vollzeit
    '''

    # load parameters
    site_info = load_parameters()
    search_criteria = site_info["search_criteria"]
    print('\n1/3 Parameters were loaded')

    # get job data
    results = DataFrame()
    for site in site_info["sites"].keys():

        # obtain html code
        data = get_data(search_criteria, site_info["sites"][site])

        # results array
        df_new = get_results(data, search_criteria, site_info["sites"][site]["job_parameters"])
        data = [results, df_new]
        results = concat(data)

    print('\n2/3 Job data was pulled and extracted')

    # create html page with results
    results_html = results.to_html(justify='center', escape=False, table_id='sortable')
    filename = search_criteria["location"] + '.html'
    write_output(filename, results_html)
    print('\n3/3 HTML File saved')

if __name__ == "__main__":
    main()
