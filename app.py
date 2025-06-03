from flask import Flask, render_template, request, jsonify
from data import Restaurant, run, wait_time_calculation
from datetime import datetime

app = Flask(__name__)
restaurant_statuses = {}


@app.route('/', methods=['GET', 'POST'])
def index():
    cuisine = request.form.get('cuisine', '')
    price = request.form.get('price', '')
    restaurants = {}

    if request.method == 'POST':
        loc = request.form.get('location')
        restaurants = run(loc)
        filtered_restaurants = restaurants.copy()

        if cuisine and cuisine.lower() != 'any':
            filtered_restaurants = {
                name: data for name, data in filtered_restaurants.items()
                if str(data['cuisine']).lower() == cuisine.lower()
            }

    else:
        filtered_restaurants = {}

    return render_template('index.html', restaurants=filtered_restaurants, status_data=restaurant_statuses)
    


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