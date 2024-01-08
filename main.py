from scr.Menu import Menu

def main():
    menu = Menu()

    while True:
        menu.show_menu()
        option = input("Seleccione una opción: ")
        menu.execute_option(option)

if __name__ == "__main__":
    main()
