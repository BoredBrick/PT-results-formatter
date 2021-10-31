import ctypes
import glob
import csv
import os
import sys
from student import Student


class DataProcessing:

    def get_file(self, file_type: str) -> str:
        if file_type == "results":
            file = glob.glob('*details.csv')
        elif file_type == "students":
            file = glob.glob('*comma_separated.csv')

        if len(file) == 0:
            ctypes.windll.user32.MessageBoxW(
                None, "Priečinok neobsahuje požadované súbory (zoznam študentov a výpis aktivity)", "Chyba", 0)
            sys.exit(0)
        elif len(file) > 1:
            ctypes.windll.user32.MessageBoxW(
                None, "Priečinok obsahuje viacero súborov, ktoré by mohli byť použité ako zoznam študentov alebo ako výpis aktivity.Odstráňte nepotrebné súbory.", "Chyba", 0)
            sys.exit(0)

        return file[0]  # konvertuje list na string

    def get_student_emails(self, students: list, students_file: str) -> None:
        with open(students_file, encoding='utf-8') as student_data:
            csv_reader = csv.reader(student_data)
            next(csv_reader)

            for row in csv_reader:
                full_name = (row[0] + " " + row[1]).strip()
                email = ""
                for column in row:
                    if "@" in column:
                        email = column
                        self.__map_email_to_student(students, email, full_name)

    @staticmethod
    def __map_email_to_student(students: list, email: str, name: str) -> None:
        for student in students:
            if student.full_name == name:
                student.email = email

    def extract_student_data(self, row: list, students: list, full_score: int) -> None:
        full_name = row[2].split("_")[0][1:].strip()
        temp = row[2].rsplit("_", 2)
        name_from_file = str(temp[1]).strip() + " " + str(temp[2].split(".")[0]).strip()
        packet_name = row[0].replace("_", " ").strip()
        pt_percentage = round((float(row[3]) / full_score * 100), 2)
        students.append(Student(full_name, name_from_file, packet_name, pt_percentage))

    def create_import_file(self, students: list) -> None:
        for student in students:
            if student.check_name_correctness():
                self.write_to_import_file(student, "no_errors")
            else:
                self.write_to_import_file(student, "with_errors")
                self.write_to_list_of_students_with_errors(student)

    def write_to_import_file(self, student: Student, file_type: str) -> None:
        file_name = "importBezChyb.csv" if file_type == "no_errors" else "importSChybami.csv"
        with open(file_name, "a+") as import_file:
            writer = csv.writer(import_file)
            filesize = os.path.getsize(file_name)
            if filesize == 0:
                writer.writerow(["Email", "Skore"])
            string = f'{student.email} {student.pt_percentage}'
            row = list(string.split())
            writer.writerow(row)

    def write_to_list_of_students_with_errors(self, student: Student) -> None:
        with open("Nespravne odovzdane.txt", "a+") as file:
            file.write(f'{student.full_name} odovzdal/a zadanie v PT s menom: {student.packet_name} \n')
