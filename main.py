from ScrapeWindow import ScrapeWindow


def main():
    while True:
        main_select = input("***Main Menu***\n0) Quit.\n1) Scrape new data.\n2) Delete existing data.\n"
                            "3) Analyse existing data.\n")

        if not main_select.isdigit():
            print("Please enter an integer to select one of the menu options.\n")

        if int(main_select) == 0:
            break

        if int(main_select) == 1:
            ScrapeWindow.scrape_window()

        if int(main_select) == 2:
            interface.delete_window()

        if int(main_select) == 3:
            interface.analyze_window()


if __name__ == '__main__':
    main()
