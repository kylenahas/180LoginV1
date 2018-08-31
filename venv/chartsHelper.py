from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go

from tinydb import *
from tinydb.operations import decrement
import re

from datetime import datetime

init_notebook_mode(connected=True)

# logfile = "log.json"
logfile = "/Users/kylenahas/Desktop/180login/log.json"

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
    def __init__(self):
        self.logDB = TinyDB(logfile)
        # self.get_entries_of_member_type()


    def get_entries_of_member_type(self):
        member_query = Query()
        print(self.logDB.all())
        
    def calculate_attendence(self, start_date=None, period=None):
        self.attendence = {  "punchcard": [0, 0, 0, 0, 0, 0, 0, 0],
                        "monthly": [0, 0, 0, 0, 0, 0, 0, 0],
                        "annual": [0, 0, 0, 0, 0, 0, 0, 0],
                        "student": [0, 0, 0, 0, 0, 0, 0, 0] }
        for entry in self.logDB:
            dt = datetime.strptime(entry['log_time'], '%Y-%m-%d %H:%M:%S.%f')
            wd = dt.weekday()
            member_type_str = "punchcard"
            try:
                member_type_str = entry['member_type_str']
            except:
                pass
            self.attendence[member_type_str][wd] += 1
        return self.attendence
    def create_attendence_chart(self):
        trace0 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendence['punchcard'],
            name="Punchcard Members"
        )
        trace1 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendence['monthly'],
            name="Monthly Members"
        )
        trace2 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendence['annual'],
            name="Annual Members"
        )
        trace3 = go.Bar(
            x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            y=self.attendence['student'],
            name="Student Members"
        )

        data = [trace0, trace1, trace2, trace3]
        layout = go.Layout(
            barmode='stack'
        )

        fig = go.Figure(data=data, layout=layout)
        return fig


ch = chartsHelper()
ch.calculate_attendence()
print(ch.create_attendence_chart())