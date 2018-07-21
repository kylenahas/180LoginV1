import sys
import pprint
import hashlib

from datetime import datetime, date, time, timedelta
from tinydb import TinyDB, Query
from tinydb.operations import decrement

membersDB = TinyDB("members.json")
logDB = TinyDB("log.json")

# Dates stored as ISO 8601?



first_name = "Jessica"
last_name = "Johnson"

birthdate = date(1994, 6, 5)

join_date = datetime.now()
exp_date = timedelta(days=30)
exp_date += join_date

member_ID_str = first_name + last_name      # TODO: Add join datetime to member ID pre hash
member_ID = int(hashlib.sha256(member_ID_str.encode('utf-8')).hexdigest(), 16) % 10 ** 16  # Generate a 16 digit ID number :: https://stackoverflow.com/a/42089311


# TODO: Check uniqueness of new ID, wait 1 second, update join_date and retry. Repeat until a unique ID is assigned.


member_type_str = "punchcard"

entry = {"name_first": first_name, "name_last": last_name, "id": member_ID, "dob": str(birthdate), "join_date": str(join_date),
         "member_type": member_type_str, "expiration_date": str(exp_date), "expiration_punches": 10}

# entry["expiration_punches"] -= 1


print(entry)

# membersDB.insert(entry)

# print(sys.version_info)

# print(membersDB.all())
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(membersDB.all())

print()
print("=====================")
print("=========LOG:========")
print("=====================")



current_M_ID = member_ID

logged_time = datetime.now()

member_query = Query()
member_data = membersDB.get(member_query.id == current_M_ID)
# print(member_data["name_last"] + ", " + member_data["name_first"])

membersDB.update(decrement('expiration_punches'), member_query.id == current_M_ID)

log_entry = {"id": current_M_ID, "name_first": member_data["name_first"], "name_last": member_data["name_last"],
             "log_time": str(logged_time), "remaining_punches": member_data["expiration_punches"]}

logDB.insert(log_entry)





pp.pprint(logDB.all())
# pp.pprint(log_entry)

print(logDB.count(member_query.id == current_M_ID))


