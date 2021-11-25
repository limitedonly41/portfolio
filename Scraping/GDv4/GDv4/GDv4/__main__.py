import os
import platform
import signal
import sys

import argparse
import time
from random import randrange
import pandas as pd

# from loginform import fill_login_form

import bs4
import requests
from bs4 import BeautifulSoup, Tag
from datetime import date, datetime, timezone
from selenium import webdriver

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.webdriver import WebDriver
# from selenium.webdriver.firefox.options import Options


from tqdm import tqdm


class Parser:
    allowed_ext = ['pdf', 'xls', 'doc']

    url_domain = 'technology.globaldata.com'

    login_url = 'https://login.globaldata.com/login/index/technology'
    url_post = 'https://login.globaldata.com/Login/Index/technology?ReturnUrl=https://technology.globaldata.com/'
    # '301852&publisheddate=1530392400000-1564606799999&direction=Descending&startdatefrom=1530392400000&startdateto=1564606799999'

    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    ]

    # _current_dir = os.path.dirname(os.path.realpath(__file__))

    #
    browser: WebDriver = None
    browser_cookies = None

    request_session = None
    request_cookies = {}

    xls = []

    ################
    login = ''
    password = ''
    mapping_file = ''
    result_path = ''
    start_date = ''
    end_date = ''

    def __init__(self, login, password, mapping_file, result_path, start_date=None, end_date=None):
        dir_path = os.path.dirname(os.path.realpath(__file__))

        self.result_path = os.path.join(dir_path, result_path)
        print('Result output foder: %s ' % self.result_path )

        self.login = login
        self.password = password
        self.mapping_file = mapping_file

        self.end_date = end_date
        self.start_date = start_date

    def start_page(self):
        # TODO: redirect use JS, use Selenium
        # session = requests.Session()
        # r = session.get(self.login_url)
        # login_info = fill_login_form(self.login_url, r.text, self.login, self.password)
        # e = session.request(login_info[2], login_info[1], data=login_info[0])

        chrome_options = webdriver.ChromeOptions()
        chrome_options.accept_untrusted_certs = True
        chrome_options.assume_untrusted_cert_issuer = True

        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-impl-side-painting")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-seccomp-filter-sandbox")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-cast")
        chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
        chrome_options.add_argument("--disable-cloud-import")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-session-crashed-bubble")
        chrome_options.add_argument("--disable-ipv6")
        chrome_options.add_argument("--allow-http-screen-capture")
        # chrome_options.add_argument("--start-maximized")

        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        _drivers_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'drivers', platform.system(), 'chromedriver')

        if platform.system() == 'Windows':
            _drivers_path += 'chromedriver.exe'
            # _drivers_path = os.path.join(_drivers_path, 'chromedriver.exe')
        #   executable_path=_drivers_path
        self.browser = Chrome(options=chrome_options, executable_path='drivers/chromedriver.exe')
        self.browser.get(self.login_url)

        return self.browser

    def handle_login(self):
        search_form = self.browser.find_element_by_xpath("(//input[@class='input-group-field'])[1]")
        search_form.send_keys(self.login)

        search_form = self.browser.find_element_by_xpath("(//input[@class='input-group-field'])[2]")
        search_form.send_keys(self.password)

        search_form.submit()

        # self.browser.get(self.url_find_prefix)

        # convert cookies from browser to requests dict
        browser_cookies = self.browser.get_cookies()
        # self.requst_cookies = {x['name']: x['value'] for x in browser_cookies}

        self.request_session = requests.Session()
        self.request_session.headers = {
            'user-agent': self.user_agents[randrange(len(self.user_agents))],
        }

        # setup cookies to every request
        self.request_cookies = {x['name']: x['value'] for x in browser_cookies}

        # r = session.get(
        #     'https://technology.globaldata.com/Analysis/ExportFullReportToPdf/smart-cities-in-europe-regional-status-key-case-studies',
        #     # headers=self.headers,
        #     cookies=self.browser_cookies,
        # )
        #
        # with open('__html.html', 'wb') as f:
        #     f.write(r.content)
        #

        # with self.requests_session as s:
        #     # for cookie in broser_cookies[0]:
        #     #     s.cookies.set(cookie['name'], cookie['value'])
        #
        #     r = s.get(
        #         'https://technology.globaldata.com/Analysis/ExportFullReportToPdf/smart-cities-in-europe-regional-status-key-case-studies',
        #         # headers=self.headers, cookies=requst_cookies
        #     )
        #     soup = BeautifulSoup(r.content, features="html.parser")
        #     el = soup.find('reportsTable')
        #     #
        #     #     r = s.post(url_post, data=login_data, headers=headers)
        #     #
        #     with open('html.html', 'wb') as f:
        #         f.write(r.content)
        #     pass

        return self.request_session

    def page_parse_items(self, industry_index):
        url_find_prefix = 'https://technology.globaldata.com/Analysis?pageSize=100&industry='
        res = []

        # with open('__html.html', 'wb') as f:
        #     f.write(r.content)

        page_number = 1

        data_sufix = ''

        if self.start_date and self.start_date:
            # int_start_date = int(datetime.strptime(self.start_date, '%d.%m.%Y').timestamp())
            int_start_date = self.str_date_to_epoch_time(self.start_date)
            int_end_date = self.str_date_to_epoch_time(self.end_date)

            data_sufix = '&publisheddate={start_date}-{end_date}&startdatefrom={start_date}&startdateto={end_date}'. \
                format(start_date=int_start_date, end_date=int_end_date)

        while True:
            page_sufix = '&pageNumber=' + str(page_number) if page_number > 1 else ''

            url = '{prefix}{industry_index}{data_sufix}{page_sufix}'.format(
                prefix=url_find_prefix,
                industry_index=industry_index,
                data_sufix=data_sufix,
                page_sufix=page_sufix,
            )

            # url = 'https://technology.globaldata.com/Analysis?pageSize=100&industry=301032'

            page_number += 1
            # print(url)

            r = self.request_session.get(url=url, cookies=self.request_cookies)
            soup = BeautifulSoup(r.content, features="html.parser")

            results_table = soup.find('table', id='reportsTable')
            # no search results
            if not results_table:
                break

            # have results
            # for row in soup.find('table', id='reportsTable').tbody.findAll('tr'):
            for row in results_table.tbody.findAll('tr'):
                second_column = row.findAll('td')[1].contents
                files_list = [x for x in second_column if type(x) is bs4.element.Tag]

                for file in files_list:
                    file_name_content = file.attrs['href']

                    file_url = 'https://technology.globaldata.com' + file_name_content
                    file_ext = file.contents[1].attrs['src'] \
                        .replace('/Content/images/icon_', '') \
                        .replace('.gif', '')

                    file_ext = file_ext.replace('word', 'doc')
                    file_ext = file_ext.replace('excel', 'xlsx')

                    file_name = file_name_content.split('/')[-1].replace('?', '_').replace('=', '_') + '.' + file_ext

                    # print(file_name, file_url)
                    res.append((file_name, file_url))

            # break
            # break if not have next page
            if not self.page_have_next(soup):
                break

        return res

    @staticmethod
    def str_date_to_epoch_time(sdate):
        return int(datetime.strptime(sdate, '%d.%m.%Y').timestamp())

    @staticmethod
    def page_have_next(soup):
        res = False

        # with open('html.html', 'rb') as f:
        #     content = f.read()
        #     soup = BeautifulSoup(content, features="html.parser")

        next_button: bs4.element.Tag = soup.find('form', 'paginationForm')
        next_link = next_button.find('a', {'id': 'nextLink'})
        # _ = next_button.findAll('nextLink')
        if next_link:
            res = next_link

        return res

    def xls_parse(self):
        # res = []

        xls = pd.ExcelFile(self.mapping_file)
        df = xls.parse(0)  # sheet number
        xls.close()

        for index, row in df.iterrows():
            url = row[0]
            path = ''.join(map(str, [x.replace('/', ' ') + '/' for x in row if type(x) is str]))

            self.xls.append((url, path))

        assert 'Mapping file empty', len(self.xls)
        return self.xls

    def download_files(self, download_list):
        pbar = tqdm(download_list)
        pbar.set_description('Downloading files...')

        for file in pbar:
            url = file[2]
            directory = os.path.join(self.result_path, file[0])
            file_name = os.path.join(directory, file[1])

            pbar.set_postfix(url=url)

            if not os.path.exists(directory):
                os.makedirs(directory)

            r = requests.get(url=url, cookies=self.request_cookies)

            with open(file_name, 'wb') as f:
                f.write(r.content)

            # Stream save to file
            # r = requests.get(url=url, cookies=self.request_cookies, stream=True)
            # with open(file_name, 'wb') as f:
            #     for chunk in r.iter_content():
            #         f.write(chunk)

            pass

    def runall(self):
        print('\nParse mapping file...')
        self.xls_parse()

        print('\nEnter to login page..')
        self.start_page()

        print('\nLogin...')
        self.handle_login()

        # if not self.requst_cookies:
        assert 'Error get page cookies or login incorrect', self.request_cookies

        # print('\nProcess pages...')

        download_list = []

        pbar = tqdm(self.xls)
        pbar.desc = 'Process pages...'

        for val in pbar:
            industry_index, path = val
            # path = val[1]

            # print('\nProcess page [%s, %s]: %s' % (index, len(self.xls), path))
            page_items = self.page_parse_items(industry_index)
            # print('\nFind files: %s' % len(page_items))
            pbar.set_postfix(path=path)

            for file_name, file_url in page_items:
                download_item = (path, file_name, file_url)

                download_list.append(download_item)

        # print('\nDownloading files...')
        self.download_files(download_list)

        print('\nAll done!')

        return 0


def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)


# @easyargs
def main():
    parser = argparse.ArgumentParser(
        description='Parser globaldata.com', epilog='by MMM_Corp, skype: mmm_ogame',
        usage='sample params: -l abaalnamlah@stc.com.sa -p Pass2019! -m Mapping+for+GlobalData.xlsx -s 01.01.2020 -e 02.01.2020 -r results',
    )

    parser.add_argument('-l', type=str, help='login')
    parser.add_argument('-p', type=str, help='password')

    parser.add_argument('-m', help='mapping filename', required=True)
    parser.add_argument('-r', default='results', help='result path')

    parser.add_argument('-s', type=str, help='start data')
    parser.add_argument('-e', type=str, help='end data')

    args = parser.parse_args()

    ##############################
    web_parser = Parser(args.l, args.p, args.m, args.r, args.s, args.e)
    return web_parser.runall()


if __name__ == '__main__':
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    sys.exit(main())
