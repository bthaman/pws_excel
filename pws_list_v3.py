'''
Note: DataFrame .append method deprecated starting in Pandas 2.0.
Last time I ran this (2/26/2024) I used Pandas 1.5.3
'''

import lxml.html
import requests
import pandas as pd
import re
import msgbox


class CountyPWS:
    def __init__(self):
        self.county = None
        self.detail_urls = []
        self.fact_sheet_urls = []
        self.summary_sheet_urls = []
        self.pws_names = []
        self.pws_numbers = []
        self.dict_names = {}

    def get_county(self):
        return self.county

    def get_urls(self, county):
        self.county = re.sub(r'\s', r'%20', county)
        base_url = 'https://dww2.tceq.texas.gov/DWW/JSP/'
        url = 'https://dww2.tceq.texas.gov/DWW/JSP/SearchDispatch?number=&name=&ActivityStatusCD=All&county=' \
              + self.county + '&WaterSystemType=All&SourceWaterType=All&SampleType=null&begin_date=10%2F4%2F2014' \
              '&end_date=10%2F4%2F2016&action=Search+For+Water+Systems'
        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.103 Safari/537.36'}
        r = requests.get(url=url, headers=headers)
        doc = lxml.html.fromstring(r.content)
        tables = doc.findall('.//table')
        # links are in the 3rd table
        pws_table = tables[2]
        # each pws's info is in a separate tr
        rows = pws_table.findall('.//tr')
        # get all the 'a' tags in each row: each pws has three "a" tags
        pws_a_tags = [row.findall('.//a') for row in rows[1:]]

        # use a list comprehension to get all the url's
        #     the water sys detail link is in the first tag within each pws
        self.detail_urls = [base_url + re.sub(r'\s', '', pws[0].get('href')) for pws in pws_a_tags]
        #     the water sys fact sheet link is in the second tag within each pws
        self.fact_sheet_urls = [base_url + re.sub(r'\s', '', pws[1].get('href')) for pws in pws_a_tags]
        #     the water sys summary sheet link is in the third tag within each pws
        self.summary_sheet_urls = [base_url + re.sub(r'\s', '', pws[2].get('href')) for pws in pws_a_tags]
        # return a list of tuples: first tuple is detail url, second is the fact sheet url, third is summary sheet url
        return list(zip(self.detail_urls, self.fact_sheet_urls, self.summary_sheet_urls))

    def get_pws_names(self, county):
        self.county = re.sub(r'\s', r'%20', county)
        base_url = 'https://dww2.tceq.texas.gov/DWW/JSP/'
        url = 'https://dww2.tceq.texas.gov/DWW/JSP/SearchDispatch?number=&name=&ActivityStatusCD=All&county=' \
              + self.county + '&WaterSystemType=All&SourceWaterType=All&SampleType=null&begin_date=10%2F4%2F2014' \
              '&end_date=10%2F4%2F2016&action=Search+For+Water+Systems'
        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.103 Safari/537.36'}
        r = requests.get(url=url, headers=headers)
        doc = lxml.html.fromstring(r.content)
        tables = doc.findall('.//table')
        # names are in the 3rd table
        pws_table = tables[2]
        # each pws's info is in a separate tr
        rows = pws_table.findall('.//tr')

        # get all the 'a' tags in each row: each pws has three "a" tags
        pws_a_tags = [row.findall('.//a') for row in rows[1:]]
        self.pws_numbers = [pws[0].text_content().strip() for pws in pws_a_tags]
        # use a list comprehension to get all the names
        #     the water sys name is in the first tag within each pws
        self.pws_names = [pws[0].get('title') for pws in pws_a_tags]
        self.detail_urls = [base_url + re.sub(r'\s', '', pws[0].get('href')) for pws in pws_a_tags]
        #     the water sys fact sheet link is in the second tag within each pws
        self.fact_sheet_urls = [base_url + re.sub(r'\s', '', pws[1].get('href')) for pws in pws_a_tags]
        #     the water sys summary sheet link is in the third tag within each pws
        self.summary_sheet_urls = [base_url + re.sub(r'\s', '', pws[2].get('href')) for pws in pws_a_tags]
        list_urls = list(zip(self.detail_urls, self.fact_sheet_urls, self.summary_sheet_urls))
        return dict(zip(self.pws_names, list_urls))

    @staticmethod
    def _unpack(row, kind='td'):
        elts = row.findall('.//%s' % kind)
        # if the tag was found, the list has members and its boolean is True
        if elts:
            return [val.text_content() for val in elts]
        else:
            return None


class PWS_Detail:
    def __init__(self):
        self.buyertable = None
        self.purchasetable = None
        self.flowratetable = None
        self.sourcetable = None
        self.measurestable = None
        # initialize the dictionaries
        self.pwsDict = {'Sys Num': '', 'Sys Name': '', 'Sys Type': '', 'Primary Source Type': '', 'Population': '',
                        'Contact': '', 'Business Phone': '', 'Mobile Phone': '', 'Max Daily Demand': '',
                        'Provided Prod. Capacity': '', 'Provided Service Pump Capacity': '', 'Avg. Daily Usage': '',
                        'Total Storage Cap.': '', 'Total Pressure Tank Cap.': '', 'Elevated Storage Cap.': ''}
        self.buyerDict = {'Sys Name': '', 'Sys Num': '', 'Buyer': '', 'Buyer Pop': '', 'Buyer Status': ''}
        self.purchaseDict = {'Sys Name': '', 'Sys Num': '', 'Purchase Info': ''}
        self.sourceDict = {'Sys Name': '', 'Sys Num': '', 'Source Name': '', 'Type': '',
                           'Activity': '', 'Availability': ''}
        self.df = pd.DataFrame()
        self.df_buyer = pd.DataFrame()
        self.df_purchase = pd.DataFrame()
        self.df_source = pd.DataFrame()
        self.df_well = pd.DataFrame()

    def get_basic_detail(self):
        return self.df

    def get_sources(self):
        return self.df_source

    def get_buyers(self):
        return self.df_buyer

    def get_purchases(self):
        return self.df_purchase

    def get_wells(self):
        return self.df_well

    def get_detail(self, url_detail, url_summary, buyers=True, purchases=True):
        headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.103 Safari/537.36'}
        r = requests.get(url=url_detail, headers=headers)
        doc = lxml.html.fromstring(r.content)
        tables = doc.findall('.//table')

        # sys. no., name, pop in 4th table
        systable = tables[3]
        rows = systable.findall('.//tr')
        sysinfo = self._unpack(rows[1])
        sysinfo = ["".join(x.split()) for x in sysinfo]
        self.pwsDict['Sys Num'] = sysinfo[1].strip()
        self.pwsDict['Sys Type'] = sysinfo[3].strip()

        # name is in the 3rd tr
        sysinfo = self._unpack(rows[2])
        sysinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in sysinfo]
        self.pwsDict['Sys Name'] = sysinfo[1].strip()
        self.pwsDict['Primary Source Type'] = sysinfo[3].strip()

        # pop is in the 6th tr
        sysinfo = self._unpack(rows[5])
        sysinfo = ["".join(x.split()) for x in sysinfo]
        self.pwsDict['Population'] = sysinfo[1].strip()

        # contact in the 5th table
        systable = tables[4]
        rows = systable.findall('.//tr')
        if len(rows) >= 3:
            sysinfo = self._unpack(rows[2])
            sysinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in sysinfo]
            self.pwsDict['Contact'] = sysinfo[1].strip()
            if len(sysinfo) >= 5:
                self.pwsDict['Business Phone'] = sysinfo[4].strip()
            if len(sysinfo) >= 7:
                self.pwsDict['Mobile Phone'] = sysinfo[6].strip()

        # the number of buyers and sellers dictate how many tables there are, so certain tables cannot always be
        #     found in the same location. have to look at the th values to find them.
        for table in tables:
            rows = table.findall('.//tr')
            # if rows has list elements, its boolean is True; if an empty list, False
            if rows:
                header = self._unpack(rows[0], kind='th')
                if header is not None:
                    if header[0] == 'Buyers of Water':
                        self.buyertable = table
                    elif header[0] == 'Water Purchases':
                        self.purchasetable = table
                    elif header[0] == 'Sources of Water':
                        self.sourcetable = table
                    elif header[0] == 'WS Flow Rates':
                        self.flowratetable = table
                    elif header[0] == 'WS Measures':
                        self.measurestable = table
        # WS Flow Rates table
        if self.flowratetable is not None:
            rows = self.flowratetable.findall('.//tr')
            if len(rows) >= 3:
                flowinfo = self._unpack(rows[2])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Max Daily Demand'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'

            if len(rows) >= 4:
                flowinfo = self._unpack(rows[3])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Provided Prod. Capacity'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'

            if len(rows) >= 5:
                flowinfo = self._unpack(rows[4])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Provided Service Pump Capacity'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'

            if len(rows) >= 6:
                flowinfo = self._unpack(rows[5])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Avg. Daily Usage'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'
        # WS Measures table
        if self.measurestable is not None:
            rows = self.measurestable.findall('.//tr')
            if len(rows) >= 3:
                flowinfo = self._unpack(rows[2])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Total Storage Cap.'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'

            if len(rows) >= 4:
                flowinfo = self._unpack(rows[3])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Total Pressure Tank Cap.'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'

            if len(rows) >= 5:
                flowinfo = self._unpack(rows[4])
                flowinfo = [re.sub(r'(\s+|&nbsp)', ' ', val) for val in flowinfo]
                self.pwsDict['Elevated Storage Cap.'] = flowinfo[1].strip() + ' (' + flowinfo[2].strip() + ')'

        # add dictionary to dataframe
        self.df = self.df.append(self.pwsDict, ignore_index=True)

        # put columns in correct order
        self.df = self.df[['Sys Num', 'Sys Name', 'Sys Type', 'Primary Source Type', 'Population',
                           'Contact', 'Business Phone', 'Mobile Phone', 'Max Daily Demand', 'Provided Prod. Capacity',
                           'Provided Service Pump Capacity', 'Avg. Daily Usage', 'Total Storage Cap.',
                           'Total Pressure Tank Cap.', 'Elevated Storage Cap.']]

        ###################
        # get the sources #
        ###################
        self.sourceDict['Sys Name'] = self.pwsDict['Sys Name']
        self.sourceDict['Sys Num'] = self.pwsDict['Sys Num']
        if self.sourcetable is not None:
            rows = self.sourcetable.findall('.//tr')
            # get sources as a list of lists
            if len(rows) >= 3:
                sources = [self._unpack(row) for row in rows[2:]]
                for xlr, row in enumerate(sources):
                    for xlc, val in enumerate(row):
                        if xlc == 0:
                            self.sourceDict['Source Name'] = val.strip()
                        if xlc == 1:
                            self.sourceDict['Type'] = val.strip()
                        if xlc == 2:
                            self.sourceDict['Activity'] = val.strip()
                        if xlc == 3:
                            self.sourceDict['Availability'] = val.strip()
                    self.df_source = self.df_source.append(self.sourceDict, ignore_index=True)
            else:
                # there are no sources
                self.sourceDict['Source Name'] = 'NO SOURCES LISTED'
                self.df_source = self.df_source.append(self.sourceDict, ignore_index=True)
        else:
            self.sourceDict['Source Name'] = 'SOURCE TABLE NOT FOUND'
            self.df_source = self.df_source.append(self.sourceDict, ignore_index=True)
        self.df_source = self.df_source[['Sys Name', 'Sys Num', 'Source Name', 'Type', 'Activity', 'Availability']]

        ###################
        # get the buyers  #
        ###################
        try:
            self.buyerDict['Sys Name'] = self.pwsDict['Sys Name']
            self.buyerDict['Sys Num'] = self.pwsDict['Sys Num']
            if self.buyertable is not None and buyers:
                rows = self.buyertable.findall('.//tr')
                if rows and len(rows) >= 3:
                    thebuyers = [self._unpack(row) for row in rows[2:]]
                    # buyers contains who is buying, their population, and their status...separated by '/'
                    #     remove the whitespace
                    if thebuyers:
                        thebuyers = [re.sub(r'(\s+|&nbsp)', ' ', val) for vals in thebuyers for val in vals]
                        # split in '/', creating a list of lists
                        buyers_split = [x.split('/') for x in thebuyers]
                        if buyers_split:
                            for xlr, row in enumerate(buyers_split):
                                if row:
                                    for xlc, val in enumerate(row):
                                        if xlc == 0:
                                            self.buyerDict['Buyer'] = val.strip()
                                        if xlc == 1:
                                            self.buyerDict['Buyer Pop'] = val.strip()
                                        if xlc == 2:
                                            self.buyerDict['Buyer Status'] = val.strip()
                                    self.df_buyer = self.df_buyer.append(self.buyerDict, ignore_index=True)
                                    if xlr > 25000:
                                        self.buyerDict['Buyer'] = 'BUYER DATA TRUNCATED DUE TO LENGTH. ' \
                                                                  'SEE TCEQ FOR MORE INFO.'
                                        self.buyerDict['Buyer Pop'] = ''
                                        self.buyerDict['Buyer Status'] = ''
                                        self.df_buyer = self.df_buyer.append(self.buyerDict, ignore_index=True)
                                        break
            else:
                self.buyerDict['Buyer'] = 'BUYER TABLE NOT FOUND'
                self.df_buyer = self.df_buyer.append(self.buyerDict, ignore_index=True)
        except Exception as e:
            msgbox.show_error('Python Error', str(e))
            self.buyerDict['Buyer'] = 'PROBLEM READING BUYER TABLE IN HTML.'
            self.df_buyer = self.df_buyer.append(self.buyerDict, ignore_index=True)

        self.df_buyer = self.df_buyer[['Sys Name', 'Sys Num', 'Buyer', 'Buyer Pop', 'Buyer Status']]
        self.df_buyer = self.df_buyer.drop_duplicates()

        ######################
        # get the purchases  #
        ######################
        try:
            self.purchaseDict['Sys Name'] = self.pwsDict['Sys Name']
            self.purchaseDict['Sys Num'] = self.pwsDict['Sys Num']
            if self.purchasetable is not None and purchases:
                rows = self.purchasetable.findall('.//tr')
                if len(rows) >= 3:
                    purchases = [self._unpack(row) for row in rows[2:]]
                    # remove the whitespace
                    purchases = [re.sub(r'(\s+|&nbsp)', ' ', val) for vals in purchases for val in vals]
                    for xlr, row in enumerate(purchases):
                        self.purchaseDict['Purchase Info'] = row.strip()
                        self.df_purchase = self.df_purchase.append(self.purchaseDict, ignore_index=True)
                        if xlr > 2000:
                            self.purchaseDict[
                                'Purchase Info'] = 'PURCHASE DATA TRUNCATED DUE TO LENGTH: SEE TCEQ FOR MORE INFO'
                            self.df_purchase = self.df_purchase.append(self.purchaseDict, ignore_index=True)
                            break
            else:
                self.purchaseDict['Purchase Info'] = 'PURCHASE TABLE NOT FOUND'
                self.df_purchase = self.df_purchase.append(self.purchaseDict, ignore_index=True)
        except Exception:
            self.purchaseDict['Purchase Info'] = 'PURCHASE TABLE NOT FOUND'
            self.df_purchase = self.df_purchase.append(self.purchaseDict, ignore_index=True)

        self.df_purchase = self.df_purchase[['Sys Name', 'Sys Num', 'Purchase Info']]
        self.df_purchase = self.df_purchase.drop_duplicates()

        ############################################
        # get the well details from summary sheet  #
        ############################################
        try:
            headers = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/51.0.2704.103 Safari/537.36'}
            r = requests.get(url=url_summary, headers=headers)
            doc = lxml.html.fromstring(r.content)
            tables = doc.findall('.//table')
            for table in tables:
                rows = table.findall('.//tr')
                # if rows has list elements, its boolean is True; if an empty list, False
                if rows:
                    stuff = [self._unpack2(row) for row in rows]
                    if stuff and len(stuff) >= 3:
                        if stuff[0] and stuff[0][0] == '(Active Sources)':
                            for i, item in enumerate(stuff):
                                if isinstance(item, list):
                                    if item[0] == 'SourceNumber':
                                        try:
                                            headings = [re.sub(r'(\s+|&nbsp)', ' ', item) for item in stuff[i]]
                                            values = [re.sub(r'(\s+|&nbsp)', ' ', item).replace(' GPM', '')
                                                      for item in stuff[i + 1]]
                                            if 'Depth' not in headings:
                                                headings.append('Depth')
                                                values.append('')
                                            if 'Tested GPM' not in headings:
                                                headings.append('Tested GPM')
                                                values.append('')
                                            if 'Rated GPM' not in headings:
                                                headings.append('Rated GPM')
                                                values.append('')
                                        except IndexError as e:
                                            pass
                                        dict_well = dict(zip(headings, values))
                                        try:
                                            dict_well['Latitude'] = re.sub(r'(\s+|&nbsp)', '', stuff[i + 7][0])
                                            dict_well['Longitude'] = re.sub(r'(\s+|&nbsp)', '', stuff[i + 7][1])
                                        except IndexError as e:
                                            dict_well['Latitude'] = ''
                                            dict_well['Longitude'] = ''
                                        try:
                                            dict_well['Drill Date'] = re.sub(r'(\s+|&nbsp)', '', stuff[i + 5][0])
                                            dict_well['Source Summary'] = re.sub(r'(\s+|&nbsp)*$', '', stuff[i + 5][1])
                                        except IndexError as e:
                                            dict_well['Drill Date'] = '-'
                                            dict_well['Source Summary'] = '-'
                                        dict_well['Sys Name'] = self.pwsDict['Sys Name']
                                        dict_well['Sys Num'] = self.pwsDict['Sys Num']
                                        self.df_well = self.df_well.append(dict_well, ignore_index=True)
            if self.df_well.empty:
                dict_well = {'Sys Name': self.pwsDict['Sys Name'], 'Sys Num': self.pwsDict['Sys Num'],
                             'SourceNumber': 'No Active Sources', 'Source Name (Activity Status)': '-',
                             'OperationalStatus': '-', 'SourceType': '-', 'Depth': '-', 'Tested GPM': '-',
                             'Rated GPM': '-', 'Drill Date': '-', 'Source Summary': '-',
                             'Latitude': '-', 'Longitude': '-'}
                self.df_well = self.df_well.append(dict_well, ignore_index=True)
            self.df_well = self.df_well[['Sys Name', 'Sys Num', 'SourceNumber', 'Source Name (Activity Status)',
                                         'OperationalStatus', 'SourceType', 'Depth', 'Tested GPM', 'Rated GPM',
                                         'Drill Date', 'Source Summary', 'Latitude', 'Longitude']]
            self.df_well = self.df_well.drop_duplicates()
        except Exception as e:
            msgbox.show_error('Error in well summary', e)

    @staticmethod
    def _unpack(row, kind='td'):
        elts = row.findall('.//%s' % kind)
        # if the tag was found, the list has members and its boolean is True
        if elts:
            return [val.text_content() for val in elts]
        else:
            return None

    @staticmethod
    def _unpack2(row, kind='td'):
        elts = row.findall('.//%s' % kind)
        # if the tag was found, the list has members and its boolean is True
        if elts:
            return [val.text_content() for val in elts]
        else:
            return ''
