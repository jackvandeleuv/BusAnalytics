import sqlite3


# This class is used to delete records from the ESTIMATES table based on stops, lines, or dates. The user can only
# select of these delete-by criteria at a time.
class DeleteDBRecords:
    def __init__(self):
        pass

    @staticmethod
    def delete_by_stops(stops):
        assert type(stops) == list

        # Validate input inside inputted lists.
        for stop in stops:
            assert type(stop[0]) == str

        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()

        # Delete all rows matching our where clause.
        delete_query = "DELETE FROM ESTIMATES WHERE STOP_ID = ?"
        cur.executemany(delete_query, stops)

        connection.commit()

    @staticmethod
    def delete_by_lines(lines):
        assert type(lines) == list

        # Validate input inside inputted lists.
        for line in lines:
            assert type(line[0]) == str

        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()

        # Delete all rows matching our where clause.
        delete_query = "DELETE FROM ESTIMATES WHERE ROUTE_ID = ?"
        cur.executemany(delete_query, lines)

        connection.commit()

    @staticmethod
    def delete_by_dates(dates):
        assert type(dates) == list

        # Validate input inside inputted lists.
        for date in dates:
            assert type(date[0]) == str

        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()

        # Delete all rows matching our where clause.
        delete_query = "DELETE FROM ESTIMATES WHERE SUBSTR(TIME_CHECKED, 1, 10) = ?"
        cur.executemany(delete_query, dates)

        connection.commit()
