import sqlite3
import glob
import time
import logging
# pylint: disable=W1203


# Set up logging
logging.basicConfig(filename='data_ingestion.log', level=logging.INFO)
logging.info(f'Data ingestion started on: {time.strftime("%Y-%m-%d %H:%M:%S")}')


# Get the list of .txt files in the specified path
file_list = glob.glob('/Users/priyesh/github/code-challenge-template/wx_data/*.txt')
# file_list = glob.glob('/Users/priyesh/github/code-challenge-template/test/*.txt')

# Connect to the SQLite database or create if it doesn't exist
# conn = sqlite3.connect('weather_data.db')
with sqlite3.connect('weather_data.db') as conn:

    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()

    # Check if the WeatherData table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='WeatherData'")
    table_exists = cursor.fetchone()

    # If the WeatherData table doesn't exist, create it
    # Using integer data type and primary key constraints for year and station_id for faster query.
    if not table_exists:
        # If the table does not exists it means we can straight away ingest the data without worrying
        # about creating duplicates.

        cursor.execute('''
            CREATE TABLE WeatherData (
                date INTEGER,
                max_temp INTEGER,
                min_temp INTEGER,
                precipitation INTEGER,
                station_id INTEGER,
                insert_date TEXT,
                PRIMARY KEY (date, station_id)
            )
        ''')
        # Create indexes for station_id and date columns
        cursor.execute('''
            CREATE INDEX idx_station_id ON WeatherData (station_id)
        ''')

        cursor.execute('''
            CREATE INDEX idx_date ON WeatherData (date)
        ''')

        # Get the current insert date
        insert_date = time.strftime("%Y-%m-%d %H:%M:%S")

        logging.info(f'Data ingestion started on: {time.strftime("%Y-%m-%d %H:%M:%S")}')

        # Track the number of records ingested
        total_records = 0

        # Process each file
        for file_path in file_list:
            # Extract the station ID from the file name. Using only the numeric part of the name for better design.
            station_id = file_path.split('/')[-1].split('.')[0][5:]
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read the lines from the file
                lines = file.readlines()

                # Process each line
                for line in lines:
                    # Split the line into columns using tab as the delimiter
                    data = line.strip().split('\t')

                    cursor.execute('''
                        INSERT INTO WeatherData (date, max_temp, min_temp, precipitation, station_id, insert_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', data + [station_id, insert_date])
                    total_records += 1

        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Data ingestion completed on: {end_time}")
        logging.info(f"Total records ingested: {total_records}")

    else:
        # If the table exists it means we need to makes sure we are not ingesting the data more than once.
        # We do it by checking for the composite keys. i.e station_id and date which uniquely identifies each row.
        # If a record comes up with these combination the we can ignore the insert.

        # Get the current insert date
        insert_date = time.strftime("%Y-%m-%d %H:%M:%S")

        # Track the number of records ingested
        total_records = 0

        # Process each file
        for file_path in file_list:
            # Extract the station ID from the file name. Using only the numeric part of the name for better design.
            station_id = file_path.split('/')[-1].split('.')[0][5:]
            print(station_id)
            with open(file_path, 'r', encoding='utf-8') as file:
                # Read the lines from the file
                lines = file.readlines()

                # Process each line
                for line in lines:
                    # Split the line into columns using tab as the delimiter
                    data = line.strip().split('\t')

                    # Check if the data already exists in the table
                    cursor.execute('''
                        SELECT COUNT(*) FROM WeatherData
                        WHERE date = ? AND station_id = ?
                    ''', (data[0], station_id))
                    count = cursor.fetchone()[0]

                    # If the data doesn't exist, insert it into the WeatherData table
                    if count == 0:
                        cursor.execute('''
                            INSERT INTO WeatherData (date, max_temp, min_temp, precipitation, station_id, insert_date)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', data + [station_id, insert_date])
                        total_records += 1

        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Data ingestion completed on: {end_time}")
        logging.info(f"Total records ingested: {total_records}")

    # Analysis

    # Create the WeatherStatistics table if it doesn't exist
    # Using integer data type and primary key constraints for year and station_id for faster query.
    logging.info(f'Data ingestion started for WeatherStatistics on: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS WeatherStatistics (
            year INTEGER,
            station_id INTEGER,
            avg_max_temp DECIMAL(7, 3),
            avg_min_temp DECIMAL(7, 3),
            total_precipitation DECIMAL(7, 3),
            PRIMARY KEY (year, station_id)
        )
    ''')
    # Create indexes for station_id and year columns
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_station_id_stat ON WeatherStatistics (station_id)
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_year_stat ON WeatherStatistics (year)
    ''')

    # Calculate and store the statistics for each year and station
    logging.info(f'Data ingestion started for WeatherStatistics on: {time.strftime("%Y-%m-%d %H:%M:%S")}')

    # The SQL code calculates the average maximum temperature, average minimum temperature,
    # and total precipitation for each unique combination of year and station ID in the WeatherData table.
    # It then inserts these calculated values into the WeatherStatistics table, ignoring any duplicates.

    cursor.execute('''
        INSERT OR IGNORE INTO WeatherStatistics (year, station_id, avg_max_temp, avg_min_temp, total_precipitation)
        SELECT 
            SUBSTR(CAST(date AS TEXT),1,4)AS year,
            station_id,
            ROUND(AVG(max_temp), 3) AS avg_max_temp,
            ROUND(AVG(min_temp), 3) AS avg_min_temp,
            ROUND(SUM(precipitation), 3) AS total_precipitation
        FROM WeatherData
        WHERE max_temp IS NOT NULL AND min_temp IS NOT NULL AND precipitation IS NOT NULL
        GROUP BY year, station_id
    ''')

    logging.info(f'Data ingestion completed for WeatherStatistics on: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    conn.commit()
