import configparser
import gui
from data_processing import DataProcessing

if __name__ == "__main__":
    # import subprocess

    # subprocess.call(r"C:\Program Files\Cisco Packet Tracer 8.0.1\bin\PacketTracer.exe")
    cfg = configparser.ConfigParser()
    cfg.read("settings.ini")

    dataProcessing = DataProcessing()

    results_file = dataProcessing.get_file("results", cfg)

    dataProcessing.get_activity_name(results_file, cfg)
    stud_file = dataProcessing.get_file("students", cfg)

    gui.main_menu()
    students = []
    FULL_SCORE = gui.get_activity_max_points()
    dataProcessing.process_pt_results(results_file, students, FULL_SCORE, cfg)
    dataProcessing.get_and_assign_student_mails(students, stud_file, cfg)
    dataProcessing.create_import_file(students)

    gui.export_successful()
