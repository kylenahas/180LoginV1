"""
Current Limitations:
    - A member cannot transition from a monthly to a punchcard without losing the remainder of their time


"""



import sys
import pprint
import hashlib

from datetime import datetime, date, time, timedelta
from tinydb import TinyDB, Query
from tinydb.operations import decrement


class LoginDatabase:
    membersDB = TinyDB("members.json")
    logDB = TinyDB("log.json")

    def add_member(self, first_name, last_name, email, phone, birthdate, member_type_str):
        join_date = datetime.now()
        exp_date = "-1"
        exp_punches = 0

        if member_type_str == "monthly":
            exp_date = str(timedelta(days=30) + join_date)
        elif member_type_str == "annual":
            exp_date = str(timedelta(years=1) + join_date)
        elif member_type_str == "student":
            exp_date = str(timedelta(days=30) + join_date)
        else:
            exp_punches = 10

        member_ID_str = first_name + last_name  # TODO: Add join datetime to member ID pre hash
        member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(),
                        16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311


        # TODO: Check uniqueness of new ID, wait 1 second, update join_date and retry. Repeat until a unique ID is assigned.

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



# join_date = datetime.now()
# exp_date = timedelta(days=30)
# exp_date += join_date
#
# member_ID_str = first_name + last_name      # TODO: Add join datetime to member ID pre hash
# member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(), 16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311
#





#
# entry = {"name_first": first_name, "name_last": last_name, "id": member_ID, "dob": str(birthdate), "join_date": str(join_date),
#          "member_type": member_type_str, "expiration_date": str(exp_date), "expiration_punches": 10}

# entry["expiration_punches"] -= 1


# print(entry)

# membersDB.insert(entry)

# print(sys.version_info)

# print(membersDB.all())

# ld = LoginDatabase()


first_name_a = "Jessica"
last_name_a = "Johnson"

email_a = "email@example.com"

phone_a = "(707) 123-4567"

birthdate_a = date(1994, 6, 5)

member_type_str_a = "punchcard"


# ld.add_member(first_name_a, last_name_a, email_a, phone_a, birthdate_a, member_type_str_a)


# pp = pprint.PrettyPrinter(indent=4)
#
# pp.pprint(ld.membersDB.all())

# print()
# print("=====================")
# print("=========LOG:========")
# print("=====================")



# current_M_ID = ld.membersDB.member_ID

# ld.log_member(LoginDatabase, current_M_ID)

# logged_time = datetime.now()
#
# member_query = Query()
# member_data = membersDB.get(member_query.id == current_M_ID)
# # print(member_data["name_last"] + ", " + member_data["name_first"])
#
# membersDB.update(decrement('expiration_punches'), member_query.id == current_M_ID)
#
# log_entry = {"id": current_M_ID, "name_first": member_data["name_first"], "name_last": member_data["name_last"],
#              "log_time": str(logged_time), "remaining_punches": member_data["expiration_punches"]}
#
# logDB.insert(log_entry)



# pp.pprint(ld.log_member(3229308233395595))
#
# pp.pprint(ld.logDB.all())


# print(logDB.count(member_query.id == current_M_ID))


