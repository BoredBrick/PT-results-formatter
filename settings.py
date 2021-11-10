import configparser


def reset_settings(parser: configparser) -> None:
    """Reset údajov na pôvodné odskúšané hodnoty"""
    def_values = ["0", "1", "5", "*comma_separated.csv", "0", "2", "3", "*details.csv", "1", "*povinne.csv"]
    set_settings(parser, def_values)


def set_settings(parser: configparser, values: dict):
    parser.set("stud_cols", "name", values[0])
    parser.set("stud_cols", "surname", values[1])
    parser.set("stud_cols", "email", values[2])
    parser.set("stud_cols", "glob", values[3])

    parser.set("activity_cols", "pt_name", values[4])
    parser.set("activity_cols", "file_name", values[5])
    parser.set("activity_cols", "percentage", values[6])
    parser.set("activity_cols", "glob", values[7])

    values[8] = "1"
    values[9] = "*povinne.csv"

    parser.set("compulsory_cols", "full_name", values[8])
    parser.set("compulsory_cols", "glob", values[9])

    with open('settings.ini', 'w') as configfile:
        parser.write(configfile)
