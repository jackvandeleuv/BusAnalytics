import DeleteInterface
from ScrapeInterface import ScrapeInterface
from DeleteInterface import DeleteInterface
from AnalyzeInterface import AnalyzeInterface
from StatsGenerator import StatsGenerator


def main():
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
