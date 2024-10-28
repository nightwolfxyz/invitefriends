import os
import os.path
import requests
import json
import math
import time
from python_anticaptcha import AnticaptchaClient, ImageToTextTask

BASE_URL = "https://api.vk.com/method/"

CONFIG = {}

captcha_encountered = False
captcha_sid = ""
captcha_key = ""

processed = set()
total_invitations = 0

def GetGroupMembers(group_id):
    global CONFIG

    result = set()

    offset = 0
    count = 0
    url = BASE_URL + "groups.getMembers?group_id=" + str(group_id) + "&offset=" + str(offset) + "&count=" + str(count) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
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

    response_body = response["response"]
    number_of_group_members = response_body["count"]
    number_of_pages = math.ceil(number_of_group_members / CONFIG["PAGE_SIZE"])
    print("Number of group members: " + str(number_of_group_members))
    print("Number of pages: " + str(number_of_pages))
    print()

    for page_index in range(number_of_pages):
        offset = page_index * CONFIG["PAGE_SIZE"]
        count = CONFIG["PAGE_SIZE"]
        url = BASE_URL + "groups.getMembers?group_id=" + str(group_id) + "&offset=" + str(offset) + "&count=" + str(count) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
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

def GetUsers(user_ids: list):
    global CONFIG
    result = []
    params = ""
    index = 0
    for user_id in user_ids:
        params = params + str(user_id)
        if (index < len(user_ids) - 1):
            params = params + ", "
        index = index + 1
    url = BASE_URL + "users.get?user_ids=" + params + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
    print(url)
    print()
    request = requests.get(url)
    time.sleep(1)
    content = request.content
    print(content)
    print()
    response = json.loads(content)
    print(response)
    print()
    if "response" not in response:
        return result
    response_body = response["response"]
    print(response_body)
    print()
    return response_body

def GetUserIds():
    user_ids = []
    with open("users.txt", "rt") as read_file:
        user_ids = read_file.readlines()
    users = []
    number_of_user_ids = len(user_ids)
    number_of_pages = math.ceil(number_of_user_ids / CONFIG["MINI_PAGE_SIZE"])
    for page_index in range(number_of_pages):
        params = ""
        index = page_index * CONFIG["MINI_PAGE_SIZE"]
        end = min(number_of_user_ids, (page_index + 1) * CONFIG["MINI_PAGE_SIZE"])
        while (index < end):
            params = params + user_ids[index]
            if (index < end - 1):
                params = params + ", "
            index = index + 1
        url = BASE_URL + "users.get?user_ids=" + params + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
        print(url)
        print()
        request = requests.get(url)
        time.sleep(1)
        content = request.content
        print(content)
        print()
        response = json.loads(content)
        print(response)
        print()
        if "response" not in response:
            continue
        response_body = response["response"]
        for user in response_body:
            if "id" in user:
                users.append(user["id"])
    return users

def AddFriend(id):
    global CONFIG
    global captcha_encountered
    global captcha_sid
    global captcha_key
    global processed
    global total_invitations
    if (id in processed):
        return 0
    url = BASE_URL + "friends.add?user_id=" + str(id) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
    if (captcha_encountered == True):
        captcha_encountered = False
        url = url + "&captcha_sid=" + captcha_sid + "&captcha_key=" + captcha_key
    print(url)
    print()
    request = requests.get(url)
    time.sleep(1)
    content = request.content
    print(content)
    print()
    response = json.loads(content)
    print(response)
    print()
    if "response" in response:
        response_body = response["response"]
        print(response_body)
        print()
        if response_body == 1:
            total_invitations = total_invitations + 1
        if id not in processed:
            processed.add(id)
        return 0 
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
        if (error_code == 9 or error_code == 29):
            # error_msg == "Flood control: cannot add this user to friends"
            # error_text == "К сожалению, вы не можете добавлять больше друзей за один день. Пожалуйста, попробуйте завтра."
            # error_msg == "Rate limit reached"
            print("OUT OF INVITES LIMITS FOR THIS/CURRENT/TODAY SESSION")
            print()
            return -1
        if (error_code == 14): 
            # error_msg == "Captcha needed"
            captcha_encountered = True
            captcha_sid = response_body["captcha_sid"]
            captcha_img = response_body["captcha_img"]
            print("CAPTCHA ENCOUNTERED!")
            print("CAPTCHA SID: " + captcha_sid)
            print("CAPTCHA IMG: " + captcha_img)
            print()
            request = requests.get(captcha_img)
            content = request.content
            with open("captcha_friends.jpeg", mode='wb') as local_file:
                local_file.write(content)
            captcha_fp = open('captcha_friends.jpeg', 'rb')
            client = AnticaptchaClient(CONFIG["ANTI_CAPTCHA_API_KEY"])
            task = ImageToTextTask(captcha_fp)
            job = client.createTask(task)
            job.join()
            captcha_key = job.get_captcha_text()
            print("CAPTCHA TEXT: " + captcha_key)
            print()
            return 1
    if id not in processed:
        processed.add(id)
    return 0

def AddFriendsFromUsers(user_ids):
    for user_id in user_ids:
        users = GetUsers([user_id])
        for user in users:
            if "id" in user:
                id = user["id"]
                result = AddFriend(id)
                if result < 0:
                    return result
                while captcha_encountered:
                    result = AddFriend(id)
                    if result < 0:
                        return result
    return 0

def AddFriendsFromGroups(group_ids):
    for group_id in group_ids:
        members = GetGroupMembers(group_id)
        for member in members:
            result = AddFriend(member)
            if result < 0:
                return result
            while captcha_encountered:
                result = AddFriend(member)
                if result < 0:
                    return result
    return 0

def LoadState():
    global processed
    global total_invitations

    if (os.path.exists("processed_friends.json")):
        with open("processed_friends.json", "r") as read_file:
            processed_list = json.load(read_file)
            for id in processed_list:
                processed.add(id)

    if (os.path.exists("total_invitations_friends.json")):
        with open("total_invitations_friends.json", "r") as read_file:
            total_invitations = json.load(read_file)

def SaveState():
    global processed
    global total_invitations
    
    processed_list = []
    for id in processed:
        processed_list.append(id)
    processed.clear()

    with open("processed_friends.json", "w") as write_file:
        json.dump(processed_list, write_file)

    with open("total_invitations_friends.json", "w") as write_file:
        json.dump(total_invitations, write_file)

def main():
    global CONFIG

    if not os.path.exists("invitefriends.conf"):
        print("ERROR: Configuration file is missing!")
        return -1

    with open("invitefriends.conf", "r") as read_file:
        CONFIG = json.load(read_file)

    if "USER_ID" not in CONFIG:
        print("ERROR: USER_ID setting is missing!")
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

    if "MINI_PAGE_SIZE" not in CONFIG:
        print("ERROR: MINI PAGE_SIZE setting is missing!")
        return -1
    
    if "API_VERSION" not in CONFIG:
        print("ERROR: API_VERSION setting is missing!")
        return -1

    print("Configuration: ")
    print(CONFIG)
    print()
    print("USER_ID: " + CONFIG["USER_ID"])
    print("USER_ACCESS_TOKEN: " + CONFIG["USER_ACCESS_TOKEN"])
    print("ANTI_CAPTCHA_API_KEY: " + CONFIG["ANTI_CAPTCHA_API_KEY"])
    print("PAGE_SIZE: " + str(CONFIG["PAGE_SIZE"]))
    print("MINI_PAGE_SIZE: " + str(CONFIG["MINI_PAGE_SIZE"]))
    print("API_VERSION: " + CONFIG["API_VERSION"])
    print()

    LoadState()

    user_ids = []
    group_ids = []

    with open("users.txt", "rt") as read_file:
        user_ids = read_file.readlines()
    
    with open("groups.txt", "rt") as read_file:
        group_ids = read_file.readlines()

    result = AddFriendsFromUsers(user_ids)
    if (result < 0):
        SaveState()
        return 0

    result = AddFriendsFromGroups(group_ids)
    if (result < 0):
        SaveState()
        return 0
    
    SaveState()
    return 0

main()