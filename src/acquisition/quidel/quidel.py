'''
===============
=== Purpose ===
===============

A Python utility class to download and parse Quidel date, which is called
by quidel_update.py


=================
=== Changelog ===
=================

2017-12-02:
	* original version
'''

# standard
from os import listdir
from os.path import isfile, join

import email, getpass, imaplib, os
import datetime
import math
from collections import defaultdict

# third party
import pandas as pd
import numpy as np

# delphi
import delphi.utils.epidate as ED
import delphi.utils.epiweek as EW
from delphi.utils.state_info import *
import delphi.operations.secrets as secrets

def word_map(row,terms):
    for (k,v) in terms.items():
        row = row.replace(k,v)
    return row

def dateToEpiweek(date, delimiter='-', shift=0):
    curr_date = datetime.datetime.now().strftime('%Y-%m-%d')
    cy,cm,cd = [int(x) for x in curr_date.split('-')]
    try:
        y,m,d = [int(x) for x in date.split(delimiter)]
    except:
        return -1

    if cy*10000+cm*100+cd<y*10000+m*100+d:
        # mark records from future as invalid
        return -1
    epidate = ED.EpiDate(y,m,d)
    epidate = epidate.add_days(shift)
    ew = epidate.get_ew()
    return ew

# convert measurment to time series format
# startweek and endweek are inclusive
def measurement_to_ts(m,index,startweek=0,endweek=999999):
    res = {}
    for r,rdict in m.items():
        res[r]={}
        for t,vals in rdict.items():
            if index>=len(vals):
                raise Exception("Index is invalid")
            if t>=startweek and t<=endweek:
                res[r][t] = vals[index]
    return res

class QuidelData:
    def __init__(self, raw_path):
        self.data_path = raw_path
        self.excel_path = join(raw_path,'excel')
        self.csv_path = join(raw_path,'csv')
        self.xlsx_list = [f[:-5] for f in listdir(self.excel_path) if isfile(join(self.excel_path, f)) and f[-5:]=='.xlsx']
        self.csv_list = [f[:-4] for f in listdir(self.csv_path) if isfile(join(self.csv_path, f)) and f[-4:]=='.csv']
        self.map_terms = {
            ' FL  34637"':'FL',
        }
        # hardcoded parameters
        self.date_dim = 1
        self.state_dim = 4
        self.fields = [
            'sofia_ser','date','fac_id','city','state','zip','age',
            'fluA','fluB','fluAll','county','fac_type'
        ]
        self.fields_to_keep = ['fac_id','fluA','fluB','fluAll']
        self.dims_to_keep = [self.fields.index(x) for x in self.fields_to_keep]
        self.retrieve_excels()
        self.prepare_csv()

    def retrieve_excels(self):
        detach_dir = self.excel_path # directory where to save attachments (default: current)

        # connecting to the gmail imap server
        m = imaplib.IMAP4_SSL("imap.gmail.com")
        m.login(secrets.quidel.email_addr,secrets.quidel.email_pwd)
        m.select("INBOX") # here you a can choose a mail box like INBOX instead
        # use m.list() to get all the mailboxes
        resp, items = m.search(None, "ALL") # you could filter using the IMAP rules here (check http://www.example-code.com/csharp/imap-search-critera.asp)
        items = items[0].split() # getting the mails id

        # The emailids are ordered from past to now
        for emailid in items:
            resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            mail = email.message_from_string(email_body) # parsing the mail content to get a mail object

            #Check if any attachments at all
            if mail.get_content_maintype() != 'multipart':
                continue

            # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
            for part in mail.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue

                # is this part an attachment ?
                if part.get('Content-Disposition') is None:
                    continue

                filename = part.get_filename()
                # check duplicates
                if filename[-5:]!='.xlsx' or filename[:-5] in self.xlsx_list:
                    continue

                self.xlsx_list.append(filename[:-5])
                att_path = os.path.join(detach_dir, filename)

                #Check if its already there
                if not os.path.isfile(att_path) :
                    # finally write the stuff
                    fp = open(att_path, 'wb')
                    fp.write(part.get_payload(decode=True))
                    fp.close()

    def prepare_csv(self):
        for f in self.xlsx_list:
            if f in self.csv_list:
                continue
            df_dict = pd.read_excel(join(self.excel_path, f+'.xlsx'), sheetname=None)
            for (_,df) in df_dict.items():
                # convert data type for saving
                types = df.apply(lambda x: pd.lib.infer_dtype(x.values))
                # re-format date if needed
                df['TestDate'] = df['TestDate'].apply(lambda x: x if '/' not in str(x) else '-'.join([
                    '0'+d if len(d)==1 else d for d in [str(x).split('/')[i] for i in [2,0,1]]
                ]))
                df.to_csv(join(self.csv_path, f+'.csv'), index=False, encoding='utf-8')
        self.csv_list = [f[:-4] for f in listdir(self.csv_path) if isfile(join(self.csv_path, f)) and f[-4:]=='.csv']

    def load_csv(self, dims=None):
        if dims is None:
            dims = self.dims_to_keep
        parsed_dict = defaultdict(dict)
        for f in self.csv_list:
            rf = open(join(self.csv_path,f+'.csv'))
            lines = rf.readlines()
            for l in lines[1:]:
                l = word_map(l,self.map_terms)
                row = l.strip().split(',')
                date = row[self.date_dim]
                state = row[self.state_dim]
                if state not in parsed_dict[date]:
                    parsed_dict[date][state] = []
                parsed_dict[date][state].append([row[x] for x in dims])
        return parsed_dict

    # hardcoded aggregation function
    # output: [#unique_device,fluA,fluB,fluAll,total]
    def prepare_measurements(self,data_dict,use_epiweek=False,use_hhs=False,start_weekday=6):
        buffer_dict = {}
        SI = StateInfo()
        if use_hhs:
            region_list = SI.hhs
        else:
            region_list = SI.sta

        day_shift = start_weekday - 6
        time_map = lambda x:dateToEpiweek(x,'-',shift=day_shift) if use_epiweek else x
        region_map = lambda x:SI.state_regions[x]['hhs'] \
                    if use_hhs and x in SI.state_regions else x # a bit hacky
        # first pass: prepare device_id set
        device_dict = {}
        for (date,daily_dict) in data_dict.items():
            time = time_map(date)
			if time == -1:
				continue
            if time not in device_dict:
                device_dict[time]={}
                for r in region_list:
                    device_dict[time][r] = Set()
            for (state,rec_list) in daily_dict.items():
                region = region_map(state)
                # get rid of non-US regions
                if region not in region_list:
                    continue
                for rec in rec_list:
                    fac = rec[0]
                    device_dict[time][region].add(fac)

        # second pass: prepare all measurements
        for (date,daily_dict) in data_dict.items():
            time = time_map(date)
			if time == -1:
				continue
            if time not in buffer_dict:
                buffer_dict[time]={}
                for r in region_list:
                    buffer_dict[time][r] = [0.0]*8

            for (state,rec_list) in daily_dict.items():
                region = region_map(state)
                # get rid of non-US regions
                if region not in region_list:
                    continue
                for rec in rec_list:
                    fac_num = float(len(device_dict[time][region]))
                    buffer_dict[time][region]= np.add(
                        buffer_dict[time][region],[
                            rec[1]=='positive',
                            rec[2]=='positive',
                            rec[3]=='positive',
                            1.0,
                            float(rec[1]=='positive')/fac_num,
                            float(rec[2]=='positive')/fac_num,
                            float(rec[3]=='positive')/fac_num,
                            1.0/fac_num,
                    ]).tolist()
        # switch two dims of dict
        result_dict = {}
        for r in region_list:
            result_dict[r]={}
            for (k,v) in buffer_dict.items():
                result_dict[r][k]=v[r]

        return result_dict
