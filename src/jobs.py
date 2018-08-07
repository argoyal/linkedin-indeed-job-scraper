# -*- coding: utf-8 -*-

from collections import OrderedDict
import datetime
from settings import config

import collections.abc
import json
import os
import pymongo

class job(object):
    """ Internal Job object. Mainly used for saving jobs crawled from websites """

    keylist = ['Title', 'URL', 'Company', 'Location', 'Time', 'Seniority Level',
                'Industry', 'Employment Type', 'Job Functions', 'Job Details',
                'Job Details Text', 'Job Details HTML', 'Job Details Contents']
    def __init__(self, title, url, company, location, time, Seniority_Level, Industry, Employment_Type, Job_Functions, job_details, job_details_text, job_details_html):
        self.title                = title
        self.url                  = url
        self.company              = company
        self.location             = location
        self.time                 = time
        self.Seniority_Level      = Seniority_Level
        self.Industry             = Industry
        self.Employment_Type      = Employment_Type
        self.Job_Functions        = Job_Functions
        self.job_details          = job_details
        self.job_details_text     = job_details_text
        self.job_details_html     = job_details_html

    def toDict(self):
        """ convert job object into python dictionary object """
        diction = OrderedDict()
        diction['Title']                = self.title
        diction['URL']                  = self.url
        diction['Company']              = self.company
        diction['Location']             = self.location
        diction['Time']                 = self.time
        diction['Seniority Level']      = self.Seniority_Level
        diction['Industry']             = self.Industry
        diction['Employment Type']      = self.Employment_Type
        diction['Job Functions']        = self.Job_Functions
        diction['Job Details']          = self.job_details
        diction['Job Details Text']     = self.job_details_text
        diction['Job Details HTML']     = self.job_details_html

        return diction


class jobs(collections.abc.Mapping):
    """ Stored all job object """
    def __init__(self, homePath, job_keyword, location):
        self.jobs               = OrderedDict()
        self.homePath           = homePath
        self.job_keyword        = job_keyword
        self.location           = location

        self.db_settings = config['database_config']

        self.client = pymongo.MongoClient(
            self.db_settings['DB_HOST'],
            self.db_settings['DB_PORT']
        )
        self.db = self.client[self.db_settings.get('DB_NAME')]

    def __getitem__(self, key): # given a key, return it's value
        return self.jobs[key]

    def __iter__(self):
        for x in self.jobs.keys():
            yield x

    def __len__(self):
        return len(self.jobs)

    def __repr__(self):
        return repr(self.jobs)

    def __contains__(self, item):
        return (item in self.jobs.keys())

    def toDict(self):
        diction = OrderedDict()
        for key, value in self.jobs.items():
            diction[key] = value.toDict()
        return diction

    def addJob(self, key, job):
        """
        converted the function to save the data in the database
        """
        print("adding job with key: {}".format(key))
        job_details = job.toDict()
        job_details.update({
            'search_information': {
                'keyword': self.job_keyword,
                'location': self.location,
                'created_key': key
            }
        })

        self.db.linkedin_jd.insert(job_details)
        # self.jobs[key] = job

    def toJSON(self):
        pathOut = os.path.join(self.homePath, 'repository', '{0}({1})'.format(self.job_keyword, self.location),datetime.date.today().strftime("%Y-%m-%d"), 'json')
        os.makedirs(pathOut, exist_ok=True)
        for key, value in self.jobs.items():
            with open(os.path.join(pathOut, key)+'.json', 'w', encoding='utf-8') as file:
                json.dump(value.toDict(), file, indent=4, sort_keys=True, ensure_ascii=False)

    def toMarkdown(self):
        pathOut = os.path.join(self.homePath, 'repository', '{0}({1})'.format(self.job_keyword, self.location), datetime.date.today().strftime("%Y-%m-%d"), 'markdown')
        os.makedirs(pathOut, exist_ok=True)
        template = open(os.path.join(self.homePath, 'src', 'template') + '.md', encoding='utf-8').read()
        for key, value in self.jobs.items():
            diction = value.toDict()
            with open(os.path.join(pathOut, key)+'.md', 'w', encoding='utf-8') as f:
                job_details = diction.get('Job Details')
                job_detailsTXT = ''
                for k, v in job_details.items():
                    job_detailsTXT += ('\n#### {0}'.format(k)) + ''.join(['\n* '+ str_ for str_ in v])
                print(template.format(fileName=key, time=diction.get('Time'),
                                      title=diction.get('Title'), company=diction.get('Company'),
                                      url=diction.get('URL'), location=diction.get('Location'),
                                      employmentType=', '.join(diction.get('Employment Type')), Industry=', '.join(diction.get('Industry')),
                                      jobFunctions=', '.join(diction.get('Job Functions')), jobDetails=job_detailsTXT.strip()),
                                      file=f)

    def inJSON(self, fileName):
        with open(fileName, encoding='utf-8') as file:
            data = json.load(file, object_pairs_hook=OrderedDict, encoding='utf-8')
        for key, value in data.items():
            title                = value.get('Title', '')
            url                  = value.get('URL', '')
            company              = value.get('Company', '')
            location             = value.get('Location', '')
            time                 = value.get('Time', '')
            Seniority_Level      = value.get('Seniority Level', '')
            Industry             = value.get('Industry', '')
            Employment_Type      = value.get('Employment Type', '')
            Job_Functions        = value.get('Job Functions', '')
            job_details          = value.get('Job Details', '')
            #job_details_text     = value.get('Job Details Text', '')
            #job_details_html     = value.get('Job Details HTML', '')
            JOB = job(title, url, company, location, time, Seniority_Level, Industry, Employment_Type, Job_Functions, job_details)
            self.addJob(key, JOB)
