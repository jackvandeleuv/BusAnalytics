from Interface import Interface


def main():
    interface = Interface()
    quit_request = False
    while not quit_request:
        main_select = input("""***Main Menu***\n
                                0) Quit
                                1) Scrape new data\n
                                2) Delete existing data\n
                                3) Analyse existing data\n""")

        if not main_select.isdigit():
            print("Please enter an integer to select one of the menu options.\n")

        if int(main_select) == 0:
            quit_request = True

        if int(main_select) == 1:
            quit_request = interface.scrape_window()

        if int(main_select) == 2:
            quit_request = interface.delete_data_window()

        if int(main_select) == 3:
            quit_request = interface.get_avg_frequency_by_criteria()


if __name__ == '__main__':
    main()
