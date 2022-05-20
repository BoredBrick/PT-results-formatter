import csv  # module for csv files support
import configparser  # parser used to manipulate data  from settings file
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

    def get_activity_name(self, results_file: str, cfg: configparser):
        """
        Given column contains name of submitted file, za predpokladu
        that student has submitted file in the correct format. But I know how
        students are, so I added an extra check, which looks for two matching
        filenames.
        """
        with open(results_file, encoding='ansi') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            UNDERSCORES_TO_FILTER = 6  # how many underscores separate activity name with date
            first_activity_check = ""
            second_activity_check = ""
            file_name_col = cfg.getint("activity_cols", "file_name")

            for row in csv_reader:
                try:
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
                except:
                    continue

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
                full_name = (row[name_col] + " " + row[surname_col]).strip()
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
        # If PT username is Guest, we cannot check who solved this activity, so we mark it 0
        cfg = configparser.ConfigParser()
        cfg.read("settings.ini")
        if packet_name == "Guest" or (cfg["stud_cols"].getboolean('check60percent') and pt_percentage < 60):
            pt_percentage = 0
        students.append(Student(full_name, name_from_file, packet_name, pt_percentage))

    def process_pt_results(self, results_file_name: str, students: list, full_score: int, cfg: configparser) -> None:
        """Process every activity result from results file """
        with open(results_file_name, encoding='ansi') as results:
            csv_reader = csv.reader(results)
            next(csv_reader)
            for row in csv_reader:
                self.extract_student_data(row, students, full_score, cfg)
