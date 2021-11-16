import csv  # module for csv files support
import glob  # file globbing, will find files containing given phrases
import os  # used to make directories
import sys  # exit program if one of the required files is missing
from os import path  # used to get current working directory
import configparser  # parser used to manipulate data  from settings file
import gui  # error popup windows support
from student import Student


class FileHandler:

    @staticmethod
    def get_file(file_type: str, cfg: configparser) -> str:
        """Get required file"""
        if file_type == "results":
            file = glob.glob(cfg["activity_cols"]["glob"])
        elif file_type == "students":
            file = glob.glob(cfg["stud_cols"]["glob"])
        elif file_type == "compulsory":
            file = glob.glob(cfg["compulsory_cols"]["glob"])

        if file_type != "compulsory":
            if len(file) == 0:
                gui.generic_error(
                    "Directory does not contain some of the reguired files (list of students / activity results)")
                sys.exit(0)
            elif len(file) > 1:
                gui.generic_error(
                    "Directory contains multiple files, which could be used as a "
                    "list of students or activity results. Remove unsused files.")
                sys.exit(0)

        if file_type == "compulsory" and len(file) == 0:
            return ""

        return file[0]  # convert list to string

    @staticmethod
    def create_file_comp_not_submitted(compulsory_dict: dict) -> None:
        """Creates list of students, who did not submit their compulsory homework"""
        for key, value in compulsory_dict.items():
            if not value:
                with open("results/compulsoryNotSubmitted.txt", "a+",  encoding='utf-8') as file:
                    file.write(f'{key} did not submit compulsory homework \n')

    def create_import_file(self, students: list, activity: str) -> None:
        """Deciding, which output file to use, based on correct PT name and if their
        mail has been found"""
        for student in students:
            student_has_email = student.email_found()
            student_has_correct_pt_name = student.check_name_correctness()
            if student.compulsory:
                self.write_to_compulsory_submitted(student)
            elif student_has_correct_pt_name and student_has_email:
                self.write_to_import_file(student, "importStudNoErrors.csv", activity)
                self.write_to_import_file(student, "importEveryone.csv", activity)
            elif student_has_email:  # student used incorrect name in PT
                self.write_to_import_file(student, "importStudSWithErrors.csv", activity)
                self.write_to_list_of_students_with_errors(student, "wrong_name")
                self.write_to_import_file(student, "importEveryone.csv", activity)
            else:  # program has not been able to assing mail to student
                self.write_to_list_of_students_with_errors(student, "missing_mail")

    @staticmethod
    def write_to_import_file(student: Student, file_name: str, activity: str) -> None:
        """writing to files used for moodle import"""
        file_path = f'results/{file_name}'

        with open(file_path, "a+", encoding='utf-8', newline="") as import_file:
            writer = csv.writer(import_file)
            filesize = path.getsize(file_path)
            if filesize == 0:
                writer.writerow(["Email", f'Activity: {activity}'])

            string = f'{student.email} {student.pt_percentage}'
            row = list(string.split())
            writer.writerow(row)

    @staticmethod
    def write_to_compulsory_submitted(student: Student):
        with open("results/compulsorySubmitted.txt", "a+", encoding='utf-8') as file:
            file.write(f'{student.full_name} scored {student.pt_percentage}% \n')

    @staticmethod
    def write_to_list_of_students_with_errors(student: Student, error_type: str) -> None:
        """If student is missing mail or has submitted PT activity with incorrect name,
        it will be noted in this file"""

        with open("results/studentsWithErrors.txt", "a+") as file:
            if error_type == "missing_mail":
                file.write(
                    f'Student {student.full_name}, who scored {student.pt_percentage}% has not been assigned an email \n')
            if error_type == "wrong_name":
                file.write(f'{student.full_name} submitted PT activity with username {student.packet_name} \n')

    @staticmethod
    def clear_results_file() -> None:
        """Deletes old files from results folder."""
        folder_name = "results"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        else:
            for file in os.scandir(folder_name):
                os.unlink(file.path)
