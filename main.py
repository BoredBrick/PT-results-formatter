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


if __name__ == "__main__":
    # import subprocess

    # subprocess.call(r"C:\Program Files\Cisco Packet Tracer 8.0.1\bin\PacketTracer.exe")

    FULL_SCORE = 278
    dataProcessing = DataProcessing()

    results_file = dataProcessing.get_file("results")

    dataProcessing.get_activity_name(results_file)
    stud_file = dataProcessing.get_file("students")

    students = []
    dataProcessing.process_pt_results(results_file, students, FULL_SCORE)
    dataProcessing.get_and_assign_student_mails(students, stud_file)
    dataProcessing.create_import_file(students)
