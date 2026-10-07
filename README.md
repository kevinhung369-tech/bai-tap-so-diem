## 1. Kết quả lệnh `flask --app sodiem routes`
Endpoint            Methods                 Rule
------------------  ----------------------  -------------------------------------------
api_student_detail  GET                     /api/students/<mssv>
api_student_score   DELETE, GET, POST, PUT  /api/students/<mssv>/scores/<course>
api_students        GET                     /api/students
export_csv          GET                     /students/<mssv>/export
index               GET                     /
search              GET                     /search
short_link          GET                     /sv/<mssv>
static              GET                     /static/<path:filename>
student_detail      GET                     /students/<mssv>
student_list        GET                     /students