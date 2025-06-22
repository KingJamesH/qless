import requests
import time
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
        self.website = data.get('website', '')  # Store website URL if available
        date_obj = datetime.now()
        day_of_week = date_obj.weekday()
        try:
            # day of week: monday=0, sunday=6
            time_ranges = data.get('hours', {}).get('week_ranges', [])[day_of_week]
            if time_ranges:
                opentimemin = int(time_ranges[0].get('open_time'))
                closetimemin = int(time_ranges[0].get('close_time'))
                
                # Convert minutes to 12-hour format with AM/PM
                def format_12h(minutes):
                    hours = minutes // 60
                    mins = minutes % 60
                    period = 'AM' if hours < 12 else 'PM'
                    hours = hours % 12
                    if hours == 0:
                        hours = 12  # Convert 0 to 12 for 12 AM
                    return f"{hours}:{mins:02d} {period}"
                
                opentime = format_12h(opentimemin)
                closetime = format_12h(closetimemin)
                
                self.times = [opentime, closetime]
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


# Fallback location IDs for common locations
FALLBACK_LOCATION_IDS = {
    'new york': '60763',
    'boston': '60745',
    'chicago': '60805',
    'los angeles': '60898',
    'san francisco': '60878',
    'short hills': '34439',  # Added Short Hills fallback
    'san diego': '60773',
    'seattle': '60824',
    'austin': '60734',
    'miami': '60800'
}

def get_id(town):
    try:
        url = "https://restaurants222.p.rapidapi.com/typeahead"
        payload = {
            "q": town,
            "language": "en_US"
        }
        headers = {
            "x-rapidapi-key": "a44f097be9mshf0bbb24982db52fp194825jsne6c53e31cf79",
            "x-rapidapi-host": "restaurants222.p.rapidapi.com",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        print(f"Fetching location ID for: {town}")
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        towniddata = response.json()
        results = towniddata.get("results", {})
        data_list = results.get("data", [])

        if not data_list:
            print(f"❌ No locations found for: {town}")
            return None

        # Get the first valid location ID
        for item in data_list:
            result_obj = item.get("result_object", {})
            location_id = result_obj.get("location_id")
            if location_id:
                print(f"✅ Found location ID: {location_id} for {result_obj.get('name')}")
                return location_id

        print(f"❌ No valid location ID found for: {town}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error making API request: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error in get_id: {str(e)}")
        return None


def get_restaurants(town, max_retries=2):
    print(f"\nSearching for restaurants in: {town}")
    
    # Get location ID
    try:
        location_id = get_id(town)
        if not location_id:
            print("❌ Could not get location ID")
            return []
    except Exception as e:
        print(f"❌ Error getting location ID: {str(e)}")
        return []
    
    # Get town coordinates for distance calculation
    try:
        global town_loc
        town_loc = get_lat_long(town)
        if not town_loc:
            print("⚠️  Could not get coordinates for distance calculation")
    except Exception as e:
        print(f"⚠️  Error getting coordinates: {str(e)}")
    
    # Fetch restaurants
    url = "https://restaurants222.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": "a44f097be9mshf0bbb24982db52fp194825jsne6c53e31cf79",
        "x-rapidapi-host": "restaurants222.p.rapidapi.com",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        print("\nFetching restaurants...")
        payload = {
            "location_id": str(location_id),
            "limit": "20",
            "language": "en_US",
            "currency": "USD"
        }
        
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Process the response
        data = response.json()
        results = data.get("results", {})
        restaurants = results.get("data", [])
        
        if not restaurants:
            print("⚠️  No restaurants found in API response")
            return []
            
        print(f"✅ Found {len(restaurants)} restaurants in the API response")
        
        # Log first few restaurants for debugging
        for i, restaurant in enumerate(restaurants[:3], 1):
            print(f"  {i}. {restaurant.get('name')} (ID: {restaurant.get('location_id')})")
        
        return restaurants
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {str(e)}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error in get_restaurants: {str(e)}")
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
    print(f"\n{'='*50}\nStarting restaurant search for: {town}\n{'='*50}")
    
    try:
        # Get town coordinates
        print("\nGetting coordinates for town...")
        global town_loc
        town_loc = get_lat_long(town)

        if not town_loc:
            print("❌ Error: Could not find coordinates for the specified location.")
            return {}
            
        print(f"✅ Found coordinates: {town_loc}")

        # Get restaurants
        print("\nFetching restaurants...")
        restaurants = get_restaurants(town)
        
        if not restaurants:
            print("❌ No restaurants found for the specified location.")
            return {}
            
        print(f"\nProcessing {len(restaurants)} restaurants...")
        restaurant_objects = [Restaurant(rest) for rest in restaurants]
        
        restaurant_data = {}
        valid_restaurants = 0
        
        for r in restaurant_objects:
            try:
                # Skip chain restaurants
                if any(chain.lower() in r.name.lower() for chain in restaurant_chains):
                    print(f"  ⏩ Skipping chain restaurant: {r.name}")
                    continue
                
                # Calculate distance if we have valid coordinates
                if r.location and r.location[0] and r.location[1]:
                    distance = calculate_distance(town_loc, r.location)
                    distance = round(distance, 2)
                    print(f"  📍 {r.name} - {distance} miles away")
                else:
                    print(f"  ⚠️  Missing coordinates for {r.name}, using default distance")
                    distance = 2.0  # Default distance if coordinates are missing
                
                # Get the times from the Restaurant object
                times = getattr(r, 'times', ['00:00', '23:59'])
                
                # Debug output
                print(f"  ⏰ {r.name} - Times: {times[0]} to {times[1]}")
                
                restaurant_data[r.name] = {
                    'cuisine': r.cuisine,
                    'rating': r.rating,
                    'distance': distance,
                    'photo': r.photo,
                    'is_open': r.is_open,
                    'times': times,  # This is what the frontend is looking for
                    'opening_time': times[0],
                    'closing_time': times[1],
                    'website': getattr(r, 'website', ''),
                    'price_level': r.price_level,
                    'review_count': getattr(r, 'review_count', 0),
                    'dietary_options': getattr(r, 'dietary_options', [])
                }
                valid_restaurants += 1
                
            except Exception as e:
                print(f"  ❌ Error processing restaurant '{r.name}': {str(e)}")
                continue

        print(f"\n✅ Successfully processed {valid_restaurants} out of {len(restaurant_objects)} restaurants")
        if valid_restaurants == 0:
            print("⚠️  No valid restaurants were found after filtering")
            return {}
            
        return restaurant_data

    except Exception as e:
        print(f"\n❌ Critical error in run function: {str(e)}")
        import traceback
        traceback.print_exc()
        return {}
    # print("\nRestaurants sorted by distance from {}:\n".format(town))
    # for name, dist in sorted_restaurants:
    #     if dist != float('inf'):
    #         print(name, ": ", dist, "mi")
    #     else:
    #         print(name, ": Location not available")