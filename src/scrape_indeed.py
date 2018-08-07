# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import bs4
from bs4 import BeautifulSoup

from time import sleep
import chromedriver_binary
import datetime
from urllib.parse import urljoin

from jobs import job
from jobs import jobs
import re

class indeedJob():
    def __init__(self, homePath, driver='chrome', sleep_sec_interval=10):
        if driver.upper() == 'CHROME':
            self.driver = webdriver.Chrome()
            self.driver.get("https://cn.indeed.com/")
            self.driver.maximize_window()
        else:
            raise "Only CHROME is supported now"

        self.homePath           = homePath
        self.sleep_sec_interval = sleep_sec_interval
        self.wait               = WebDriverWait(self.driver, self.sleep_sec_interval)
        self.id                 = 0

    def logIn(self, email, password):
        login = self.driver.find_element_by_css_selector('ul[class="icl-DesktopGlobalHeader-items icl-DesktopGlobalHeader-items--right"]')
        loginbutton = login.find_elements_by_css_selector('li[class="icl-DesktopGlobalHeader-item"]')[1]
        loginbutton.click()

        sleep(5)

        # fill in username
        email_elem = self.driver.find_element_by_id('signin_email')
        email_elem.clear()
        email_elem.send_keys(email)

        # fill in password
        pass_elem = self.driver.find_element_by_id('signin_password')
        pass_elem.clear()
        pass_elem.send_keys(password)
        # sign in button
        self.driver.find_element_by_css_selector("button[class='sg-btn sg-btn-primary btn-signin']").click()


    def driverQuit(self):
        """ Quit driver """
        self.driver.quit()

    def search(self, job_keyword, location):
        self.job_keyword        = job_keyword
        self.location           = location
        self.job_list           = jobs(self.homePath, self.job_keyword, self.location)

        # fill in search keyword
        keyword_search = self.wait.until(EC.presence_of_element_located((By.ID, 'text-input-what')))
        keyword_search.send_keys(self.job_keyword)

        # fill in location
        location_search = self.wait.until(EC.presence_of_element_located((By.ID, 'text-input-where')))
        location_search.clear()
        # clear text box as element.clear() not working
        for i in range(50):
            location_search.send_keys(Keys.BACKSPACE)
        location_search.send_keys(self.location)

        # search
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[class="icl-WhatWhere-button"]'))).click()


    def customSearch(self, filterByDate='Any Time', sortBy='relevance'):
        """custom search results by either filter date posted or sort criteria"""
        # custom filter criteria by date
        valuelist = ['any', '15', '7', '3', '1', 'last']
        if filterByDate not in valuelist or filterByDate == 'Any Time':
            pass
        else:
            advancedSearch = self.driver.find_element_by_css_selector('td[class="npl advanced-search"]').find_element_by_css_selector('a[class="sl"]').click()
            select = Select(self.driver.find_element_by_id('fromage'))
            select.select_by_value(filterByDate)
            self.driver.find_element_by_id('fj').click()
            sleep(4)

        # custom sort criteria
        if sortBy == "relevance":
            pass
        elif sortBy == 'post date':
            self.driver.find_element_by_css_selector('span[class="no-wrap"]').find_element_by_tag_name('a').click()
        else:
            print("sortBy not in ('relevance' 'post date')\nusing default sort: relevance")
        sleep(5)

    def scroll(self):
        """
            scroll every job finding page to get all job search result
            results are stored in jobs object
        """

        remain = True
        self.screened = ['1']

        while remain == True:
            remain = False

            # cancel pop up page
            try:
                popup = self.driver.find_element_by_id('popover-close-link')
                popup.click()
            except:
                pass
            # parse jobs in whole page
            buttonList = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div[data-tn-component="organicJob"]')))

            n = 1
            for button in buttonList:
                n+=1
                print(n)
                href = button.find_element_by_css_selector('h2[class="jobtitle"]')
                href.click()
                sleep(4)
                self.scrape()

            # to next page
            try:
                pageList = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="pagination"]')))
            except TimeoutException:
                break

            page = pageList.find_elements_by_tag_name('a')[-1]
            if page.text.find('下一页') >= 0:
                remain = True
                page.send_keys("\n")
                sleep(4)

    def scrape(self):
        """ scrape job information from the current page """
        self.wait.until(EC.presence_of_element_located((By.ID, 'vjs-desc')))
        content                    = self.driver.page_source
        soup                       = BeautifulSoup(content, 'lxml').find(id='vjs-container')
        parseTopCard               = self.parseTopCard(soup)
        parseJobDetails            = self.parseJobDetails(soup)

        self.id += 1
        key = "Indeed-{date}[{id:03d}]".format(date=datetime.date.today().strftime("%Y-%m-%d"), id=self.id)
        JOB = job(parseTopCard['Job Title'], parseTopCard['url'], parseTopCard['Company Name'], parseTopCard['Company Location'], parseTopCard['Post Date'],
                  '', '', '', '',
                  parseJobDetails[0], parseJobDetails[1], parseJobDetails[2])
        self.job_list.addJob(key, JOB)
        sleep(4)


    def parseTopCard(self, soup):
        out                     = {}
        out['Job Title']        = soup.find(id='vjs-jobtitle').text.strip()
        out['Company Name']     = soup.find(id='vjs-cn').text.strip()
        out['Company Location'] = soup.find(id='vjs-loc').text.strip()
        footer                  = soup.find(id='vjs-footer')
        out['url']              = urljoin('https://cn.indeed.com/', footer.select('a[class*="sl ws_label"]')[0].get('href', ''))


        date = footer.find(class_='date').text
        if '小时' in date or 'hour' in date:
            out['Post Date'] = datetime.date.today().strftime("%Y-%m-%d")
        else:
            daten = int(re.findall('\d+', date )[0])
            out['Post Date'] = (datetime.date.today() + datetime.timedelta(days=daten)).strftime("%Y-%m-%d")
        return out

    def parseJobDetails(self, soup):
        keyWordList = ['']
        job_details          = soup.find(id='vjs-desc')
        job_details_text     = list(job_details.stripped_strings)
        job_details_html     = job_details.prettify()
        out                  = {'Job Description':[]}
        keyword              = 'Job Description'

        for child in job_details.children:
            if type(child) == bs4.element.Comment:
                pass
            elif type(child) == bs4.element.NavigableString:
                string = child.string.strip()
                if string and string.upper() != "JOB DESCRIPTION":
                    for str_ in string.split('\n'):
                        out[keyword].append(str_.strip())
            else:
                text = child.text.strip()
                if text:
                    if child.find('b') or child.name == 'b':
                        keyword = text
                        out[keyword] = []
                    elif text.upper() == "JOB DESCRIPTION":
                        pass
                    else:
                        for str_ in text.split('\n'):
                            out[keyword].append(str_.strip())
        return (out, job_details_text, job_details_html)
