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
## 2. Kết quả kiểm thử curl
- `curl -i $B/sv/23T1020001` -> Trả về `HTTP/1.1 301 MOVED PERMANENTLY` kèm header `Location: /students/23T1020001`.
- `curl -i $B/students/23T1020001/export` -> Trả về `HTTP/1.1 200 OK` kèm file CSV.
- `curl -i "$B/api/students?lop=k47a&min_avg=7"` -> Trả về `HTTP/1.1 200 OK` (Danh sách JSON sinh viên).
- `curl -i "$B/api/students?min_avg=abc"` -> Trả về `HTTP/1.1 400 BAD REQUEST` (Lỗi sai kiểu).
- `curl -i $B/api/students/999` -> Trả về `HTTP/1.1 404 NOT FOUND`.
- `curl -i -X PUT "$S/web?score=9"` -> Trả về `HTTP/1.1 201 CREATED` kèm `Location`.
- `curl -i -X PUT "$S/WEB?score=7.5"` -> Trả về `HTTP/1.1 200 OK`.
- `curl -i -X PUT "$S/WEB?score=11"` -> Trả về `HTTP/1.1 400 BAD REQUEST` (Điểm ngoài khoảng 0-10).
- `curl -i -X DELETE $S/WEB` -> Trả về `HTTP/1.1 204 NO CONTENT`.
- `curl -i -X POST $S/WEB` -> Trả về `HTTP/1.1 405 METHOD NOT ALLOWED` (Lỗi JSON).
- `curl -i -X POST $B/students` -> Trả về `HTTP/1.1 405 METHOD NOT ALLOWED` (Trang lỗi HTML).
- 