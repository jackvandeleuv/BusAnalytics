import sqlite3
from datetime import datetime


class StatsGenerator:
    def __init__(self):
        self.__stop_filters = []
        self.__route_filters = []
        self.__day_filters = []
        self.__group_stops = False
        self.__group_routes = False
        self.__group_days = False

    def set_stop_filters(self, stops):
        assert type(stops) == list
        self.__stop_filters = stops

    def set_route_filters(self, routes):
        assert type(routes) == list
        self.__route_filters = routes

    def set_day_filters(self, days):
        assert type(days) == list
        self.__day_filters = days

    def set_stop_group(self, boolean):
        self.__group_stops = boolean

    def set_route_group(self, boolean):
        self.__group_routes = boolean

    def set_day_group(self, boolean):
        self.__group_days = boolean

    def __make_where_clause(self):
        where_clause = ""
        subclauses = []

        if len(self.__stop_filters) != 0:
            stop_in = " STOP_ID IN ("
            for i in range(len(self.__stop_filters)):
                stop_in = stop_in + "?,"
            stop_in = stop_in[:-1] + ") "
            subclauses.append(stop_in)

        if len(self.__route_filters) != 0:
            route_in = " ROUTE_ID IN ("
            for i in range(len(self.__route_filters)):
                route_in = route_in + "?,"
            route_in = route_in[:-1] + ") "
            subclauses.append(route_in)

        if len(self.__day_filters) != 0:
            days_in = " SUBSTR(TIME_CHECKED, 1, 10) IN ("
            for i in range(len(self.__day_filters)):
                days_in = days_in + "?,"
            days_in = days_in[:-1] + ") "
            subclauses.append(days_in)

        if len(subclauses) == 1:
            where_clause = "WHERE" + subclauses[0]

        if len(subclauses) > 1:
            subclauses = "AND".join(subclauses)
            where_clause = "WHERE" + subclauses

        return where_clause

    def make_group_clause(self):
        group_clause = ""
        subclauses = []

        if self.__group_stops:
            stop_g = "STOP_ID"
            subclauses.append(stop_g)

        if self.__group_routes:
            route_g = "ROUTE_ID"
            subclauses.append(route_g)

        if self.__group_days:
            day_g = "SUBSTR(TIME_CHECKED, 1, 10)"
            subclauses.append(day_g)

        if len(subclauses) != 0:
            subclauses = ", ".join(subclauses)
            group_clause = "GROUP BY " + subclauses

        print(group_clause)

    def get_scrape_ids(self, cur):
        cur.execute("SELECT DISTINCT(SCRAPE_ID) FROM ESTIMATES")
        scrape_ids = cur.fetchall()
        return scrape_ids

    def calc_frequency(self):
        conn = sqlite3.Connection("transit_data.db")
        cur = conn.cursor()
        scrape_ids = self.get_scrape_ids(cur)
        for id in scrape_ids:
            cur.execute("""
            SELECT ETA, TIME_CHECKED, VEHICLE_ID, STOP_ID
            FROM ESTIMATES
            WHERE SCRAPE_ID = ?
            ORDER BY STOP_ID
            """, id)
            estimates = cur.fetchall()
            for estimate in estimates:
                print(estimate)

        conn.commit()

    def query_test(self):
        conn = sqlite3.Connection("transit_data.db")
        cur = conn.cursor()

        cur.execute("""
        SELECT SCRAPE_ID, MIN(TIME_CHECKED), MAX(TIME_CHECKED)
        FROM ESTIMATES
        WHERE SCRAPE_ID = 1665243291.0
        """)
        results = cur.fetchall()
        for r in results:
            print(r)

        conn.commit()


sg = StatsGenerator()
sg.query_test()
