"""
Current Limitations:
    - A member cannot transition from a monthly to a punchcard without losing the remainder of their time


"""



import sys
import pprint
import hashlib

from datetime import datetime, date, time, timedelta
import time
from tinydb import *
from tinydb.operations import decrement
import re


def init():
    global appDB
    appDB = LoginDatabase()
    

class LoginDatabase:
    membersDB = TinyDB("members.json")
    logDB = TinyDB("log.json")

    def add_member(self, first_name, last_name, email, phone, birthdate, member_type_str, link=None):
        join_date = datetime.now()


        member_ID_str = first_name + last_name + str(join_date)
        member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(),
                        16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311

        while self.membersDB.contains(Query().id == member_ID) or len(str(member_ID)) < 16:    # Check for member_id uniqueness
            time.sleep(0.1)
            join_date = datetime.now()
            member_ID_str = first_name + last_name + str(join_date)
            member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(),
                            16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311

        exp_date = "-1"
        exp_punches = 0

        if member_type_str == "monthly" or member_type_str == "student":
            exp_date = str(timedelta(days=31) + join_date)
        elif member_type_str == "annual" or member_type_str == "student_annual":
            exp_date = str(timedelta(days=365) + join_date)
        elif member_type_str == "trial":
            exp_date = str(timedelta(days=7) + join_date)
        elif member_type_str == "punchcard":
            exp_punches = 10



        entry = {"name_first": first_name,
                 "name_last": last_name,
                 "id": member_ID,
                 "dob": str(birthdate),
                 "email" : email,
                 "phone": phone,
                 "join_date": str(join_date),
                 "member_type": member_type_str,
                 "expiration_date": exp_date,
                 "expiration_punches": exp_punches,
                 "link": link}

        self.membersDB.insert(entry)

        return entry


    def retrieve_member(self, member_id):
        member_query = Query()
        if self.membersDB.contains(member_query.id == member_id):
            member_data = self.membersDB.get(member_query.id == member_id)
            return member_data
        else:
            raise ValueError("The entered user ID could not be found in the database")

    def update_member(self, member_id, first_name, last_name, email, phone, birthdate, member_type_str,
                      expiration_punches=-1, expiration_date="-1", link=None):

        # TODO: Implement update. Currently just adds new member

        member_query = Query()

        if self.membersDB.contains(member_query.id == member_id):


            member_data = self.membersDB.get(member_query.id == member_id)
            member_data["name_first"] = first_name
            member_data["name_last"] = last_name
            member_data["dob"] = str(birthdate)
            member_data["email"] = email
            member_data["phone"] = phone
            member_data["member_type"] = member_type_str
            member_data["expiration_date"] = expiration_date
            member_data["expiration_punches"] = int(expiration_punches)
            member_data["link"] = link


            self.membersDB.update(member_data, member_query.id == member_id)
            return member_data
        else:
            raise ValueError("The entered user ID could not be found in the database")


    def log_member(self, member_id):
        logged_time = datetime.now()

        member_query = Query()
        # db.contains(User.name == 'John')
        if self.membersDB.contains(member_query.id == member_id):
            today = date.today()
            visited_today = self.logDB.search((member_query.id == member_id) &
                                              (member_query.log_time.matches(re.compile(str(today), re.IGNORECASE))))

            if visited_today:
                raise LookupError("Member has already logged in today!")

            else:
                member_data = self.membersDB.get(member_query.id == member_id)
                # print(member_data["name_last"] + ", " + member_data["name_first"])
                member_type_str = member_data["member_type"]

                remaining_time="-1"

                if member_type_str == "punchcard":
                    if member_data["expiration_punches"] <= 0:
                        raise RuntimeError("The member has used all of their punches!")
                    self.membersDB.update(decrement('expiration_punches'), member_query.id == member_id)



                log_entry = {"id": member_id, "name_first": member_data["name_first"], "name_last": member_data["name_last"],
                             "log_time": str(logged_time), "member_type_str": member_type_str,
                             "remaining_punches": member_data["expiration_punches"] - 1,
                             "expiration_date": member_data["expiration_date"],
                             "link": member_data.get("link", None)}

                self.logDB.insert(log_entry)

                return log_entry
        else:
            raise LookupError("The entered user ID could not be found in the database")

    def query_member(self, name_first="-1", log_date=None):
        member = Query()

        if name_first != "-1":
            results = self.membersDB.search(member.name_first.matches(re.compile(name_first, re.IGNORECASE)))

            if not results:
                raise ValueError("The entered first name could not be found in the database!")

            return results
        elif log_date:
            today = date.today()
            members_today = self.logDB.search(member.log_time.matches(re.compile(str(today), re.IGNORECASE)))
            results = []
            if not members_today:
                raise ValueError("No members logged in today")
            for memb in members_today:
                member_id = memb["id"]
                results.append(self.membersDB.get(member.id == member_id))
            return results



