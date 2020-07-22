from discord.ext import commands
from dotenv import load_dotenv
import requests
import os
import json



load_dotenv()

global api_key
global HEADERS
# create HEADERS and base_url
api_key = os.getenv('DESTINY_API_KEY')
bot_name = os.getenv('BOT_NAME')
bot_version = os.getenv('BOT_VERSION')
client_id = os.getenv('DESTINY_OATH_CLIENT_ID')
email = os.getenv('EMAIL')
HEADERS = {
    'X-API-Key': api_key,  
    'User-Agent': bot_name + "/" + bot_version + " AppId/" + client_id + " (+https://github.com/michaelScarfi/Discord-Bot;" + email + ")"
}
base_url = "https://www.bungie.net/platform"
user_name = "Scarfi"
character = "Hunter"


# helper function to get memberID and membershipType from steam_name
def get_member_info(name:str, platform: int = 3):
    # 3 = steam, 2 = xbox, 1 = psn, (4 = stadia?)

    # base url
    global base_url
    

    # create blank MemberID, needed to raise proper error
    memberID = ""

    #make request for membership ID
    url = base_url + f'/Destiny2/SearchDestinyPlayer/{platform}/{name}/'
    r = requests.get(url, headers = HEADERS)

    #convert the json object we received into a Python dictionary object
    #and print the name of the item
    get_user_return = r.json()
    del r

    # check to get user with exact display name, not full-proof but should reduce issues with grabbing the wrong player
    for user in get_user_return['Response']:
        try:
            if(user['displayName'] == name):
                # get member ID for user
                memberID = user['membershipId']

                # get membershipType
                membershipType = user['membershipType']
        except IndexError:
            print("Bungie account could not be found, if there is any whitespace in your name make sure you surround it with quotes")

    # could not get exact match, return first results
    if(memberID == ""):
        try: 
            # get member ID for user
            memberID = get_user_return['Response'][0]['membershipId']

            # get membershipType
            membershipType = get_user_return['Response'][0]['membershipType']
        except IndexError:
            print("Bungie account could not be found, if there is any whitespace in your name make sure you surround it with quotes")


    # deleting json to save resources
    del get_user_return

    # return memberID and membershipType
    return [memberID, membershipType]

# helper function to get player info as player[memberID, membershipType, class_type, char_ids]
def get_player_char_info(memberID, membershipType, character: str):
    global base_url

    # convert character as string to int, 0 = Titan, 1 = Hunter, 2 = Warlock
    if(character.lower() == "titan"):
        character_class = 0
    elif(character.lower() == "hunter"):
        character_class = 1
    elif(character.lower() == "warlock"):
        character_class = 2
    else:
        raise errors.NotaDestinyClass("Class name not recognized, please input a valid Destiny class")

    # make request for player info, getting character info.
    url = base_url + f'/Destiny2/{membershipType}/Profile/{memberID}/?components=200'
    r = requests.get(url, headers = HEADERS)
    get_characters_return = r.json()
    del r

    # get character IDs and confirm user has a character of the requested class
    char_ids = []
    has_character = False
    for key in get_characters_return['Response']['characters']['data']:
        char_ids.append(key)
        if (get_characters_return['Response']['characters']['data'][str(key)]['classType'] == character_class):
            has_character = True
            char_id = key

    # if user does not have a character of that class, raise exception
    if (not has_character):
        raise errors.NoCharacterOfClass(f'You do not have a character of class {character}')

    # delete json to save memory
    del get_characters_return

    player_char_info = [memberID, membershipType, character_class, char_ids, char_id]
    return player_char_info


player_info = get_member_info(user_name, 3)

player_char_info = get_player_char_info(player_info[0], player_info[1], character)
destinyMembershipId = player_char_info[0]
membershipType = player_char_info[1]
character_class = player_char_info[2]
char_ids = player_char_info[3]
characterId = player_char_info[4]

#make request for membership ID
url = base_url + f'/Destiny2/Stats/PostGameCarnageReport/6657805713/'
r = requests.get(url, headers = HEADERS)

#convert the json object we received into a Python dictionary object
#and print the name of the item
get_user_return = r.json()

with open('test_api_return.json', 'w') as data_file:
    json.dump(get_user_return, data_file, indent = 4)



