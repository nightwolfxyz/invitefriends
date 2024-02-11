import os
import os.path

print("CLEANING UP, PROBABLY BEFORE STARTING A NEW COMMUNITY...")
if (os.path.exists("processed_friends.json")):
    os.remove("processed_friends.json")
if (os.path.exists("total_invitations_friends.json")):
    os.remove("total_invitations_friends.json")
if (os.path.exists("captcha_friends.jpeg")):
    os.remove("captcha_friends.jpeg")
print("DONE.")