import sqlite3


# This class allows us to make basic queries from our database to assist various parts of the application.
class QueryDB:
    # Returns all routes contained in the ROUTES table. This should be every route listed on the TrueTime website.
    @staticmethod
    def get_available_routes():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()
        cursor.execute('SELECT ROUTE_ID, ROUTE_NAME FROM ROUTES')
        available_routes = cursor.fetchall()
        connection.commit()

        return available_routes

    # Get only those routes for which we have scraped ETA data.
    @staticmethod
    def get_scraped_routes():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT(ROUTE_ID) FROM ESTIMATES')
        scraped_routes = cursor.fetchall()
        connection.commit()

        return scraped_routes

    # Get only those stops for which we have scraped ETA data.
    @staticmethod
    def get_scraped_stops():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()
        # SELECT both stops and routes, so that they can be combined together and returned.
        cursor.execute("SELECT DISTINCT(STOP_ID), ROUTES.ROUTE_ID FROM ESTIMATES "
                       "JOIN STOPS_ON_ROUTES USING(STOP_ID) "
                       "JOIN ROUTES USING(ROUTE_ID)"
                       "ORDER BY ROUTES.ROUTE_ID DESC")
        results = cursor.fetchall()
        connection.commit()

        scraped_stops = {}
        # Insert the distinct stop IDs and routes into a dict.
        for i in range(len(results)):
            stop = results[i][0]
            route = results[i][1]
            scraped_stops[stop] = route

        return scraped_stops

    # Get only those stops which we have ETA data for and that match a particular route (which should be a single str).
    @staticmethod
    def get_scraped_stops_based_on_route(route):
        assert type(route) == str

        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()

        cursor.execute("SELECT STOP_ID, STOP_NAME "
                       "FROM STOPS JOIN ESTIMATES USING(STOP_ID) "
                       "WHERE ROUTE_ID = ? "
                       "GROUP BY STOP_ID, STOP_NAME ORDER BY STOP_NAME", (route,))
        scraped_stops = cursor.fetchall()

        for i in range(len(scraped_stops)):
            # Pull out each individual stop_id/stop_name combo and turn the two-tuple into a list.
            scraped_stop_list = list(scraped_stops[i])
            # Convert each stop id into an int
            scraped_stop_list[0] = int(scraped_stop_list[0])
            # Insert the new list back into the data.
            scraped_stops[i] = scraped_stop_list

        connection.commit()

        return scraped_stops

    # Get all dates for which we have scraped ETA data. Each date is a str, formatted like '2022-10-10'.
    @staticmethod
    def get_scraped_days():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT(SUBSTR(TIME_CHECKED, 1, 10)) AS days FROM ESTIMATES ORDER BY days DESC')
        scraped_days = cursor.fetchall()
        connection.commit()

        for i in range(len(scraped_days)):
            day = scraped_days[i]
            scraped_days[i] = day[0]

        return scraped_days

    # Return a single tuple, containing the count of all the rows in our ESTIMATES table.
    @staticmethod
    def count_estimates():
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(ID) FROM ESTIMATES')
        estimate_count = cursor.fetchall()
        connection.commit()

        return estimate_count

    # Function to make quick queries for debugging.
    @staticmethod
    def test_data():
        # Here's the boilerplate code needed to query the database.
        connection = sqlite3.Connection('transit_data.db')
        cursor = connection.cursor()

        # Count the primary keys in the ESTIMATES table.
        cursor.execute("""SELECT COUNT(ID) FROM ESTIMATES""")

        results = cursor.fetchall()
        for r in results:
            print(r)

        connection.commit()
