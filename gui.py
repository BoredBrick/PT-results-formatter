import configparser
import sys  # exit systému
import PySimpleGUI as sg
import settings


def main_menu() -> None:
    """Grafika pre hlavné menu, ktoré sa otvorí po spustení"""
    sg.theme('DarkAmber')
    layout = [[sg.Button("Štart"), sg.Button("Nastavenia"), sg.Button("O programe"), sg.Exit("Koniec")]]

    window = sg.Window("Main menu", layout, no_titlebar=True, keep_on_top=True)
    while True:
        event, _values = window.read()
        if event == "Koniec":
            sys.exit(0)
        elif event == "Štart":
            break
        elif event == "O programe":
            sg.PopupOK("Program na spracovanie výsledkov z PT aktivít do formátu,\
                ktorý umožňuje ich jednoduchý import na moodle\n",
                       "Vytvorené v rámci bakalárskej práce: ",
                       " \"Zvýšenie automatizácie v procesoch pri využívaní systému e-vzdelávanie a LMS Moodle\" ",
                       "Daniel Caban 2021/2022",
                       no_titlebar=True, keep_on_top=True)
        elif event == "Nastavenia":
            edit_settings()
    window.close()


def edit_settings() -> None:
    """
    Ponuka, kde je možnosť upraviť, v ktorých stĺpcoch sa nachádzajú
    požadované dáta + globovanie súborov, pre prípad, že by sa do budúcna
    zmenil formát niektorých z týchto dokumentov
    """
    sg.theme('DarkAmber')
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")

    column1 = [[sg.Text('Súbor s údajmi študentov')],
               [sg.Text('Meno', size=(10, 1)), sg.Input(cfg["stud_cols"]["name"], size=(10, 1))],
               [sg.Text('Priezvisko', size=(10, 1)), sg.Input(cfg["stud_cols"]["surname"], size=(10, 1))],
               [sg.Text('Email', size=(10, 1)), sg.Input(cfg["stud_cols"]["email"], size=(10, 1))],
               [sg.Text('Glob', size=(10, 1)), sg.Input(cfg["stud_cols"]["glob"], size=(10, 1))]]

    column2 = [[sg.Text('Súbor s výsledkami aktivít')],
               [sg.Text('Meno z PT',  size=(10, 1)), sg.Input(
                   cfg["activity_cols"]["pt_name"], size=(10, 1))],
               [sg.Text('Názov súboru',  size=(10, 1)), sg.Input(
                   cfg["activity_cols"]["file_name"], size=(10, 1))],
               [sg.Text('Výsledok', size=(10, 1)), sg.Input(
                   cfg["activity_cols"]["percentage"], size=(10, 1))],
               [sg.Text('Glob', size=(10, 1)), sg.Input(cfg["activity_cols"]["glob"], size=(10, 1))]]

    layout = [[sg.Column(column1), sg.Column(column2)],
              [sg.Button("Ok", size=(10, 1)), sg.Button("Reset", size=(10, 1)), sg.Button("Zruš", size=(10, 1))]]
    window = sg.Window("Settings", layout, no_titlebar=True, keep_on_top=True)

    event, values = window.read()
    if event == "Ok":
        settings.set_settings(cfg, values)
    elif event == "Reset":
        settings.reset_settings(cfg)
        window.close()
        edit_settings()
    elif event == "Zruš":
        pass
    window.close()


def get_activity_max_points() -> int:
    """Užívateľ zadá maximálny počet bodov z aktivity"""
    while True:
        sg.theme('DarkAmber')

        layout = [[sg.Text('Zadaj maximálny počete bodov z aktivity')],
                  [sg.InputText()],
                  [sg.Submit("Ok"), sg.Cancel("Koniec")]]

        window = sg.Window("Max points", layout, no_titlebar=True, keep_on_top=True)

        event, values = window.read()
        window.close()
        if event == "Koniec":
            sys.exit(0)
        try:
            return int(values[0])
        except ValueError:
            sg.popup_error("Je potrebné zadať celé číslo", no_titlebar=True)


def generic_error(message: str) -> None:
    sg.theme('DarkAmber')
    sg.popup_error(f'{message}', no_titlebar=True)


def export_successful() -> None:
    sg.theme('DarkAmber')
    sg.PopupOK("Súbory na import boli úspešne vytvorené", no_titlebar=True)
