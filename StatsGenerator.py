class StatsGenerator:
    def __init__(self):
        self.__stop_filters = None
        self.__route_filters = None
        self.__day_filters = None
        self.__stop_groups = None
        self.__route_groups = None
        self.__day_groups = None

    def set_stop_filters(self, stops):
        assert type(stops) == list
        self.__stop_filters = stops

    def set_route_filters(self, routes):
        assert type(routes) == list
        self.__route_filters = routes

    def set_day_filters(self, days):
        assert type(days) == list
        self.__day_filters = days

    def set_stop_groups(self, stops):
        assert type(stops) == list
        self.__stop_groups = stops

    def set_route_groups(self, routes):
        assert type(routes) == list
        self.__route_groups = routes

    def set_day_groups(self, days):
        assert type(days) == list
        self.__day_groups = days

    def __make_where_clause(self):
        where_clause = ""
        subclauses = []

        if len(self.__stops) != 0:
            stop_in = " STOP_ID IN ("
            for i in range(len(self.__stops)):
                stop_in = stop_in + "?,"
            stop_in = stop_in[:-1] + ") "
            subclauses.append(stop_in)

        if len(self.__routes) != 0:
            route_in = " ROUTE_ID IN ("
            for i in range(len(self.__routes)):
                route_in = route_in + "?,"
            route_in = route_in[:-1] + ") "
            subclauses.append(route_in)

        if len(self.__days) != 0:
            days_in = " SUBSTR(TIME_CHECKED, 1, 10) IN ("
            for i in range(len(self.__days)):
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

        if len(self.__stop_groups) != 0:



