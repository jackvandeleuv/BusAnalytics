import DeleteInterface
from ScrapeInterface import ScrapeInterface
from DeleteInterface import DeleteInterface
from AnalyzeInterface import AnalyzeInterface
from StatsGenerator import StatsGenerator
from CreateDB import CreateDB
from os import path


def new_install_window():
    user_input = input("Welcome to BusAnalytics. Your database is currently empty. To start using this program select "
                       "option 1) which will pull an updated list of routes and stops from the Pittsburgh Port "
                       "Authority's TrueTime API.\n0) Exit\n1) Generate database with new routes and stops.\n")

    if not user_input.isdigit():
        print("Please enter an integer to select one of the menu options.\n")

    if int(user_input) == 0:
        return

    if int(user_input) == 1:
        print("Downloading information from TrueTime...\n")
        CreateDB.recreate_db_with_new_stops_n_routes()


def main():
    if not path.exists("transit_data.db"):
        new_install_window()

    if path.exists("transit_data.db"):
        stat_gen = StatsGenerator()
        while True:
            main_select = input("***Main Menu***\n0) Quit.\n1) Scrape new data.\n2) Delete existing data.\n"
                                "3) Analyse existing data.\n")

            if not main_select.isdigit():
                print("Please enter an integer to select one of the menu options.\n")

            if int(main_select) == 0:
                break

            if int(main_select) == 1:
                ScrapeInterface.scrape_window()

            if int(main_select) == 2:
                DeleteInterface.delete_window()

            if int(main_select) == 3:
                AnalyzeInterface.analyze_window(stat_gen)


if __name__ == '__main__':
    main()
