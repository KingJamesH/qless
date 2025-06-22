from flask import Flask, render_template, request, jsonify
from data import Restaurant, run, wait_time_calculation
from datetime import datetime
import os

# Configure Flask to serve static files from the correct directory
app = Flask(__name__, static_url_path='', static_folder='static')
restaurant_statuses = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Get form data
            loc = request.form.get('location', '').strip()
            cuisine = request.form.get('cuisine', '').strip()
            
            if not loc:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'error': 'Location is required'}), 400
                return render_template('index.html', restaurants={}, status_data=restaurant_statuses)
            
            print(f"Getting restaurants for location: {loc}")
            
            # Get restaurant data
            restaurants = run(loc)
            print(f"Found {len(restaurants)} restaurants")
            
            # Filter by cuisine if specified
            filtered_restaurants = {}
            for name, data in restaurants.items():
                if not cuisine or cuisine.lower() == 'any' or \
                   (data.get('cuisine') and data['cuisine'].lower() == cuisine.lower()):
                    # Ensure all required fields exist
                    if 'is_open' not in data:
                        data['is_open'] = True  # Default to open if not specified
                    if 'rating' not in data:
                        data['rating'] = 0
                    if 'price_level' not in data:
                        data['price_level'] = 1
                    filtered_restaurants[name] = data
            
            print(f"After filtering: {len(filtered_restaurants)} restaurants")
            
            # Prepare response data
            response_data = {
                'success': True,
                'count': len(filtered_restaurants),
                'restaurants': filtered_restaurants
            }
            
            # Check if it's an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify(response_data)
            
            # For regular form submission (fallback)
            return render_template('index.html', 
                               restaurants=filtered_restaurants, 
                               status_data=restaurant_statuses)
            
        except Exception as e:
            print(f"Error in index route: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': str(e)}), 500
            return render_template('index.html', restaurants={}, status_data=restaurant_statuses)
    
    # GET request - show empty form
    return render_template('index.html', 
                         restaurants={}, 
                         status_data=restaurant_statuses)
    


@app.route('/business')
def business():
    return render_template('business.html')



@app.route('/update-status', methods=['POST'])
def update_status():
    data = request.get_json()
    restaurant_name = data.get('restaurant')

    if not restaurant_name:
        return jsonify({"success": False, "message": "Restaurant name required"}), 400

    status_data = {
        'employees': int(data.get('employees', 0)),
        'total_tables': int(data.get('total_tables', 0)),
        'open_tables': int(data.get('open_tables', 0)),
        'queue_length': int(data.get('queue_length', 0)),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'est-waittime': wait_time_calculation(int(data.get('employees', 0)), int(data.get('open_tables', 0)), int(data.get('total_tables', 0)), int(data.get('queue_length', 0)))
    }

    restaurant_statuses[restaurant_name] = status_data
    return jsonify({"success": True, "status": status_data})

    

@app.route('/get_status', methods=['POST'])
def get_status():
    data = request.get_json()
    restaurant_name = data.get('restaurant')
    status = restaurant_statuses.get(restaurant_name, {
        'employees': 0,
        'total_tables': 0,
        'open_tables': 0,
        'queue_length': 0,
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'est-waittime': 0
    })
    return jsonify({"success": True, "status": status})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)