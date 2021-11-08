import ctypes  # použité na vyskakovacie okná pri chybách
import glob  # globovanie súborov, aby užívateľ nemusel zadávať jeho názov
import csv  # modul pre prácu s csv súbormi
from os import path  # získanie current working directory
import os
import sys  # exit systému pri chybe so súbormi
from student import Student


class DataProcessing:

    def __init__(self) -> None:
        self.activity_name = ""

    # getovanie súboru s výsledkami alebo so zoznamom študentov
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

    # v treťom stĺpci sa nachádza cely názov odovzdaného súboru, z neho dostanem názov aktivity
    # prehľadáva sa tretí stĺpec, pokiaľ sa nenájdu dve zhody po sebe (pre prípad, že by niekto odovzdal súbor so zlým formátom názvu)
    def get_activity_name(self, results_file):
        with open(results_file) as file:
            csv_reader = csv.reader(file)
            next(csv_reader)
            UNDERSCORES_TO_FILTER = 6  # kolko _ oddeluje nazov aktivity a datum s menom
            first_name = ""
            second_name = ""

            for row in csv_reader:
                if first_name == "":
                    first_name = row[2].split("/")[1].rsplit("_", UNDERSCORES_TO_FILTER)[0]
                    continue
                second_name = row[2].split("/")[1].rsplit("_", UNDERSCORES_TO_FILTER)[0]
                if first_name == second_name:
                    self.activity_name = first_name
                    break
                first_name = second_name
                second_name = ""

            if self.activity_name == "":
                self.activity_name = "Neznámy názov aktivity"

    def get_and_assign_student_mails(self, students: list, students_file: str) -> None:
        with open(students_file, encoding='utf-8') as student_data:
            csv_reader = csv.reader(student_data)
            next(csv_reader)

            # nájdenie mena a stĺpca, ktorý obsahuje zavináč - čiže mail
            for row in csv_reader:
                full_name = (row[1] + " " + row[0]).strip()
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

    # získanie informácií o študentovi - meno, meno v PT, výsledok aktivity
    @staticmethod
    def extract_student_data(row: list, students: list, full_score: int) -> None:
        full_name = row[2].split("_")[0][1:].strip()
        temp = row[2].rsplit("_", 2)
        name_from_file = str(temp[1]).strip() + " " + str(temp[2].split(".")[0]).strip()
        packet_name = row[0].replace("_", " ").strip()
        pt_percentage = round((float(row[3]) / full_score * 100), 2)

        if packet_name == "Guest" or pt_percentage < 60:
            pt_percentage = 0
        students.append(Student(full_name, name_from_file, packet_name, pt_percentage))

    # zapisovanie výsledok do súboru na import podľa toho, či má správne meno v PT

    def create_import_file(self, students: list) -> None:
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

    # zapisovanie do samotných súborov na import

    def write_to_import_file(self, student: Student, file__name: str) -> None:

        file_path = f'vysledky/{file__name}'

        with open(file_path, "a+", encoding='utf-8', newline="") as import_file:
            writer = csv.writer(import_file)
            filesize = path.getsize(file_path)
            if filesize == 0:
                writer.writerow(["Email", f'Zadanie: {self.activity_name}'])

            string = f'{student.email} {student.pt_percentage}'
            row = list(string.split())
            writer.writerow(row)

    # pri nesprávnom mene sa táto skutočnost zapíše do samostatného súboru

    def write_to_list_of_students_with_errors(self, student: Student, error_type: str) -> None:
        with open("vysledky/Nesprávne odovzdané.txt", "a+") as file:
            if error_type == "missing_mail":
                file.write(
                    f'Študentovi {student.full_name}, ktorý/á mal/a z aktivity {student.pt_percentage}% nebolo možné priradiť email')
            if error_type == "wrong_name":
                file.write(f'{student.full_name} odovzdal/a zadanie v PT s menom: {student.packet_name} \n')

    # vyčistí priečinok od starých súborov s výsledkami
    @staticmethod
    def _clear_results_file() -> None:
        folder_name = "vysledky"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        else:
            for file in os.scandir(folder_name):
                os.unlink(file.path)

    # spracovanie celého súboru s výsledkami aktivity
    def process_pt_results(self, results_file_name: str, students: list, full_score: int) -> None:
        self._clear_results_file()
        with open(results_file_name) as results:
            csv_reader = csv.reader(results)
            next(csv_reader)
            for row in csv_reader:
                self.extract_student_data(row, students, full_score)
