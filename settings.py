import configparser


def reset_settings(parser: configparser) -> None:

    parser.set("stud_cols", "name", "0")
    parser.set("stud_cols", "surname", "1")
    parser.set("stud_cols", "email", "5")
    parser.set("stud_cols", "glob", "*comma_separated.csv")

    parser.set("activity_cols", "pt_name", "0")
    parser.set("activity_cols", "file_name", "2")
    parser.set("activity_cols", "percentage", "3")
    parser.set("activity_cols", "glob", "*details.csv")

    with open('settings.ini', 'w') as configfile:
        parser.write(configfile)


def set_settings(parser: configparser, values: list):
    parser.set("stud_cols", "name", values[0])
    parser.set("stud_cols", "surname", values[1])
    parser.set("stud_cols", "email", values[2])
    parser.set("stud_cols", "glob", values[3])

    parser.set("activity_cols", "pt_name", values[4])
    parser.set("activity_cols", "file_name", values[5])
    parser.set("activity_cols", "percentage", values[6])
    parser.set("activity_cols", "glob", values[7])

    with open('settings.ini', 'w') as configfile:
        parser.write(configfile)
