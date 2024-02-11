import os
import os.path

print("CLEANING UP, PROBABLY BEFORE STARTING A NEW COMMUNITY...")
if (os.path.exists("friends_to_invite.json")):
    os.remove("friends_to_invite.json")
if (os.path.exists("index_invite.json")):
    os.remove("index_invite.json")
if (os.path.exists("total_invitations_invite.json")):
    os.remove("total_invitations_invite.json")
if (os.path.exists("processed_invite.json")):
    os.remove("processed_invite.json")
if (os.path.exists("captcha_invite.jpeg")):
    os.remove("captcha_invite.jpeg")
print("DONE.")