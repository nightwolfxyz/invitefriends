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
captcha_solved = False
captcha_sid = ""
captcha_key = ""
MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA = 100

processed = set()
count = 0
total_invitations = 0

#TODO
invites_graph = [38]
invites_index = 0

def GetGroupMembers(group_id):
    global CONFIG

    # result = set()

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
        return -1
        # return result

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
                result = AddFriend(item)
                if result < 0:
                    return result
                while captcha_encountered:
                    result = AddFriend(item)
                    if result < 0:
                        return result
                # result.add(item)
    # return result
    return 0

def GetUsers(user_ids: list):
    global CONFIG
    # result = []
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
        return -1
    response_body = response["response"]
    print(response_body)
    print()
    # return response_body
    for user in response_body:
        if "id" in user:
            user_id = user["id"]
            result = AddFriend(user_id)
            if result < 0:
                return result
            while captcha_encountered:
                result = AddFriend(id)
                if result < 0:
                    return result
    return 0

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
    global captcha_solved
    global captcha_sid
    global captcha_key
    global processed
    global count
    global total_invitations
    global MAX_NUMBER_OF_TRIES_TO_SOLVE_CAPTCHA

    if (id in processed):
        return 0

    url = BASE_URL + "friends.add?user_id=" + str(id) + "&access_token=" + CONFIG["USER_ACCESS_TOKEN"] + "&v=" + CONFIG["API_VERSION"]
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
    print(response)
    print()

    if "response" in response:
        response_body = response["response"]
        print(response_body)
        print()
        if response_body == 1:
            count = count + 1
            total_invitations = total_invitations + 1
            print("COUNT: " + str(count))
            print("TOTAL INVITATIONS: " + str(total_invitations))
            print()
        if id not in processed:
            processed.add(id)
            # print("PROCESSED: " + str(processed.__len__))
        #if count >= CONFIG["MAX_INVITES_PER_SESSION"]:
        if count >= invites_graph[invites_index]:
            print("OUT OF COUNT INVITES LIMITS FOR THIS/CURRENT/TODAY SESSION")
            print()
            return -1
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
        if (error_code == 242):
            # error_msg == "Too many friends: friends count exceeded"
            # error_text == "К сожалению, вы не можете добавлять больше 10 000 друзей. Возможно, вам стоит создать для них группу, в группе нет ограничений на количество участников."
            print("TOO MANY FRIENDS")
            print()
            return -1
        if (error_code == 14): 
            # error_msg == "Captcha needed"
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
                return -1
            return 1
    if id not in processed:
        processed.add(id)
    return 0

def AddFriendsFromUsers(user_ids):
    for user_id in user_ids:
        result = GetUsers([user_id])
        if result < 0:
            return result
        # users = GetUsers([user_id])
        # for user in users:
        #     if "id" in user:
        #         id = user["id"]
        #         result = AddFriend(id)
        #         if result < 0:
        #             return result
        #         while captcha_encountered:
        #             result = AddFriend(id)
        #             if result < 0:
        #                 return result
    return 0

def AddFriendsFromGroups(group_ids):
    for group_id in group_ids:
        result = GetGroupMembers(group_id)
        if result < 0:
            return result
        # members = GetGroupMembers(group_id)
        # for member in members:
        #     result = AddFriend(member)
        #     if result < 0:
        #         return result
        #     while captcha_encountered:
        #         result = AddFriend(member)
        #         if result < 0:
        #             return result
    return 0

def LoadState():
    global processed
    global total_invitations
    global invites_graph
    global invites_index

    if (os.path.exists("processed_friends.json")):
        with open("processed_friends.json", "r") as read_file:
            processed_list = json.load(read_file)
            for id in processed_list:
                processed.add(id)

    if (os.path.exists("total_invitations_friends.json")):
        with open("total_invitations_friends.json", "r") as read_file:
            total_invitations = json.load(read_file)

    if (os.path.exists("invites_index_friends.json")):
        with open("invites_index_friends.json", "r") as read_file:
            invites_index = json.load(read_file)

def SaveState():
    global processed
    global total_invitations
    global invites_graph
    global invites_index
    
    processed_list = []
    for id in processed:
        processed_list.append(id)
    processed.clear()

    with open("processed_friends.json", "w") as write_file:
        json.dump(processed_list, write_file)

    with open("total_invitations_friends.json", "w") as write_file:
        json.dump(total_invitations, write_file)

    invites_index = (invites_index + 1) % len(invites_graph)
    with open("invites_index_friends.json", "w") as write_file:
        json.dump(invites_index, write_file)

def AddFriends():
    user_ids = []
    group_ids = []
    with open("users.txt", "rt") as read_file:
        user_ids = read_file.readlines()
    with open("groups.txt", "rt") as read_file:
        group_ids = read_file.readlines()
    result = AddFriendsFromUsers(user_ids)
    if (result < 0):
        return result
    result = AddFriendsFromGroups(group_ids)
    if (result < 0):
        return result
    return 0

def main():
    global CONFIG
    global count
    global total_invitations
    global invites_graph
    global invites_index

    result = 0

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
    print("USER_ACCESS_TOKEN: " + CONFIG["USER_ACCESS_TOKEN"])
    print("ANTI_CAPTCHA_API_KEY: " + CONFIG["ANTI_CAPTCHA_API_KEY"])
    print("PAGE_SIZE: " + str(CONFIG["PAGE_SIZE"]))
    print("MINI_PAGE_SIZE: " + str(CONFIG["MINI_PAGE_SIZE"]))
    print("MAX_INVITES_PER_SESSION: " + str(CONFIG["MAX_INVITES_PER_SESSION"]))
    print("API_VERSION: " + CONFIG["API_VERSION"])
    print()

    LoadState()

    print("INVITES INDEX: " + str(invites_index))
    print("INVITES GRAPH COUNT: " + str(len(invites_graph)))
    print("INVITES GRAPH: ")
    for i in invites_graph:
        print(i)
        #print(str(i))
    print(invites_graph)
    #print(str(invites_graph))
    print()

    print("TOTAL INVITATIONS: " + str(total_invitations))
    # print("PROCESSED: " + str(processed.__len__))
    print()

    result = AddFriends()
    
    SaveState()

    print("COUNT: " + str(count))
    print("NEXT INVITES INDEX: " + str(invites_index))
    print("TOTAL INVITATIONS: " + str(total_invitations))
    print()

    return result

main()