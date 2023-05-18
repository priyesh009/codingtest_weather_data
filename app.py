import sqlite3
from flask import Flask, request, jsonify
# pylint: disable=E0401
from flask_swagger_ui import get_swaggerui_blueprint


app = Flask(__name__)

# Configure Swagger/OpenAPI
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': 'Weather API'}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# GET /api/weather
@app.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Retrieve weather data from the 'WeatherData' table in the 'weather_data.db' SQLite database
    based on the provided query parameters.

    Query Parameters:
    - date (str): Optional. Filter the data by a specific date.
    - station_id (str): Optional. Filter the data by a specific station ID.

    Returns:
    - JSON: Weather data as a JSON response.

    Note:
    - This function assumes the 'weather_data.db' database file exists and contains a table named 'WeatherData'.
    - The function uses the 'request.args' object to retrieve query parameters, so it should be called within
    a Flask route.
    - The returned weather data is in the form of a list of dictionaries, where each dictionary represents a
    row in the table.
    """
    with sqlite3.connect('weather_data.db', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        query_parameters = request.args
        date = query_parameters.get('date')
        station_id = query_parameters.get('station_id')

        query = "SELECT * FROM WeatherData"
        if date and station_id:
            query += f" WHERE date = {date} and station_id = {station_id}"
        elif date and not station_id:
            query += f" WHERE date = {date}"
        else:
            query += f" WHERE station_id = {station_id}"

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        weather_data = []
        for row in rows:
            weather_data.append(dict(row))

        return jsonify(weather_data)

# GET /api/weather/stats
@app.route('/api/weather/stats', methods=['GET'])
def get_weather_stats():
    """
    Retrieve weather statistics data from the 'WeatherStatistics' table in the 'weather_data.db' SQLite database
    based on the provided query parameters.

    Query Parameters:
    - date (str): Optional. Filter the data by a specific year.
    - station_id (str): Optional. Filter the data by a specific station ID.

    Returns:
    - JSON: Weather statistics data as a JSON response.

    Note:
    - This function assumes the 'weather_data.db' database file exists and contains a table named 'WeatherStatistics'.
    - The function uses the 'request.args' object to retrieve query parameters, so it should be called within
     a Flask route.
    - The returned weather statistics data is in the form of a list of dictionaries, where each dictionary represents
    a row in the table.
    """
    with sqlite3.connect('weather_data.db', uri=True) as conn:
        conn.row_factory = sqlite3.Row
        query_parameters = request.args
        date = query_parameters.get('date')
        station_id = query_parameters.get('station_id')

        query = "SELECT * FROM WeatherStatistics"

        if date and station_id:
            query += f" WHERE year = {date} and station_id = {station_id}"
        elif date and not station_id:
            query += f" WHERE year = {date}"
        else:
            query += f" WHERE station_id = {station_id}"

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        weather_stats = []
        for row in rows:
            weather_stats.append(dict(row))

        return jsonify(weather_stats)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
