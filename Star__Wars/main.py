import argparse
import json
from src.star_wars_api import search_star_wars_character, get_homeworld_info
import datetime
import os
from prettytable import PrettyTable

#arxeio gia na mhn caxnv synexeia sto api. dyo lejika kai mia lista
CACHE_FILE = 'cache.json'

#load to arxeio
def load_cache():
    try:
        with open(CACHE_FILE, 'r') as file:
            loaded_cache = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        loaded_cache = {'characters': {}, 'homeworlds': {}, 'search_history': []}
    
    if not isinstance(loaded_cache, dict):
        loaded_cache = {'characters': {}, 'search_history': []}
    
    # Ensure both 'characters' and 'homeworlds' keys are present
    loaded_cache.setdefault('characters', {})
    loaded_cache.setdefault('homeworlds', {})
    loaded_cache.setdefault('search_history', [])
    
    return loaded_cache



def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file, default=str)  

#synarthsh gia to vizual
def display_search_history(cache):
    search_history = cache.get('search_history', [])

    if not search_history:
        print("No search history available.")
    else:
        # Create a PrettyTable instance with column names
        table = PrettyTable(["Inputed Name", "Name", "Height", "Mass", "Birth Year", "Timestamp", "Homeworld Name", "Homeworld Population", "Earth Years", "Earth Days"])  # Update column names here

        # Iterate over the search history and add rows to the table
        for entry in search_history:
            inputed_name = entry['name']
            character_result = entry['result']
            
            if character_result is not None:
                character_info = character_result.get('properties', {})
                character_name = character_info.get("name", "Name not found")
                height = character_info.get('height', 'None')
                mass = character_info.get('mass', 'None')
                birth_year = character_info.get('birth_year', 'None')
            else:
                character_name = "Character not found"
                height = 'None'
                mass = 'None'
                birth_year = 'None'
            
            timestamp = entry['timestamp']
            homeworld_name = entry.get('homeworld_Name', 'None') 
            homeworld_population = entry.get('homeworld_Population', 'None')  
            years = entry.get('years', 'None')
            days = entry.get('days', 'None')
            table.add_row([inputed_name, character_name, height, mass, birth_year, timestamp, homeworld_name, homeworld_population, years, days])

        # Set the alignment of columns to left
        table.align["Inputed Name"] = "l"
        table.align["Name"] = "l"
        table.align["Height"] = "l"
        table.align["Mass"] = "l"
        table.align["Birth Year"] = "l"
        table.align["Timestamp"] = "l"
        table.align["Homeworld Name"] = "l"
        table.align["Homeworld Population"] = "l"
        table.align["Earth Years"] = "l"
        table.align["Earth Days"] = "l"

        # Print the table
        print(table)



def main():

    flag =False
    flaghome=False

    cache = load_cache()

    #arguments, command line
    # Create the top-level parser
    parser = argparse.ArgumentParser(description="Search for a Star Wars character by name.")
    
    # Create subparsers for the 'search' and 'clear' subcommands
    subparsers = parser.add_subparsers(dest='command', help="Subcommands")
    
    # Subparser for 'search'
    search_parser = subparsers.add_parser('search', help="Search for a character")
    search_parser.add_argument("name", nargs='?', default=None, help="Name of the Star Wars character to search for.")
    search_parser.add_argument("--world", action="store_true", help="Retrieve homeworld information.")

    #'clear'
    cache_parser = subparsers.add_parser('cache', help="Cache operations")
    cache_parser.add_argument("--clean", action="store_true", help="Clear the search cache")

    # Subparser for 'history'
    history_parser = subparsers.add_parser('history', help="Display search history")

    args = parser.parse_args()

    #arguments, command line

    # θέλει να ψάξει?
    if args.command == "search": 

        #καλει την συναρτηση που ρωταει το api                                     
        result, flag, last_searched = search_star_wars_character(args.name, cache)
        save_cache(cache)

        #αν υπαρχει
        if result:
            # παιρνει τα αποτελεσματα απο το εμφωλευμενο dictionary                                                      
            properties = result.get("properties", {})
            character_name = properties.get("name", "Name not found")  
            #πριντ τα ντατα
            print(f"Name: {character_name}")
            print(f"Height: {properties.get('height', 'Height not found')}")
            print(f"Mass: {properties.get('mass', 'Mass not found')}")
            print(f"Birth Year: {properties.get('birth_year', 'Birth Year not found')}")

            #αν θελει και τον κοσμο του χαρακτηρα
            if args.world:

                #pairnei απο τα ντατα του χαρακτηρα τον κοσμο του
                homeworld_url = properties.get("homeworld")

                #καλει την συναρτηση που ψαχνει στο api
                homeworld_data, flaghome, last_searched = get_homeworld_info(homeworld_url, cache)
                save_cache(cache)

                #an yparxei
                if homeworld_data:

                    #ta pairnei apo to εμφωλευμενο dictionary
                    homeworld_properties = homeworld_data.get("result", {}).get("properties", {})
                    homeworld_name = homeworld_properties.get("name", "Homeworld Name not found")
                    homeworld_population = homeworld_properties.get("population", "Homeworld Population not found")

                    #ta kanei print        
                    print("\nHomeworld")
                    print("----------------")
                    print(f"Name: {homeworld_name}")
                    print(f"Population: {homeworld_population}")

                    #ypologizv ton enan xrono toy kaue planhth
                    years= round(float(homeworld_properties.get("orbital_period"))/365,2)

                    #ypologizv thn mia mera toy kaue planhth
                    days=round(float(homeworld_properties.get("rotation_period"))/24,2)

                    print(f"\nIn {homeworld_name}, 1 year on earth is {years} years and 1 day is {days} days")
                else:
                    print("Homeworld information not available.")

            # timestap kai print timestamp
            if flaghome == False:
                if flag == False:
                    timestamp = last_searched
                else:
                    timestamp = last_searched
                print(f"\ncached: {timestamp}")
            else:
                timestamp = last_searched
                print(f"\ncached: {timestamp}")

            #ενημερωνω την λιστα στη cache για το viz
            if args.world:
                cache['search_history'].append({'name': args.name, 'result': result, 'timestamp': timestamp, 'homeworld_Name': homeworld_name, 'homeworld_Population': homeworld_population, 'years':years, 'days': days})
                save_cache(cache)
            else:
                cache['search_history'].append({'name': args.name, 'result': result, 'timestamp': timestamp})
                save_cache(cache)

        #αν δεν υπαρχει
        else:
            print("The force is not strong within you")
            print(f"\ncached: {last_searched}")
            cache['search_history'].append({'name': args.name, 'result': result, 'timestamp': last_searched})
            save_cache(cache)
    elif args.command == "cache" and args.clean:
        cache.clear()
        save_cache(cache)
        print("Cache cleared")

    #θελει να δει το history?    
    if args.command == "history":
        display_search_history(cache)
 


if __name__ == "__main__":
    main()