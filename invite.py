import requests
import json
import os
import os.path
import time
import math
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

BASE_URL = "https://api.vk.com/method/"

CONFIG = {}

captcha_encountered = False
captcha_solved = False
captcha_sid = ""
captcha_key = ""
MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA = 100

friends_to_invite = set()
processed = set()
count = 0
total_invitations = 0

def GetFriendsGroupMembers():
    result = set()

    my_filter = "friends"

    offset = 0
    count = 0
    url = BASE_URL + "groups.getMembers?group_id=" + CONFIG["COMMUNITY_ID"] + "&filter=" + my_filter + "&offset=" + str(offset) + "&count=" + str(count) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
    print(url)
    print()

    request = requests.get(url)
    time.sleep(1)
    content = request.content
    print(content)
    print()
    response = json.loads(content)

    if ("response" not in response):
        return result

    number_of_group_members = 0
    number_of_pages = 0

    response_body = response["response"]
    number_of_group_members = response_body["count"]
    number_of_pages = math.ceil(number_of_group_members / CONFIG["PAGE_SIZE"])
    print("Number of group members: " + str(number_of_group_members))
    print("Number of pages: " + str(number_of_pages))
    print()

    for page_index in range(number_of_pages):
        offset = page_index * CONFIG["PAGE_SIZE"]
        count = CONFIG["PAGE_SIZE"]
        url = BASE_URL + "groups.getMembers?group_id=" + CONFIG["COMMUNITY_ID"] + "&filter=" + my_filter + "&offset=" + str(offset) + "&count=" + str(count) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
        print(url)
        print()
        request = requests.get(url)
        time.sleep(1)
        content = request.content
        print(content)
        print()
        response = json.loads(content)
        if ("response" in response):
            response_body = response["response"]
            for item in response_body["items"]:
                result.add(item)

    return result

def GetAllFriends():
    result = set()

    offset = 0
    count = 0
    url = BASE_URL + "friends.get?user_id=" + CONFIG["USER_ID"] + "&offset=" + str(offset) + "&count=" + str(count) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
    print(url)
    print()

    request = requests.get(url)
    time.sleep(1)
    content = request.content
    print(content)
    print()
    response = json.loads(content)
        
    if ("response" not in response):
        return result

    number_of_friends = 0
    number_of_pages = 0

    response_body = response["response"]
    number_of_friends = response_body["count"]
    number_of_pages = math.ceil(number_of_friends / CONFIG["PAGE_SIZE"])
    print("Number of friends: " + str(number_of_friends))
    print("Number of pages: " + str(number_of_pages))

    for page_index in range(number_of_pages):
        offset = page_index * CONFIG["PAGE_SIZE"]
        count = CONFIG["PAGE_SIZE"]
        url = BASE_URL + "friends.get?user_id=" + CONFIG["USER_ID"] + "&offset=" + str(offset) + "&count=" + str(count) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
        print(url)
        print()
        request = requests.get(url)
        time.sleep(1)
        content = request.content
        print(content)
        print()
        response = json.loads(content)
        if ("response" in response):
            response_body = response["response"]
            for item in response_body["items"]:
                result.add(item)

    return result

def GetFriendsToInvite():
    result = []
    friends_group_members = GetFriendsGroupMembers()
    time.sleep(1)
    all_friends = GetAllFriends()
    time.sleep(1)
    for friend in all_friends:
        if friend not in friends_group_members:
            result.append(friend)
    return result

def ReadConfig():
    global CONFIG

    if not os.path.exists("invitefriends.conf"):
        print("ERROR: Configuration file is missing!")
        return -1

    with open("invitefriends.conf", "r") as read_file:
        CONFIG = json.load(read_file)

    if "USER_ID" not in CONFIG:
        print("ERROR: USER_ID setting is missing!")
        return -1

    if "COMMUNITY_ID" not in CONFIG:
        print("ERROR: COMMUNITY_ID setting is missing!")
        return -1

    if "USER_ACCESS_TOKEN" not in CONFIG:
        print("ERROR: USER_ACCESS_TOKEN setting is missing!")
        return -1

    if "ANTI_CAPTCHA_API_KEY" not in CONFIG:
        print("ERROR: ANTI_CAPTCHA_API_KEY setting is missing!")
        return -1

    if "PAGE_SIZE" not in CONFIG:
        print("ERROR: PAGE_SIZE setting is missing!")
        return -1

    if "MAX_INVITES_PER_SESSION" not in CONFIG:
        print("ERROR: MAX_INVITES_PER_SESSION setting is missing!")
        return -1

    if "API_VERSION" not in CONFIG:
        print("ERROR: API_VERSION setting is missing!")
        return -1

    print("Configuration: ")
    print(CONFIG)
    print()
    print("USER_ID: " + CONFIG["USER_ID"])
    print("COMMUNITY_ID: " + CONFIG["COMMUNITY_ID"])
    print("USER_ACCESS_TOKEN: " + CONFIG["USER_ACCESS_TOKEN"])
    print("ANTI_CAPTCHA_API_KEY: " + CONFIG["ANTI_CAPTCHA_API_KEY"])
    print("PAGE_SIZE: " + str(CONFIG["PAGE_SIZE"]))
    print("MAX_INVITES_PER_SESSION: " + str(CONFIG["MAX_INVITES_PER_SESSION"]))
    print("API_VERSION: " + CONFIG["API_VERSION"])
    print()

    return 0

def LoadState():
    global processed
    global total_invitations

    if (os.path.exists("processed_invite.json")):
        with open("processed_invite.json", "r") as read_file:
            processed_list = json.load(read_file)
            for id in processed_list:
                processed.add(id)

    if (os.path.exists("total_invitations_invite.json")):
        with open("total_invitations_invite.json", "r") as read_file:
            total_invitations = json.load(read_file)

    return 0

def SaveState():
    global processed
    global total_invitations

    processed_list = []
    for id in processed:
        processed_list.append(id)
    processed.clear()

    with open("processed_invite.json", "w") as write_file:
        json.dump(processed_list, write_file)

    with open("total_invitations_invite.json", "w") as write_file:
        json.dump(total_invitations, write_file)

    return 0

def main():
    global CONFIG
    global friends_to_invite
    global processed
    global total_invitations
    global count
    global captcha_encountered
    global captcha_solved
    global captcha_sid
    global captcha_key
    global MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA

    result = ReadConfig()
    if result < 0:
        return result

    LoadState()

    all_friends_processed = True
    friends_to_invite = GetFriendsToInvite()
    time.sleep(1)
    print("FRIENDS TO INVITE:")
    for friend in friends_to_invite:
        print(friend)
        if friend not in processed:
            all_friends_processed = False
    print(friends_to_invite)
    print("PROCESSED FRIENDS:")
    for friend in processed:
        print (friend)
    print(processed)
    print("TOTAL INVITATIONS SENT: " + str(total_invitations))
    print()
    if all_friends_processed == True:
        print("ALL POSSIBLE AND AVAILABLE FRIENDS PROCESSED!")
        print("INVITE MORE FRIENDS AND/OR START NEW COMMUNITY SESSION.")
        return 1
    else:
        print("NOT ALL POSSIBLE AND AVAILABLE FRIENDS PROCESSED. WILL CONTINUE...")
    print()

    count = 0
    index = 0
    captcha_encountered = False
    captcha_solved = False
    captcha_sid = ""
    captcha_key = ""
    while (count < CONFIG["MAX_INVITES_PER_SESSION"] and index < len(friends_to_invite)):
        user_id = friends_to_invite[index]

        if (user_id in processed):
            print("USER " + str(user_id) + " IS ALREADY PROCESSED. SKIPPING...")
            index = index + 1
            continue

        print("INVITING USER " + str(user_id) + "...")
        print()

        url = BASE_URL + "groups.invite?group_id=" + CONFIG["COMMUNITY_ID"] + "&user_id=" + str(user_id) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
        if (captcha_encountered == True and captcha_solved == True):
            captcha_encountered = False
            captcha_solved = False
            url = url + "&captcha_sid=" + captcha_sid + "&captcha_key=" + captcha_key
        print(url)
        print()

        request = requests.get(url)
        time.sleep(1)
        content = request.content 
        print(content)
        print()

        response = json.loads(content)
        if ("response" in response and response["response"] == 1):
            print("INVITED!")
            print()
            count = count + 1
            print("CURRENT SESSION INVITATIONS SENT: " + str(count))
            print()
            total_invitations = total_invitations + 1
            print("TOTAL INVITATIONS SENT: " + str(total_invitations))
            print()

        if ("error" in response):
            response_body = response["error"]
            error_code = response_body["error_code"]
            error_msg = response_body["error_msg"]
            error_text = ""
            if ("error_text" in response_body):
                error_text = response_body["error_text"] 
            print("ERROR")
            print("ERROR CODE: " + str(error_code))
            print("ERROR MSG: " + error_msg)
            print("ERROR TEXT: " + error_text)
            print()
            if (error_code == 14): # error_msg == "Captcha needed"
                captcha_encountered = True
                captcha_solved = False
                number_of_tries = 0
                while not captcha_solved:
                    if (number_of_tries > MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA):
                        break
                    try:
                        captcha_sid = response_body["captcha_sid"]
                        captcha_img = response_body["captcha_img"]
                        print("CAPTCHA ENCOUNTERED!")
                        print("CAPTCHA SID: " + captcha_sid)
                        print("CAPTCHA IMG: " + captcha_img)
                        print()
                        request = requests.get(captcha_img)
                        content = request.content
                        with open("captcha_invite.jpeg", mode='wb') as local_file:
                            local_file.write(content)
                        captcha_fp = open('captcha_invite.jpeg', 'rb')
                        client = AnticaptchaClient(CONFIG["ANTI_CAPTCHA_API_KEY"])
                        task = ImageToTextTask(captcha_fp)
                        job = client.createTask(task)
                        job.join()
                        captcha_key = job.get_captcha_text()
                        print("CAPTCHA TEXT: " + captcha_key)
                        print()
                    except Exception as e:
                        print("COULD NOT SOLVE CAPTCHA!")
                        print("REASON:")
                        print(e)
                        print()
                        captcha_solved = False
                        number_of_tries = number_of_tries + 1
                        time.sleep(1)
                        continue
                    captcha_solved = True
                    break
                if (not captcha_solved) and (number_of_tries > MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA):
                    print("COULD NOT SOLVE CAPTCHA IN " + str(MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA) + " TRIES")
                    print()
                    break
            if (error_code == 103): # error_msg == "Out of limits: invites limit"
                print("OUT OF INVITES LIMITS FOR THIS/CURRENT/TODAY SESSION")
                print()
                break

        if (captcha_encountered == True):
            continue
        
        processed.add(user_id)
        index = index + 1

    print("SESSION OVER. Come back next time (tomorrow, maybe).")
    print("SESSION RESULTS:")
    print("PROCESSED FRIENDS:")
    for friend in processed:
        print (friend)
    print(processed)
    print()
    print("CURRENT SESSION INVITES COUNT: " + str(count))
    print("NEXT STARTING INDEX: " + str(index))
    print("TOTAL INVITATIONS SENT: " + str(total_invitations))
    print()

    all_friends_processed = True
    for friend in friends_to_invite:
        if friend not in processed:
            all_friends_processed = False
            break
    if all_friends_processed == True:
        print("ALL POSSIBLE AND AVAILABLE FRIENDS PROCESSED!")
        print("INVITE MORE FRIENDS AND/OR START NEW COMMUNITY SESSION.")
    else:
        print("NOT ALL POSSIBLE AND AVAILABLE FRIENDS PROCESSED. WILL CONTINUE NEXT TIME...")
    print()

    SaveState()
    print("STATE DATA SUCCESSFULLY SAVED")
    print("SEE YOU LATER! (TOMORROW, MAYBE)")

    return 0

main()