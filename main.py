import configparser
import gui
from data_processing import DataProcessing
from file_handler import FileHandler


def main() -> None:
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")

    data_processing = DataProcessing()
    file_handler = FileHandler()

    results_file = file_handler.get_file("results", cfg)
    data_processing.get_activity_name(results_file, cfg)
    stud_file = file_handler.get_file("students", cfg)

    gui.main_menu()
    students = []
    FULL_SCORE = gui.get_activity_max_points()

    compulsory_file = file_handler.get_file("compulsory", cfg)
    compulsory_students = data_processing.get_dict_of_compulsory(compulsory_file, cfg)

    file_handler.clear_results_file()
    data_processing.process_pt_results(results_file, students, FULL_SCORE, cfg)
    data_processing.get_and_assign_student_mails(students, stud_file, cfg)
    data_processing.mark_compulsory_students(compulsory_students, students)

    file_handler.create_import_file(students, getattr(data_processing, "activity_name"))
    file_handler.create_file_comp_not_submitted(compulsory_students)

    gui.export_successful()


if __name__ == "__main__":
    main()
