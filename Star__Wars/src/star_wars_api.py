import requests
from datetime import datetime


def search_star_wars_character(character_name, cache):

    #yparxei sto arxeio?
    if character_name in cache:
        flag = True
        character_data, last_searched = cache[character_name]['data'], cache[character_name]['last_searched']
        print(f"Retrieved from cache.")
        return character_data, flag, last_searched
    
    #den yparxei
    else:
        flag = False
        base_url = "https://www.swapi.tech/api/people/"
        query_parameters = {"name": character_name}
    
        response = requests.get(base_url, params=query_parameters)

        if response.status_code == 200:
            data = response.json()
            results = data.get("result", [])

            #yparxei sto api?
            if results:
                character_data = results[0]
                homeworld_url = character_data.get("properties", {}).get("homeworld")
                cache[character_name] = {"data": character_data, "last_searched": datetime.now(), "homeworld_url": homeworld_url}
                last_searched = datetime.now()
                return character_data, flag, last_searched
            
            #den yparxei
            else:
                cache[character_name] = {"data": None, "last_searched": datetime.now(), "homeworld_url": None}
                last_searched=datetime.now()
                return None, flag, last_searched
        else:
            return None, flag, None



def get_homeworld_info(homeworld_url, cache):
    if homeworld_url in cache['homeworlds']:
        flaghome = True
        homeworld_info = cache['homeworlds'][homeworld_url]
        homeworld_data = homeworld_info['data']
        last_searched = homeworld_info.get('last_searched', 'Not previously cached')
        print(f"Retrieved also homeworld from cache.")
        return homeworld_data, flaghome, last_searched 
    if homeworld_url:
        flaghome = False
        response = requests.get(homeworld_url)
        if response.status_code == 200:
            homeworld_data = response.json()
            cache['homeworlds'][homeworld_url] = {"data": homeworld_data,"last_searched": datetime.now()}
            last_searched=datetime.now()
            return homeworld_data, flaghome, last_searched
    return None

