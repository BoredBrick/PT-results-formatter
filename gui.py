import configparser
import sys
import PySimpleGUI as sg
import settings


def main_menu() -> None:
    """Main menu graphics, which is launched right after program launch"""
    sg.theme('DarkAmber')
    layout = [[sg.Button("Start"), sg.Button("Settings"), sg.Button("About"), sg.Exit("Exit")]]

    window = sg.Window("Main menu", layout, no_titlebar=True, grab_anywhere=True, keep_on_top=True, scaling=2)
    while True:
        event, _values = window.read()
        if event == "Exit":
            sys.exit(0)
        elif event == "Start":
            break
        elif event == "About":
            sg.PopupOK("Application used for processing results from PT's activity grader "
                       "into format, which allows their simple mass import into moodle \n"
                       "Made as a part of bachelor's thesis: ",
                       " \"Automation of processes when using UNIZA e-vzdelavanie system and LMS Moodle\" ",
                       "Daniel Caban 2021/2022",
                       no_titlebar=True, grab_anywhere=True, keep_on_top=True)
        elif event == "Settings":
            edit_settings()
    window.close()


def edit_settings() -> None:
    """
    Menu, where user can edit which column in csv files contains required data
    + globbing of said files. Made for future proofing.
    """
    sg.theme('DarkAmber')
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")

    column1 = [[sg.Text('File with student data')],
               [sg.Text('Name', size=(10, 1)), sg.Input(cfg["stud_cols"]["name"], size=(10, 1))],
               [sg.Text('Surname', size=(10, 1)), sg.Input(cfg["stud_cols"]["surname"], size=(10, 1))],
               [sg.Text('Email', size=(10, 1)), sg.Input(cfg["stud_cols"]["email"], size=(10, 1))],
               [sg.Text('Glob', size=(10, 1)), sg.Input(cfg["stud_cols"]["glob"], size=(10, 1))]]

    column2 = [[sg.Text('File with PT activity results')],
               [sg.Text('PT name',  size=(10, 1)), sg.Input(
                   cfg["activity_cols"]["pt_name"], size=(10, 1))],
               [sg.Text('File name',  size=(10, 1)), sg.Input(
                   cfg["activity_cols"]["file_name"], size=(10, 1))],
               [sg.Text('Result', size=(10, 1)), sg.Input(
                   cfg["activity_cols"]["percentage"], size=(10, 1))],
               [sg.Text('Glob', size=(10, 1)), sg.Input(cfg["activity_cols"]["glob"], size=(10, 1))]]

    layout = [[sg.Column(column1), sg.Column(column2)],
              [sg.Button("Ok", size=(10, 1)), sg.Button("Reset", size=(10, 1)), sg.Button("Exit", size=(10, 1))]]
    window = sg.Window("Settings", layout, no_titlebar=True, grab_anywhere=True, keep_on_top=True)

    event, values = window.read()
    if event == "Ok":
        settings.set_settings(cfg, values)
    elif event == "Reset":
        settings.reset_settings(cfg)
        window.close()
        edit_settings()
    elif event == "Exit":
        pass
    window.close()


def get_activity_max_points() -> int:
    """Asks user for maximum points from current activity"""
    while True:
        sg.theme('DarkAmber')

        layout = [[sg.Text('Input max points from PT activity')],
                  [sg.InputText()],
                  [sg.Submit("Ok"), sg.Cancel("Exit")]]

        window = sg.Window("Max points", layout, no_titlebar=True, grab_anywhere=True, keep_on_top=True)

        event, values = window.read()
        window.close()
        if event == "Exit":
            sys.exit(0)
        try:
            return int(values[0])
        except ValueError:
            sg.popup_error("An integer is required", grab_anywhere=True, no_titlebar=True)


def generic_error(message: str) -> None:
    sg.theme('DarkAmber')
    sg.popup_error(f'{message}', no_titlebar=True)


def export_successful() -> None:
    sg.theme('DarkAmber')
    sg.PopupOK("All files have been successfully created", grab_anywhere=True, no_titlebar=True)
