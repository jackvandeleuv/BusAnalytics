import sqlite3
from scrape_truetime import get_stop_list

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Calling methods in this function may delete/drop any existing database with the same name in its directory!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# DB schema here: https://docs.google.com/document/d/16u6fOXoH7vvdpqc0chSfZFtU7WNWvtZJj_QmHI8KwQc/edit?usp=sharing
# Broadly, the database for this application has four tables:
#     STOPS: Basic information about all current stops offered by the TrueTime website.
#     ROUTES: Basic information about all current routes offered by the TrueTime website.
#     STOPS_ON_ROUTES: Table to link STOPS and ROUTES by primary key.
#     ESTIMATES: Each row is a snapshot of the current estimated ETAs in a specific location with each row having
#     a unique combination of bus stop, route, and time stamp.
# The methods in the CreateDB class create a SQLite3 database in the same directory.
class CreateDB:
    def __init__(self):
        pass

    # This method creates a fresh copy of transit_data.db, and then scrapes the TrueTime Pittsburgh Port Authority
    # website to find all active routes and stops that are available to scrape.
    @staticmethod
    def reset_db_with_new_stops_n_routes():
        # Create four blank tables
        CreateDB.__make_empty_tables()
        # Scrape TrueTime and fill in all the current bus routes and stops
        CreateDB.__fill_routes_and_stops()
        # Print the table schema to check that four new tables were created.
        CreateDB.__confirm_empty_table_generated()

    # Calls PRAGMA and prints meta_data about the current tables in the transit_data db.
    @staticmethod
    def __confirm_empty_table_generated():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()
        print('These tables are in the database currently:')
        cursor.execute('PRAGMA table_info(ROUTES)')
        print(cursor.fetchall())
        cursor.execute('PRAGMA table_info(STOPS)')
        print(cursor.fetchall())
        cursor.execute('PRAGMA table_info(STOPS_ON_ROUTES)')
        print(cursor.fetchall())
        cursor.execute('PRAGMA table_info(ESTIMATES)')
        print(cursor.fetchall())
        connection.commit()

    # Drop all four tables in the database and create new, empty versions.
    @staticmethod
    def __make_empty_tables():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()

        # Create ROUTES table.
        cursor.execute('DROP TABLE IF EXISTS ROUTES')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ROUTES(
        ROUTE_ID TEXT PRIMARY KEY,
        ROUTE_NAME TEXT
        )""")

        # Create STOPS table.
        cursor.execute('DROP TABLE IF EXISTS STOPS')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS STOPS(
        STOP_ID TEXT PRIMARY KEY,
        STOP_NAME TEXT,
        DIRECTION TEXT
        )""")

        # This is an intermediate table that allows us to retain knowledge about which stops are on which routes.
        # This is necessary because stops and routes have a many-to-many relationship.
        cursor.execute('DROP TABLE IF EXISTS STOPS_ON_ROUTES')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS STOPS_ON_ROUTES(
        STOP_ID TEXT NOT NULL REFERENCES STOPS(STOP_ID),
        ROUTE_ID TEXT NOT NULL REFERENCES ROUTES(ROUTE_ID),
        PRIMARY KEY (STOP_ID, ROUTE_ID)
        )""")

        # Create ESTIMATES table.
        cursor.execute('DROP TABLE IF EXISTS ESTIMATES')
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ESTIMATES(
        ID INTEGER PRIMARY KEY,
        ETA INTEGER,
        TIME_CHECKED INTEGER,
        VEHICLE_ID STRING,
        PASSENGERS STRING,
        STOP_ID INTEGER,
        ROUTE_ID TEXT,
        FOREIGN KEY (STOP_ID)
            REFERENCES STOPS(STOP_ID),
        FOREIGN KEY (ROUTE_ID)
            REFERENCES ROUTES(ROUTE_ID)
        )""")

        connection.commit()

    # This method fills in routes and stops based on TrueTime website, using the get_stop_list() method of the
    # scrape_truetime module.
    @staticmethod
    def __fill_routes_and_stops():
        # Structure of each dict in the list is {STOP_ID: [STOP_NAME, DIRECTION, ROUTE_ID, ROUTE_NAME]}
        list_of_dicts = get_stop_list()

        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()

        # This block prepares all valid route-stop combinations to be inserted into STOPS_ON_ROUTES below.
        stop_route_combo_set = set()
        for d in list_of_dicts:
            for key, value in d.items():
                stop_route_combo_set.add((key, value[2]))

        # This block prepares route_set for insertion below into ROUTES.
        route_set = set()
        for d in list_of_dicts:
            for key, value in d.items():
                route_info = (value[2], value[3])
                # Add the information we care about for the ROUTES table into a set to ensure uniqueness
                route_set.add(route_info)

        # This block prepares stop_list for insertion below into STOPS.
        stop_list = []
        stop_set = set()
        for d in list_of_dicts:
            for key, value in d.items():
                if key not in stop_set:
                    stop_list.append((key, value[0], value[1]))
                    stop_set.add(key)

        # Insert the data into the respective tables.
        cursor.executemany('INSERT INTO ROUTES VALUES(?, ?)', route_set)
        cursor.executemany('INSERT INTO STOPS VALUES(?, ?, ?)', stop_list)
        cursor.executemany('INSERT INTO STOPS_ON_ROUTES VALUES(?, ?)', stop_route_combo_set)

        connection.commit()
