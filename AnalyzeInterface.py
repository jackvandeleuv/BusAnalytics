class AnalyzeInterface:
    def __init__(self):
        pass

    # This window allows the user to explore average frequency (gap between bus arrivals) at specific stops and routes,
    # filtered by a variety of criteria selected by the user.
    @staticmethod
    def analyze_window(stat_gen):
        while True:
            user_input = input("***Calculate Frequency of Bus Arrivals***\n0) Return to main menu.\n1) Modify filters."
                               "\n2) Calculate frequencies, grouped by stop.\n3) Calculate frequencies, grouped by "
                               "routes and stops.\n4) Calculate overall average frequency.\n")

            if not user_input.isdigit():
                print("\nPlease enter an integer to select one of the menu options.\n")

            if int(user_input) == 0:
                return

            if int(user_input) == 1:
                stat_gen.print_filters()
                while True:
                    filter_choice = input("Select one of the following options:\n0) Return\n1) Add new stop filters.\n"
                                          "2) Add new route filters.\n3) Add new day filters.\n4) Delete current stop "
                                          "filters.\n5) Delete current route filters\n6) Delete current day filters.\n"
                                          "7) View current filters.\n")

                    if not filter_choice.isdigit():
                        print("\nPlease enter an integer to select one of the menu options.\n")

                    if int(filter_choice) == 0:
                        break

                    if int(filter_choice) == 1:
                        input_list = input("Enter the stops you would like to filter by separated by commas, "
                                           "e.g.: 8912, 8913, 34\n")
                        str_list = AnalyzeInterface.__process_user_input(input_list)
                        stat_gen.set_stop_filters(str_list)

                    if int(filter_choice) == 2:
                        input_list = input("Enter the routes you would like to filter by separated by commas, "
                                           "e.g.: 71A, 71C, 82\n")
                        str_list = AnalyzeInterface.__process_user_input(input_list)
                        stat_gen.set_route_filters(str_list)

                    if int(filter_choice) == 3:
                        input_list = input("Enter the dates you would like to filter by separated by commas, "
                                           "e.g.: 2022-10-31, 2022-01-01, 2021-12-15\n")
                        str_list = AnalyzeInterface.__process_user_input(input_list)
                        stat_gen.set_day_filters(str_list)

                    if int(filter_choice) == 4:
                        stat_gen.set_stop_filters([])

                    if int(filter_choice) == 5:
                        stat_gen.set_route_filters([])

                    if int(filter_choice) == 6:
                        stat_gen.set_day_filters([])

                    if int(filter_choice) == 7:
                        stat_gen.print_filters()

            if int(user_input) == 2:
                stat_gen.group_by_stop()

            if int(user_input) == 3:
                stat_gen.group_by_both()

            if int(user_input) == 4:
                stat_gen.overall_frequency()

    @staticmethod
    def __process_user_input(string):
        has_comma = "," in string
        if has_comma:
            str_list = string.split(",")
            for i in range(len(str_list)):
                str_list[i] = str_list[i].upper()
                str_list[i] = str_list[i].strip()
        if not has_comma:
            string = string.upper()
            str_list = [string.strip()]
        return str_list
