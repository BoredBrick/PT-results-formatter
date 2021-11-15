import csv  # module for csv files support
import glob  # file globbing, will find files containing given phrases
import os  # used to make directories
import sys  # exit program if one of the required files is missing
from os import path  # used to get current working directory
import configparser  # parser used to manipulate data  from settings file
import gui  # error popup windows support
from student import Student


class DataProcessing:
    """
    Class, which manages all available data - this means file with students,
    where it gets mail of each of them and then file with results itself,
    it formats everything accordingly and creates import files for moodle
    """

    def __init__(self) -> None:
        self.activity_name = ""

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
    def get_dict_of_compulsory(compulsory_file: str, cfg: configparser) -> dict:
        """
        Gets dictionary of all students for whom the activity is compulsory.
        Boolean will be used to mark students, who have submitted their activity.
        """
        name_dict = {}
        try:
            with open(compulsory_file) as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    name_column = cfg.getint("compulsory_cols", "full_name")
                    name_dict[row[name_column]] = False
            return name_dict
        except FileNotFoundError:  # return empty dict if compulsory part not used
            return name_dict

    @staticmethod
    def mark_compulsory_students(compulsory_dict: dict, students: list) -> None:
        """
        Checks list of students and marks those who have submitted their
        compulsory homework
        """
        for student in students:
            if student.full_name in compulsory_dict:
                student.compulsory = True
                compulsory_dict[student.full_name] = True

    @staticmethod
    def create_file_comp_not_submitted(compulsory_dict: dict) -> None:
        """Creates list of students, who did not submit their compulsory homework"""
        for key, value in compulsory_dict.items():
            if not value:
                with open("results/compulsoryNotSubmitted.txt", "a+",  encoding='utf-8') as file:
                    file.write(f'{key} did not submit compulsory homework \n')

    def get_activity_name(self, results_file: str, cfg: configparser):
        """
        Given column contains name of submitted file, za predpokladu
        that student has submitted file in the correct format. But I know how
        students are, so I added an extra check, which looks for two matching
        filenames.
        """
        with open(results_file) as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            UNDERSCORES_TO_FILTER = 6  # how many underscores separate activity name with date
            first_activity_check = ""
            second_activity_check = ""
            file_name_col = cfg.getint("activity_cols", "file_name")

            for row in csv_reader:
                if first_activity_check == "":
                    first_activity_check = row[file_name_col].split(
                        "/")[1].rsplit("_", UNDERSCORES_TO_FILTER)[0]
                    continue
                second_activity_check = row[file_name_col].split(
                    "/")[1].rsplit("_", UNDERSCORES_TO_FILTER)[0]
                if first_activity_check == second_activity_check:
                    self.activity_name = first_activity_check
                    break
                first_activity_check = second_activity_check
                second_activity_check = ""

            if self.activity_name == "":
                self.activity_name = "Unknown activity name"

    def get_and_assign_student_mails(self, students: list, students_file: str, cfg: configparser) -> None:
        """Iterates trought all mails and assigns one to those students, who submitted their homework"""
        with open(students_file, encoding='utf-8') as student_data:
            csv_reader = csv.reader(student_data)
            next(csv_reader)
            surname_col = cfg.getint("stud_cols", "surname")
            name_col = cfg.getint("stud_cols", "name")
            email_col = cfg.getint("stud_cols", "email")

            for row in csv_reader:
                full_name = (row[surname_col] + " " + row[name_col]).strip()
                email = row[email_col]
                self.__map_email_to_student(students, email, full_name)

    @staticmethod
    def __map_email_to_student(students: list, email: str, name: str) -> None:
        for student in students:
            if student.full_name == name:
                student.email = email

    @staticmethod
    def extract_student_data(row: list, students: list, full_score: int, cfg: configparser) -> None:
        """Getting all needed data about student and their activity from activity results file"""
        file_name_col = cfg.getint("activity_cols", "file_name")
        # the beginning of the filename contains the full name of student, [1:] removes extra space
        full_name = row[file_name_col].split("_")[0][1:].strip()
        temp = row[file_name_col].rsplit("_", 2)
        # student's name from the end of the file, currently not used
        name_from_file = str(temp[1]).strip() + " " + str(temp[2].split(".")[0]).strip()

        pt_name_col = cfg.getint("activity_cols", "pt_name")
        packet_name = row[pt_name_col].replace("_", " ").strip()

        pt_percentage_col = cfg.getint("activity_cols", "percentage")
        pt_percentage = round((float(row[pt_percentage_col]) / full_score * 100), 2)
        # If PT username is Guest, we cannot check who solved this activity, so we mark it zero
        if packet_name == "Guest" or pt_percentage < 60:
            pt_percentage = 0
        students.append(Student(full_name, name_from_file, packet_name, pt_percentage))

    def create_import_file(self, students: list) -> None:
        """Deciding, which output file to use, based on correct PT name and if their
        mail has been found"""
        for student in students:
            student_has_email = student.email_found()
            student_has_correct_pt_name = student.check_name_correctness()
            if student.compulsory:
                self.write_to_compulsory_submitted(student)
            elif student_has_correct_pt_name and student_has_email:
                self.write_to_import_file(student, "importStudNoErrors.csv")
                self.write_to_import_file(student, "importEveryone.csv")
            elif student_has_email:  # student used incorrect name in PT
                self.write_to_import_file(student, "importStudSWithErrors.csv")
                self.write_to_list_of_students_with_errors(student, "wrong_name")
                self.write_to_import_file(student, "importEveryone.csv")
            else:  # program has not been able to assing mail to student
                self.write_to_list_of_students_with_errors(student, "missing_mail")

    def write_to_import_file(self, student: Student, file__name: str) -> None:
        """writing to files used for moodle import"""
        file_path = f'results/{file__name}'

        with open(file_path, "a+", encoding='utf-8', newline="") as import_file:
            writer = csv.writer(import_file)
            filesize = path.getsize(file_path)
            if filesize == 0:
                writer.writerow(["Email", f'Activity: {self.activity_name}'])

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
    def _clear_results_file() -> None:
        """Deletes old files from results folder"""
        folder_name = "results"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        else:
            for file in os.scandir(folder_name):
                os.unlink(file.path)

    def process_pt_results(self, results_file_name: str, students: list, full_score: int, cfg: configparser) -> None:
        """Process every activity result from results file """
        self._clear_results_file()
        with open(results_file_name) as results:
            csv_reader = csv.reader(results)
            next(csv_reader)
            for row in csv_reader:
                self.extract_student_data(row, students, full_score, cfg)
