import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime


town_loc = None


class Restaurant():
    def __init__(self, data):
        self.name = data.get('name')
        self.location = (data.get('latitude'), data.get('longitude'))
        self.rating = data.get('rating')
        self.is_open = not data.get('is_closed')
        self.price_level = data.get('price_level')
        try:
            self.cuisine = data.get('cuisine')[0].get('name')
            print(data.get('cuisine'))
            print(self.cuisine + "\n\n")
        except:
            self.cuisine = 'No specific cuisine'
        self.dietary_options = [option.get('name') for option in data.get('dietary_restrictions')]
        self.photo = data.get('photo', {}).get('images', {}).get('medium', {}).get('url', 'No photo available')
        date_obj = datetime.now()
        day_of_week = date_obj.weekday()
        try:
            # day of week: monday=0, sunday=6
            time_ranges = data.get('hours', {}).get('week_ranges', [])[day_of_week]
            if time_ranges:
                opentimemin = int(time_ranges[0].get('open_time'))
                closetimemin = int(time_ranges[0].get('close_time'))
                
                opentime = str(opentimemin//60) + ":" + str(opentimemin%60)
                closetime = str(closetimemin//60) + ":" + str(closetimemin%60)
                if opentime[-2]==":":
                    opentime+="0"
                if closetime[-2]==":":
                    closetime+="0"


                self.times = [
                    opentime if opentime else '00:00',
                    closetime if closetime else '23:59'
                ]
            else:
                # default
                self.times = ['00:00', '23:59']
        except (IndexError, TypeError) as e:
            print("Error processing times for " + data.get('name') + ": " + str(e))
            self.times = ['00:00', '23:59']

def wait_time_calculation(employees, open, total, queue):
   avg_table_time = 20 / employees
   available_capacity = total - open
  
   if available_capacity > 0:
       wait_time = min(queue, available_capacity) * avg_table_time
   else:
       wait_time = queue * avg_table_time
  
   wait_time += queue * 5
  
   return max(5, int(wait_time))


def get_id(town):
    url = "https://restaurants222.p.rapidapi.com/typeahead"
    payload = {
        "q": town,
        "language": "en_US"
    }
    headers = {
        "x-rapidapi-key": "0a2fba2ccbmsh4b0e46c27030e46p19bf52jsnbba99414a639",
        "x-rapidapi-host": "restaurants222.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)


    # print(response.json())
    towniddata = response.json()
    results = towniddata.get("results", {})
    data_list = results.get("data", [])


    locations = []
    for item in data_list:
        result_obj = item.get("result_object", {})
        name = result_obj.get("name")
        location_id = result_obj.get("location_id")
        locations.append({
            "name": name,
            "location_id": location_id
        })


    # print(locations)
    for loc in locations:
        print(loc['location_id'])
        loc_id = loc['location_id']
    return loc_id


def get_restaurants(town):
    try:
        searching_id = get_id(town)
        url = "https://restaurants222.p.rapidapi.com/search"

        payload = {
            "location_id": searching_id,
            "limit": "10", 
            "language": "en_US",
            "currency": "USD"
        }
        headers = {
            "x-rapidapi-key": "0a2fba2ccbmsh4b0e46c27030e46p19bf52jsnbba99414a639",
            "x-rapidapi-host": "restaurants222.p.rapidapi.com",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, data=payload, headers=headers)
        
        # Debug logging
        print("API Response Status Code: " + str(response.status_code))
        print("API Response: " + response.text)

        restaurantdatastuff = response.json()
        data_list = restaurantdatastuff.get("results", {}).get("data", [])
        print("Number of restaurants found: " + str(len(data_list)))
        
        return data_list
    except Exception as e:
        print("Error in get_restaurants: " + str(e))
        return []


def get_lat_long(address):
    geolocator = Nominatim(user_agent="geocoding_app")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None


def calculate_distance(coord1, coord2):
    return geodesic(coord1, coord2).mi


restaurant_chains = [
   "McDonald's", "Burger King", "Wendy's", "Chick-fil-A", "Taco Bell", "KFC",
   "Arby's", "Sonic Drive-In", "Popeyes", "Jack in the Box", "Dairy Queen",
   "Hardee's", "Carl's Jr.", "Subway", "Jimmy John's", "Jersey Mike's Subs",
   "Firehouse Subs", "Panda Express", "Raising Cane's", "In-N-Out Burger",
   "Culver's", "Domino's Pizza", "Pizza Hut", "Papa John's", "Little Caesars",
   "Marco's Pizza", "Papa Murphy's", "California Pizza Kitchen", "Blaze Pizza",
   "MOD Pizza", "Jet's Pizza", "Starbucks", "Dunkin'", "Dutch Bros Coffee",
   "Tim Hortons", "Peet's Coffee", "Biggby Coffee", "Scooter's Coffee",
   "Bagels 4U", "Au Bon Pain",
   "Chipotle Mexican Grill", "Panera Bread", "Shake Shack", "Five Guys",
   "QDOBA Mexican Eats", "Moe's Southwest Grill", "Sweetgreen", "Chopt",
   "Noodles & Company", "CAVA", "Zaxby's", "Wingstop", "El Pollo Loco",
   "Applebee's", "Chili's Grill & Bar", "Olive Garden", "Red Lobster",
   "Outback Steakhouse", "Texas Roadhouse", "LongHorn Steakhouse", "IHOP",
   "Denny's", "Cracker Barrel", "Perkins", "Bob Evans", "TGI Fridays",
   "Ruby Tuesday", "BJ's Restaurant & Brewhouse", "The Cheesecake Factory",
   "Golden Corral", "Hooters", "Friendly's", "Village Inn",
   "Jason's Deli", "Potbelly Sandwich Shop", "McAlister's Deli", "Schlotzsky's",
   "Bojangles", "Church's Chicken"
]


def wait_time_calculation(employees, open, total, queue):
    avg_table_time = 20 / employees
    available_capacity = total - open
    
    if available_capacity > 0:
        wait_time = min(queue, available_capacity) * avg_table_time
    else:
        wait_time = queue * avg_table_time
    
    wait_time += queue * 5
    
    return max(5, int(wait_time))


print(wait_time_calculation(3,0,5,2))

def run(town):
    try:
        global town_loc
        town_loc = get_lat_long(town)

        if not town_loc:
            print("Could not find location.")
            return {}

        restaurants = get_restaurants(town)
        if not restaurants:
            print("No restaurants found")
            return {}

        restaurant_objects = [Restaurant(rest) for rest in restaurants]
        
        restaurant_data = {}
        for r in restaurant_objects:
            try:
                if not any(chain.lower() in r.name.lower() for chain in restaurant_chains):
                    if r.location[0] and r.location[1]:
                        distance = calculate_distance(town_loc, r.location)
                        distance = round(distance, 2)
                    else:
                        distance = 2.0
                    
                    restaurant_data[r.name] = {
                        'rating': r.rating,
                        'distance': distance,
                        'cuisine': r.cuisine,
                        'photo': r.photo,
                        'is_open': r.is_open,
                        'opening_time': r.times[0],
                        'closing_time': r.times[1]
                    }
            except Exception as e:
                print("Error processing restaurant {}: {}".format(r.name, str(e)))
                continue

        return restaurant_data

    except Exception as e:
        print("Error in run function: {}".format(str(e)))
        return {}
    # print("\nRestaurants sorted by distance from {}:\n".format(town))
    # for name, dist in sorted_restaurants:
    #     if dist != float('inf'):
    #         print(name, ": ", dist, "mi")
    #     else:
    #         print(name, ": Location not available")