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


class LoginDatabase:
    membersDB = TinyDB("members.json")
    logDB = TinyDB("log.json")

    def add_member(self, first_name, last_name, email, phone, birthdate, member_type_str):
        join_date = datetime.now()
        exp_date = "-1"
        exp_punches = 0

        member_ID_str = first_name + last_name + str(join_date)
        member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(),
                        16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311

        while self.membersDB.contains(Query().id == member_ID) or len(str(member_ID)) < 16:    # Check for member_id uniqueness
            time.sleep(0.1)
            join_date = datetime.now()
            member_ID_str = first_name + last_name + str(join_date)
            member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(),
                            16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311

        if member_type_str == "monthly":
            exp_date = str(timedelta(days=30) + join_date)
        elif member_type_str == "annual":
            exp_date = str(timedelta(days=360) + join_date)
        elif member_type_str == "student":
            exp_date = str(timedelta(days=30) + join_date)
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
                 "expiration_punches": exp_punches}

        self.membersDB.insert(entry)

        return entry


    def retrieve_member(self, member_id):
        member_query = Query()
        if self.membersDB.contains(member_query.id == member_id):
            member_data = self.membersDB.get(member_query.id == member_id)
            return member_data
        else:
            raise ValueError("The entered user ID could not be found in the database")

    def update_member(self, member_id, first_name, last_name, email, phone, birthdate, member_type_str, expiration_punches=-1):

        # TODO: Implement update. Currently just adds new member

        member_query = Query()

        if self.membersDB.contains(member_query.id == member_id):
            exp_date = "-1"

            if member_type_str == "monthly":
                exp_date = str(timedelta(days=30) + datetime.now())
            elif member_type_str == "annual":
                exp_date = str(timedelta(years=1) + datetime.now())
            elif member_type_str == "student":
                exp_date = str(timedelta(days=30) + datetime.now())

            member_data = self.membersDB.get(member_query.id == member_id)
            member_data["name_first"] = first_name
            member_data["name_last"] = last_name
            member_data["dob"] = str(birthdate)
            member_data["email"] = email
            member_data["phone"] = phone
            member_data["member_type"] = member_type_str
            member_data["expiration_date"] = exp_date
            member_data["expiration_punches"] = int(expiration_punches)


            self.membersDB.update(member_data, member_query.id == member_id)
            return member_data
        else:
            raise ValueError("The entered user ID could not be found in the database")


    def log_member(self, member_id):
        logged_time = datetime.now()

        member_query = Query()
        # db.contains(User.name == 'John')
        if self.membersDB.contains(member_query.id == member_id):

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
                         "remaining_punches": member_data["expiration_punches"] - 1}

            self.logDB.insert(log_entry)

            return log_entry
        else:
            raise ValueError("The entered user ID could not be found in the database")

    def query_member(self, name_first):
        member = Query()
        results = self.membersDB.search(member.name_first.matches(re.compile(name_first, re.IGNORECASE)))

        if not results:
            raise ValueError("The entered first name could not be found in the database!")

        return results


