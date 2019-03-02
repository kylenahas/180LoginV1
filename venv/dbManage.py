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

import config


def init():
    global appDB
    appDB = LoginDatabase()
    

class LoginDatabase:
    membersDB = TinyDB("members.json")
    logDB = TinyDB("log.json")

    """ add_member: Adds a new member to the database. All parameters but link are required. 
                    Expiration date is automatically set using the member date and current time. Current time 
                    is recorded. A 16 digit numerical ID is generated and assigned based off the date and member's name
                    and checked against the database. If the ID has been already been used, it waits .1 second and 
                    tries again until an unused ID has been generated. Also protects against IDs that are less than 16
                    digits long, as sometimes they were generated that were too short.
                    
                    Returns: Dictionary of the data entered into the database """

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

    """ retrieve_member: Upon being passed a member ID, checks if the member exists (and not deleted) and then 
                            returns the member's data. Raises LookupError if the member does not exits.
                            
                            Returns: Document type containing data of the selected member in the members database"""

    def retrieve_member(self, member_id):
        member_query = Query()
        if self.membersDB.contains(member_query.id == member_id):
            member_data = self.membersDB.get(member_query.id == member_id)
            if member_data.get("deleted", False):
                raise LookupError("The entered user ID could not be found in the database")
            return member_data
        else:
            raise LookupError("The entered user ID could not be found in the database")

    """ update_member: Updates a member in the database. With the exception of expiration_punches, expiration_date
                            and link, all of the member data must be passed in. Currently does not support passing 
                            in just the parameters you want to update. In the future, might consider using **kwargs
                            as a more flexible update. Raises a LookupError if the associated member cannot be found.

                            Returns: List of documents containing data of the selected member in the members database"""

    def update_member(self, member_id, first_name, last_name, email, phone, birthdate, member_type_str,
                      expiration_punches=-1, expiration_date="-1", link=None):


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
            raise LookupError("The entered user ID could not be found in the database")

    """ log_member: Logs in member by adding their member_id to the log database, along with:
                        * Log Date
                        * First/Last name
                        * Member Type
                        * Expiration Date/Punches Remaining
                        * Link (if Applicable) 
                    If a member is a punchcard member, one punch is removed from their account.
                    If the member has already logged in during the past day (since midnight), and the debug feature 
                    "config.allow_multiple_scans_a_day" is False, a LookupError will be raised, indicating that the
                    member has already logged in today.
    
                    Returns: List type of the log entry """

    def log_member(self, member_id):
        logged_time = datetime.now()

        member_query = Query()
        # db.contains(User.name == 'John')
        if self.membersDB.contains(member_query.id == member_id):
            today = date.today()
            visited_today = self.logDB.search((member_query.id == member_id) &
                                              (member_query.log_time.matches(re.compile(str(today), re.IGNORECASE))))

            if visited_today and not config.allow_multiple_scans_a_day:
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

    """ query_member: Performs a regex search on the database, by member's first name or current day. Ignores members
                        marked as deleted. The parameter "log_date" can be passed True to use the current day, or a 
                        date object to specify a certain day. If no members match the name, or nobody has logged in
                        today, a LookupError is raised.

                        Returns: List of documents containing data of all the members matching the search in the 
                            members database """

    def query_member(self, name_first="-1", log_date=None):
        member = Query()

        if name_first != "-1":
            results = self.membersDB.search((member.name_first.matches(re.compile(name_first, re.IGNORECASE)))
                                            & ~(member.deleted == True))


            if not results:
                raise LookupError("The entered first name could not be found in the database!")

            return results
        elif log_date:
            if log_date == True:
                log_date = date.today()
            members_today = self.logDB.search((member.log_time.matches(re.compile(str(log_date), re.IGNORECASE)))
                                              & ~(member.deleted == True))

            results = []
            if not members_today:
                raise LookupError("No members logged in today")
            for memb in members_today:
                member_id = memb["id"]
                results.append(self.membersDB.get(member.id == member_id))
            return results
        else:
            raise LookupError("Invalid search query.")


    """ get_member_sign_offs: When given a member ID. this function retrieves the member's sign ins from the member 
                                database. If the member does not have any sign offs, generates an empty dict containing
                                the sign-offs listed in config.sign_off_list. The dict should only contain booleans.
                                If the member ID does not exist in the database, a LookupError is raised.

                            Returns: Dictionary containing the skills a member has been signed off on. If the member
                             does not have any recorded sign-offs, generates a dict of all the sign-offs with 
                             the value False """

    def get_member_sign_offs(self, member_id):
        member_query = Query()
        if self.membersDB.contains(member_query.id == member_id):
            member_data = self.membersDB.get(member_query.id == member_id)
            sign_offs = member_data.get("sign_offs", None)

            if not sign_offs:
                sign_offs_dict = {}
                for activity in config.sign_off_list.keys():
                    sign_offs_dict[activity] = False
                sign_offs = sign_offs_dict

            return sign_offs
        else:
            raise LookupError("The entered user ID could not be found in the database")

    """ set_member_sign_offs: Updates the sign-offs for a given member. 

                                Returns: Dictionary containing the skills a member has been signed off on. If the member
                                 does not have any recorded sign-offs, generates a dict of all the sign-offs with 
                                 the value False """

    def set_member_sign_offs(self, member_id, sign_offs):
        member_query = Query()
        if self.membersDB.contains(member_query.id == member_id):
            member_data = self.membersDB.get(member_query.id == member_id)

            if not sign_offs:
                for activity in config.sign_off_list.keys():
                    sign_offs[activity] = False

            member_data["sign_offs"] = sign_offs
            self.membersDB.update(member_data, member_query.id == member_id)

            return sign_offs
        else:
            raise LookupError("The entered user ID could not be found in the database")

    def delete_member(self, member_id, hard_delete=False):
        member_query = Query()
        if self.membersDB.contains(member_query.id == member_id):
            member_data = self.membersDB.get(member_query.id == member_id)
            member_data["deleted"] = True
            self.membersDB.update(member_data, member_query.id == member_id)
        else:
            raise LookupError("The entered user ID could not be found in the database")




