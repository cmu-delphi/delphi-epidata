"""
===============
=== Purpose ===
===============

A Python utility class to download and parse Quidel data, which is called
by quidel_update.py


=================
=== Changelog ===
=================
2017-12-14:
    * fix epiweek shift bug
    * add end date, end week check
2017-12-02:
    * original version
"""

# standard library
from collections import defaultdict
import email
import imaplib
import os
from os import listdir
from os.path import isfile, join
import re

# third party
import numpy as np
import pandas as pd

# first party
import delphi.operations.secrets as secrets
import delphi.utils.epidate as ED
from delphi.utils.geo.locations import Locations


def word_map(row, terms):
    for (k, v) in terms.items():
        row = row.replace(k, v)
    return row


def date_less_than(d1, d2):
    y1, m1, d1 = [int(x) for x in d1.split("-")]
    y2, m2, d2 = [int(x) for x in d2.split("-")]

    if y1 * 10000 + m1 * 100 + d1 < y2 * 10000 + m2 * 100 + d2:
        return 1
    elif y1 * 10000 + m1 * 100 + d1 == y2 * 10000 + m2 * 100 + d2:
        return 0
    else:
        return -1


# shift>0: shifted to future
def date_to_epiweek(date, shift=0):
    y, m, d = [int(x) for x in date.split("-")]

    epidate = ED.EpiDate(y, m, d)
    epidate = epidate.add_days(shift)
    ew = epidate.get_ew()
    return ew


# convert measurment to time series format
# startweek and endweek are inclusive
def measurement_to_ts(m, index, startweek=None, endweek=None):
    if startweek is None:
        startweek = 0
    if endweek is None:
        endweek = 999999
    res = {}
    for r, rdict in m.items():
        res[r] = {}
        for t, vals in rdict.items():
            if index >= len(vals):
                raise Exception("Index is invalid")
            if t >= startweek and t <= endweek:
                res[r][t] = vals[index]
    return res


class QuidelData:
    def __init__(self, raw_path, load_email=True):
        self.data_path = raw_path
        self.excel_uptodate_path = join(raw_path, "excel/uptodate")
        self.excel_history_path = join(raw_path, "excel/history")
        self.csv_path = join(raw_path, "csv")
        self.xlsx_uptodate_list = [f[:-5] for f in listdir(self.excel_uptodate_path) if isfile(join(self.excel_uptodate_path, f)) and f[-5:] == ".xlsx"]
        self.xlsx_history_list = [f[:-5] for f in listdir(self.excel_history_path) if isfile(join(self.excel_history_path, f)) and f[-5:] == ".xlsx"]
        self.csv_list = [f[:-4] for f in listdir(self.csv_path) if isfile(join(self.csv_path, f)) and f[-4:] == ".csv"]
        self.map_terms = {
            ' FL  34637"': "FL",
        }
        # hardcoded parameters
        self.date_dim = 1
        self.state_dim = 4
        self.fields = ["sofia_ser", "date", "fac_id", "city", "state", "zip", "age", "fluA", "fluB", "fluAll", "county", "fac_type"]
        self.fields_to_keep = ["fac_id", "fluA", "fluB", "fluAll"]
        self.dims_to_keep = [self.fields.index(x) for x in self.fields_to_keep]
        if load_email:
            self.retrieve_excels()
        self.prepare_csv()

    def retrieve_excels(self):
        detach_dir = self.excel_uptodate_path  # directory where to save attachments (default: current)

        # connecting to the gmail imap server
        m = imaplib.IMAP4_SSL("imap.gmail.com")
        m.login(secrets.quidel.email_addr, secrets.quidel.email_pwd)
        m.select("INBOX")  # here you a can choose a mail box like INBOX instead
        # use m.list() to get all the mailboxes
        _, items = m.search(None, "ALL")  # you could filter using the IMAP rules here (check https://www.example-code.com/csharp/imap-search-critera.asp)
        items = items[0].split()  # getting the mails id

        # The emailids are ordered from past to now
        for emailid in items:
            _, data = m.fetch(emailid, "(RFC822)")  # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1].decode("utf-8")  # getting the mail content
            mail = email.message_from_string(email_body)  # parsing the mail content to get a mail object

            # Check if any attachments at all
            if mail.get_content_maintype() != "multipart":
                continue

            # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
            for part in mail.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == "multipart":
                    continue

                # is this part an attachment ?
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()
                # check duplicates
                if filename[-5:] != ".xlsx" or filename[:-5] in self.xlsx_uptodate_list + self.xlsx_history_list:
                    continue

                self.xlsx_uptodate_list.append(filename[:-5])
                att_path = os.path.join(detach_dir, filename)

                # Check if its already there
                if not os.path.isfile(att_path):
                    # finally write the stuff
                    fp = open(att_path, "wb")
                    fp.write(part.get_payload(decode=True))
                    fp.close()

    def prepare_csv(self):
        need_update = False
        for f in self.xlsx_uptodate_list:
            if f in self.csv_list:
                continue
            else:
                need_update = True

            date_regex = "\d{2}-\d{2}-\d{4}"
            date_items = re.findall(date_regex, f)
            if date_items:
                end_date = "-".join(date_items[-1].split("-")[x] for x in [2, 0, 1])
            else:
                print("End date not found in file name:" + f)
                end_date = None

            df_dict = pd.read_excel(join(self.excel_uptodate_path, f + ".xlsx"), sheet_name=None)
            for (_, df) in df_dict.items():
                df = df.dropna(axis=0, how="all")
                df["TestDate"] = df["TestDate"].apply(lambda x: x.strftime("%Y-%m-%d"))
                df_filtered = df[df["TestDate"] != ""]
                if end_date is not None:
                    df_filtered = df_filtered[df.apply(lambda x: date_less_than(end_date, x["TestDate"]) != 1, axis=1)]
                df_filtered.to_csv(join(self.csv_path, f + ".csv"), index=False, encoding="utf-8")
        self.csv_list = [f[:-4] for f in listdir(self.csv_path) if isfile(join(self.csv_path, f)) and f[-4:] == ".csv"]
        self.need_update = need_update

    def load_csv(self, dims=None):
        if dims is None:
            dims = self.dims_to_keep
        parsed_dict = defaultdict(dict)
        for f in self.csv_list:
            if f in self.xlsx_history_list:
                continue
            rf = open(join(self.csv_path, f + ".csv"))

            lines = rf.readlines()
            for l in lines[1:]:
                l = word_map(l, self.map_terms)
                row = l.strip().split(",")
                date = row[self.date_dim]
                state = row[self.state_dim]
                if state not in parsed_dict[date]:
                    parsed_dict[date][state] = []
                parsed_dict[date][state].append([row[x] for x in dims])

        return parsed_dict

    # hardcoded aggregation function
    # output: [#unique_device,fluA,fluB,fluAll,total]
    def prepare_measurements(self, data_dict, use_hhs=True, start_weekday=6):
        buffer_dict = {}
        if use_hhs:
            region_list = Locations.hhs_list
        else:
            region_list = Locations.atom_list

        def get_hhs_region(atom):
            for region in Locations.hhs_list:
                if atom.lower() in Locations.hhs_map[region]:
                    return region
            if atom.lower() == "ny":
                return "hhs2"
            return atom

        day_shift = 6 - start_weekday
        time_map = lambda x: date_to_epiweek(x, shift=day_shift)
        region_map = lambda x: get_hhs_region(x) if use_hhs and x not in Locations.hhs_list else x  # a bit hacky

        end_date = sorted(data_dict.keys())[-1]
        # count the latest week in only if Thurs data is included
        end_epiweek = date_to_epiweek(end_date, shift=-4)
        # first pass: prepare device_id set
        device_dict = {}
        for (date, daily_dict) in data_dict.items():
            if not date:
                continue
            ew = time_map(date)
            if ew == -1 or ew > end_epiweek:
                continue
            if ew not in device_dict:
                device_dict[ew] = {}
                for r in region_list:
                    device_dict[ew][r] = set()
            for (state, rec_list) in daily_dict.items():
                region = region_map(state)
                # get rid of non-US regions
                if region not in region_list:
                    continue
                for rec in rec_list:
                    fac = rec[0]
                    device_dict[ew][region].add(fac)

        # second pass: prepare all measurements
        for (date, daily_dict) in data_dict.items():
            ew = time_map(date)
            if ew == -1 or ew > end_epiweek:
                continue
            if ew not in buffer_dict:
                buffer_dict[ew] = {}
                for r in region_list:
                    buffer_dict[ew][r] = [0.0] * 8

            for (state, rec_list) in daily_dict.items():
                region = region_map(state)
                # get rid of non-US regions
                if region not in region_list:
                    continue
                for rec in rec_list:
                    fac_num = float(len(device_dict[ew][region]))
                    buffer_dict[ew][region] = np.add(
                        buffer_dict[ew][region],
                        [
                            rec[1] == "positive",
                            rec[2] == "positive",
                            rec[3] == "positive",
                            1.0,
                            float(rec[1] == "positive") / fac_num,
                            float(rec[2] == "positive") / fac_num,
                            float(rec[3] == "positive") / fac_num,
                            1.0 / fac_num,
                        ],
                    ).tolist()
        # switch two dims of dict
        result_dict = {}
        for r in region_list:
            result_dict[r] = {}
            for (k, v) in buffer_dict.items():
                result_dict[r][k] = v[r]

        return result_dict
