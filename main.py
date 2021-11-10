import configparser
import gui
from data_processing import DataProcessing

if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")

    dataProcessing = DataProcessing()

    results_file = dataProcessing.get_file("results", cfg)

    dataProcessing.get_activity_name(results_file, cfg)
    stud_file = dataProcessing.get_file("students", cfg)

    gui.main_menu()
    students = []
    FULL_SCORE = gui.get_activity_max_points()

    compulsory_file = dataProcessing.get_file("compulsory", cfg)
    compulsory_students = dataProcessing.get_dict_of_compulsory(compulsory_file, cfg)

    dataProcessing.process_pt_results(results_file, students, FULL_SCORE, cfg)
    dataProcessing.get_and_assign_student_mails(students, stud_file, cfg)
    dataProcessing.mark_compulsory_students(compulsory_students, students)

    dataProcessing.create_import_file(students)

    dataProcessing.create_file_comp_not_submitted(compulsory_students)
    gui.export_successful()
