import csv
from data_processing import DataProcessing


# mozno useless
# def get_full_score(reader):
#     next(reader)
#     for row in reader:
#         scores = row[4:-1]
#         full_score = 0
#         [full_score := full_score + int(points.split("/")[1]) for points in scores]
#         break
#     print(full_score)


def process_pt_results(results_file_name: str, students: list) -> None:
    with open(results_file_name) as results:
        csv_reader = csv.reader(results)
        next(csv_reader)
        for row in csv_reader:
            dataProcessing.extract_student_data(row, students, FULL_SCORE)


if __name__ == "__main__":
    FULL_SCORE = 79
    dataProcessing = DataProcessing()
    results_file = dataProcessing.get_file("results")
    stud_file = dataProcessing.get_file("students")
    students = []
    process_pt_results(results_file, students)
    dataProcessing.get_student_emails(students, stud_file)
    dataProcessing.create_import_file(students)
