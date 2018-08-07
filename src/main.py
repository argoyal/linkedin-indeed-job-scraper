# -*- coding: utf-8 -*-
import os
import json
try:
    os.chdir(r'C:\Users\chase\Documents\GitHub\job_scrape\src')
except:
    pass
from scrape_linkedin import linkedinJob
from scrape_indeed import indeedJob


def parseAuthkey(web, authkeyPath):
    """
    parses the auth key
    """

    authkey = json.load(open(authkeyPath))

    return authkey[web]['email'], authkey[web]['password']


def scrape(website, email, password, job_keyword,
           location, filterByDate, sortBy):

    websiteList = {'linkedin': linkedinJob, "indeed": indeedJob}
    jobType = websiteList[website]
    global job_scrape
    job_scrape = jobType(homePath)
    job_scrape.logIn(email, password)
    job_scrape.search(job_keyword, location)
    job_scrape.customSearch(filterByDate, sortBy)
    job_scrape.scroll()
    # job_scrape.job_list.toJSON()
    # job_scrape.job_list.toMarkdown()
    job_scrape.driverQuit()


if __name__ == "__main__":
    from settings import config

    website = config['website']
    homePath = config['homePath']
    authkey = config['authkey']

    email, password = parseAuthkey(website, authkey)

    job_keyword = config['keywords']
    location = config['locations'][0]
    date_range = config['date_range']
    sort_by = config['sort_by']

    for i in range(len(job_keyword)):
        print('Searching for job_keyword: {}'.format(job_keyword[i]))
        scrape(website, email, password, job_keyword[i],
               location, date_range[website], sort_by)
