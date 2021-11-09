import csv  # modul pre prácu s csv súbormi
import glob  # globovanie súborov, aby užívateľ nemusel zadávať jeho názov
import os  # použíté pri vytváraní priečinkov
import sys  # exit systému pri chybe so súbormi
from os import path  # získanie current working directory
import configparser  # parser na získanie údajov zo settings súboru

import gui  # použité na vyskakovacie okná pri chybách
from student import Student


class DataProcessing:

    """
    Trieda, ktorá spravuje všetky dostupné dáta - to znamená súbor so študentami,
    kde získa mail každého z nich a následne samotný súbor s výsledkami,
    všetko sformátuje a vytvorí výstupy
    """

    def __init__(self) -> None:
        self.activity_name = ""

    @staticmethod
    def get_file(file_type: str, cfg: configparser) -> str:
        """getovanie súboru s výsledkami alebo so zoznamom študentov"""
        if file_type == "results":
            file = glob.glob(cfg["activity_cols"]["glob"])
        elif file_type == "students":
            file = glob.glob(cfg["stud_cols"]["glob"])

        if len(file) == 0:
            gui.generic_error("Priečinok neobsahuje požadované súbory \
                (zoznam študentov alebo výpis aktivity)")
            sys.exit(0)
        elif len(file) > 1:
            gui.generic_error(
                "Priečinok obsahuje viacero súborov, ktoré by mohli byť použité ako zoznam"
                "študentov alebo ako výpis aktivity. Odstráňte nepotrebné súbory.")
            sys.exit(0)

        return file[0]  # konvertuje list na string

    def get_activity_name(self, results_file: str, cfg: configparser):
        """
        V danom stĺpci sa nachádza cely názov odovzdaného súboru, za predpokladu
        že študent odovzdal súbor v správnom formáte. Kedže poznám študentov, tak
        som pridal kontrolu, ktorá hľadá dva za sebou zhodné názvy
        """
        with open(results_file) as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            UNDERSCORES_TO_FILTER = 6  # kolko _ oddeluje nazov aktivity a datum s menom
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
                self.activity_name = "Neznámy názov aktivity"

    def get_and_assign_student_mails(self, students: list, students_file: str, cfg: configparser) -> None:
        """Prejde množinou mailov a priradí ich študentom, ktorí odovzdali zadanie"""
        with open(students_file, encoding='utf-8') as student_data:
            csv_reader = csv.reader(student_data)
            next(csv_reader)
            surname_col = cfg.getint("stud_cols", "surname")
            name_col = cfg.getint("stud_cols", "name")
            email_col = cfg.getint("stud_cols", "name")

            for row in csv_reader:
                full_name = (row[surname_col] + " " + row[name_col]).strip()
                email = ""
                email = row[email_col]
                self.__map_email_to_student(students, email, full_name)

    @staticmethod
    def __map_email_to_student(students: list, email: str, name: str) -> None:
        for student in students:
            if student.full_name == name:
                student.email = email

    @staticmethod
    def extract_student_data(row: list, students: list, full_score: int, cfg: configparser) -> None:
        """Získanie všetkých potrebných dát zo súboru z výsledkami aktivity"""
        file_name_col = cfg.getint("activity_cols", "file_name")
        full_name = row[file_name_col].split("_")[0][1:].strip()
        temp = row[file_name_col].rsplit("_", 2)
        name_from_file = str(temp[1]).strip() + " " + str(temp[2].split(".")[0]).strip()

        pt_name_col = cfg.getint("activity_cols", "pt_name")
        packet_name = row[pt_name_col].replace("_", " ").strip()

        pt_percentage_col = cfg.getint("activity_cols", "percentage")
        pt_percentage = round((float(row[pt_percentage_col]) / full_score * 100), 2)

        if packet_name == "Guest" or pt_percentage < 60:
            pt_percentage = 0
        students.append(Student(full_name, name_from_file, packet_name, pt_percentage))

    def create_import_file(self, students: list) -> None:
        """rozhodovanie, aký výstup použiť podľa správnosti PT mena a prítomnosti mailu"""
        for student in students:
            student_has_email = student.email_found()
            student_has_correct_pt_name = student.check_name_correctness()
            if student_has_correct_pt_name and student_has_email:
                self.write_to_import_file(student, "importStudBezChyb.csv")
                self.write_to_import_file(student, "importVsetci.csv")
            elif student_has_email:  # študent uviedol nesprávne meno v aktivite
                self.write_to_import_file(student, "importStudSChybami.csv")
                self.write_to_list_of_students_with_errors(student, "wrong_name")
                self.write_to_import_file(student, "importVsetci.csv")
            else:  # nebolo možné priradiť mail ku študentovi
                self.write_to_list_of_students_with_errors(student, "missing_mail")

    def write_to_import_file(self, student: Student, file__name: str) -> None:
        """zapisovanie do samotných súborov na import"""
        file_path = f'vysledky/{file__name}'

        with open(file_path, "a+", encoding='utf-8', newline="") as import_file:
            writer = csv.writer(import_file)
            filesize = path.getsize(file_path)
            if filesize == 0:
                writer.writerow(["Email", f'Zadanie: {self.activity_name}'])

            string = f'{student.email} {student.pt_percentage}'
            row = list(string.split())
            writer.writerow(row)

    @staticmethod
    def write_to_list_of_students_with_errors(student: Student, error_type: str) -> None:
        """pri nesprávnom mene/chýbajúcom maily sa táto skutočnost zapíše do samostatného súboru"""
        with open("vysledky/Nesprávne odovzdané.txt", "a+") as file:
            if error_type == "missing_mail":
                file.write(
                    f'Študentovi {student.full_name}, ktorý/á mal/a z aktivity \
                    {student.pt_percentage}% nebolo možné priradiť email \n')
            if error_type == "wrong_name":
                file.write(f'{student.full_name} odovzdal/a zadanie \
                    v PT s menom: {student.packet_name} \n')

    @staticmethod
    def _clear_results_file() -> None:
        """vyčistí priečinok od starých súborov s výsledkami"""
        folder_name = "vysledky"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        else:
            for file in os.scandir(folder_name):
                os.unlink(file.path)

    def process_pt_results(self, results_file_name: str, students: list, full_score: int, cfg: configparser) -> None:
        """spracovanie celého súboru s výsledkami aktivity """
        self._clear_results_file()
        with open(results_file_name) as results:
            csv_reader = csv.reader(results)
            next(csv_reader)
            for row in csv_reader:
                self.extract_student_data(row, students, full_score, cfg)
