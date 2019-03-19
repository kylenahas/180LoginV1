from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import numpy, pandas

from tinydb import *
from tinydb.operations import decrement
import re

from datetime import datetime

import config

# init_notebook_mode(connected=True)

# logfile = "log.json"
try:
    logfile = "/Users/kylenahas/Desktop/180LoginV1/db/log.json"
except:
    logfile = "./log.json"


def simple_chart():
    trace0 = go.Bar(
        x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        y=[3, 1, 6, 3, 2, 5],
        name="Punchcard Members"
    )
    trace1 = go.Bar(
        x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        y=[2, 3, 4, 1, 5, 1],
        name="Monthly Members"
    )

    data = [trace0, trace1]
    layout = go.Layout(
        barmode='stack'
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


class chartsHelper:
    def __init__(self, log=None):
        if not log:
            self.log = logfile
        try:
            self.log = log
            self.logDB = TinyDB(self.log)
        except FileNotFoundError as e:
            print("Invalid logfile")
        # self.get_entries_of_member_type()


    def get_entries_of_member_type(self):
        member_query = Query()
        print(self.logDB.all())
        
    def calculate_attendence(self, start_date=None, period=None):
        # zeros = numpy.zeros((7,), dtype=int)
        # self.attendance = {}
        # # self.attendance = {k:numpy.zeros((7,), dtype=int) for k in config.member_types.keys()}  # https://stackoverflow.com/a/483833
        # for member_type_k in config.member_types.keys():
        #     # print(member_type_k)
        #     self.attendance.update({member_type_k: zeros})
        self.attendance = {  "punchcard": [0, 0, 0, 0, 0, 0, 0, 0],
                        "monthly": [0, 0, 0, 0, 0, 0, 0, 0],
                        "annual": [0, 0, 0, 0, 0, 0, 0, 0],
                        "student": [0, 0, 0, 0, 0, 0, 0, 0],
                        "student_annual": [0, 0, 0, 0, 0, 0, 0, 0],
                        "volunteer": [0, 0, 0, 0, 0, 0, 0, 0],
                        "trial": [0, 0, 0, 0, 0, 0, 0, 0],
                        "organization": [0, 0, 0, 0, 0, 0, 0, 0] }
        for entry in self.logDB:
            # print(entry)
            dt = datetime.strptime(entry['log_time'], '%Y-%m-%d %H:%M:%S.%f')
            wd = dt.weekday()
            member_type_str = "punchcard"
            try:
                member_type_str = entry['member_type_str']
            except:
                pass
            self.attendance[member_type_str][wd] += 1
        return self.attendance
    def create_attendence_chart(self):
        trace0 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendance['punchcard'],
            name="Punchcard Members"
        )
        trace1 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendance['monthly'],
            name="Monthly Members"
        )
        trace2 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendance['annual'],
            name="Annual Members"
        )
        trace3 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendance['student'],
            name="Student Members"
        )
        trace4 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendance['volunteer'],
            name="Volunteer Members"
        )
        trace5 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendance['organization'],
            name="Organization Members"
        )

        data = [trace0, trace1, trace2, trace3, trace4, trace5]
        layout = go.Layout(
            barmode='stack'
        )

        fig = go.Figure(data=data, layout=layout)
        return fig

    def panda_tests(self):
        # print(self.logDB.all())
        pandas.set_option('display.max_colwidth', -1)
        pandas.set_option('display.max_columns', None)
        df = pandas.DataFrame(self.logDB.all())
        # for entry in self.logDB:
        #     df.append(entry, ignore_index=True)
        # pd = pandas.read_json(self.logDB.all(), orient='index')
        df['log_time'] = pandas.to_datetime(df['log_time'])

        df['weekday'] = df['log_time'].apply(lambda x: x.isoweekday())

        df.set_index("log_time", inplace=True)

        print(df.columns)
        print(df.head(10))

        print(df.groupby("id").count())


if __name__ == '__main__':
    ch = chartsHelper(log="/Users/kylenahas/Desktop/180LoginV1/db/log-mar19.json")
    # ch.calculate_attendence()
    # plot(ch.create_attendence_chart())
    ch.panda_tests()