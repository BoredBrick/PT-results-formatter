import configparser


def reset_settings(parser: configparser) -> None:
    """Reset values to their default values."""
    def_values = ["0", "1", "5", "*comma_separated.csv", True, "0", "2", "3", "*details.csv", "1", "*povinne.csv"]
    set_settings(parser, def_values)


def set_settings(parser: configparser, values: dict) -> None:
    parser.set("stud_cols", "name", values[0])
    parser.set("stud_cols", "surname", values[1])
    parser.set("stud_cols", "email", values[2])
    parser.set("stud_cols", "glob", values[3])
    parser.set("stud_cols", "check60percent", str(values[4]))

    parser.set("activity_cols", "pt_name", values[5])
    parser.set("activity_cols", "file_name", values[6])
    parser.set("activity_cols", "percentage", values[7])
    parser.set("activity_cols", "glob", values[8])

    values[9] = "1"
    values[10] = "*compulsoryStudents.csv"

    parser.set("compulsory_cols", "full_name", values[9])
    parser.set("compulsory_cols", "glob", values[10])

    with open('settings.ini', 'w') as configfile:
        parser.write(configfile)
