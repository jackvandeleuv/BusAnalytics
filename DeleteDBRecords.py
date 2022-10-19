import sqlite3

# This class is used to delete records from the ESTIMATES table based on stops, lines, or dates. The user can only
# select of these delete-by criteria at a time.
class DeleteDBRecords:
    def __init__(self):
        pass

    # Input must be three lists. The lists can either be empty (indicating that we will not filter by that criteria),
    # or they can be lists of strings.
    @staticmethod
    def delete_by_criteria(stops, lines, dates):
        # Validate input.
        assert type(stops) == list
        assert type(lines) == list
        assert type(dates) == list

        where_clause = ''

        # Validate input inside inputted lists.
        for stop in stops:
            assert type(stop) == str

        for line in lines:
            assert type(line) == str

        for date in dates:
            assert type(date) == str

        # If the function was called with a non-empty stops list, process the received stops into a WHERE clause for
        # our SQL query.
        if len(stops) != 0:
            stops_str = ",".join(stops)
            where_clause = " WHERE STOP_ID IN (" + stops_str + ")"

        # If the function was called with a non-empty lines list, process the received lines into a WHERE clause for
        # our SQL query.
        if len(lines) != 0:
            lines_str = "','".join(lines)
            where_clause = " WHERE ROUTE_ID IN ('" + lines_str + "')"

        # If the function was called with a non-empty dates list, process the received dates into a WHERE clause for
        # our SQL query.
        if len(dates) != 0:
            dates_str = "','".join(dates)
            # Filtering by substring will allow us to compare the time stamps in TIME_CHECKED directly with the incoming
            # dates, which are formatted like '2022-10-10'
            where_clause = " WHERE SUBSTR(TIME_CHECKED, 1, 10) IN ('" + dates_str + "')"

        connection = sqlite3.Connection('transit_data.db')
        cur = connection.cursor()

        # Delete all rows matching our where clauses, which filters either by stops, routes, or dates.
        delete_query = "DELETE FROM ESTIMATES" + where_clause
        cur.execute(delete_query)

        connection.commit()