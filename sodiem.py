from flask import Flask, request, url_for, redirect, abort, make_response
from markupsafe import escape

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

STUDENTS = {
    "23T1020001": {
        "name": "Nguyễn Văn An",
        "lop": "MMT",
        "scores": {"PMMNM": 8.5, "CSDL": 7.0},
    },
    "23T1020002": {
        "name": "Trần Thị Bình",
        "lop": "MMT",
        "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 9.0},
    },
    "23T1020003": {
        "name": "Lê Hoàng Cường",
        "lop": "K47A",
        "scores": {"PMMNM": 9.5, "CSDL": 9.0},
    },
    "23T1020004": {
        "name": "Phạm Minh Dũng",
        "lop": "K47A",
        "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 7.0},
    },
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47B", "scores": {}},
    "23T1020006": {
        "name": "Võ Quốc Khánh",
        "lop": "K47C",
        "scores": {"PMMNM": 7.5, "MMT": 8.0},
    },
}


# --- PHẦN 0: HÀM PHỤ VÀ KHUNG TRANG ---
def average(scores):
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)


def rank(avg):
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"


def student_summary(mssv):
    if mssv not in STUDENTS:
        return None
    student = STUDENTS[mssv]
    avg = average(student["scores"])
    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rank(avg),
    }


def layout(title, body):
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>{escape(title)} - Sổ điểm</title>
    </head>
    <body>
        <nav>
            <a href="{url_for("index")}">Trang chủ</a> | 
            <a href="{url_for("student_list")}">Sinh viên</a> | 
            <a href="{url_for("search")}">Tìm kiếm</a>
        </nav>
        <hr>
        {body}
    </body>
    </html>
    """


# --- PHẦN 1: GIAO DIỆN WEB ---
@app.route("/")
def index():
    total_students = len(STUDENTS)
    classes = set(s["lop"] for s in STUDENTS.values())
    body = f"""
    <h1>Trang chủ</h1>
    <p>Tổng số sinh viên: {total_students}</p>
    <p>Số lớp: {len(classes)}</p>
    <ul>
        <li><a href="{url_for("student_list")}">Danh sách sinh viên</a></li>
        <li><a href="{url_for("api_students")}">API Sinh viên</a></li>
    </ul>
    """
    return layout("Trang chủ", body)


@app.route("/students")
def student_list():
    filter_lop = request.args.get("lop", "").upper()
    all_classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))

    filter_links = [f'<a href="{url_for("student_list")}">Tất cả</a>']
    for c in all_classes:
        filter_links.append(
            f'<a href="{url_for("student_list", lop=c)}">{escape(c)}</a>'
        )

    html_rows = ""
    for mssv, data in STUDENTS.items():
        if filter_lop and data["lop"].upper() != filter_lop:
            continue
        summ = student_summary(mssv)
        avg_display = summ["average"] if summ["average"] is not None else ""
        html_rows += f"""<tr>
            <td><a href="{url_for("student_detail", mssv=mssv)}">{escape(mssv)}</a></td>
            <td>{escape(summ["name"])}</td>
            <td>{escape(summ["lop"])}</td>
            <td>{escape(avg_display)}</td>
            <td>{escape(summ["rank"])}</td>
        </tr>"""

    table_html = (
        "<p>Không có sinh viên phù hợp.</p>"
        if not html_rows
        else f"""<table border="1" style="border-collapse: collapse; text-align: center;">
            <tr><th>MSSV</th><th>Họ tên</th><th>Lớp</th><th>Điểm TB</th><th>Xếp loại</th></tr>
            {html_rows}
        </table>"""
    )

    body = f"""<h1>Danh sách sinh viên</h1>
    <p>Lọc theo lớp: {" | ".join(filter_links)}</p>
    {table_html}"""
    return layout("Danh sách", body)


@app.route("/students/<mssv>")
def student_detail(mssv):
    summ = student_summary(mssv)
    if not summ:
        abort(404, description=f"Không có sinh viên với MSSV = {escape(mssv)}.")
    avg_display = summ["average"] if summ["average"] is not None else "Chưa có điểm"

    score_rows = ""
    for subject, score in summ["scores"].items():
        score_rows += f"<tr><td>{escape(subject)}</td><td>{score}</td></tr>"

    score_table = (
        f"<table border='1'><tr><th>Học phần</th><th>Điểm</th></tr>{score_rows}</table>"
        if score_rows
        else "<p>Chưa có điểm học phần nào.</p>"
    )
    short_link = url_for("short_link", mssv=mssv)

    body = f"""<h2>{escape(summ["name"])} ({escape(mssv)})</h2>
    <p>Lớp: <a href="{url_for("student_list", lop=summ["lop"])}">{escape(summ["lop"])}</a></p>
    <p>Điểm TB: {escape(avg_display)} | Xếp loại: {escape(summ["rank"])}</p>
    {score_table}
    <br><a href="{url_for("export_csv", mssv=mssv)}">Tải bảng điểm (CSV)</a>
    <p>Link rút gọn: <a href="{short_link}">{short_link}</a></p>"""
    return layout(f"Chi tiết {mssv}", body)


@app.route("/sv/<mssv>")
def short_link(mssv):
    return redirect(url_for("student_detail", mssv=mssv), code=301)


@app.route("/students/<mssv>/export")
def export_csv(mssv):
    summ = student_summary(mssv)
    if not summ:
        abort(404, description="Không tìm thấy sinh viên.")
    csv_content = "hoc_phan,diem\n" + "".join(
        [f"{subject},{score}\n" for subject, score in summ["scores"].items()]
    )
    response = make_response(csv_content)
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = f"attachment; filename=diem_{mssv}.csv"
    return response


@app.route("/search")
def search():
    q = request.args.get("q", "")
    safe_q = escape(q)
    results = [
        (mssv, data["name"])
        for mssv, data in STUDENTS.items()
        if q and (q.lower() in data["name"].lower() or q.lower() in mssv.lower())
    ]

    result_html = ""
    if q:
        result_html += f'<p>Tìm thấy {len(results)} kết quả cho "{safe_q}".</p>'
        if results:
            result_html += (
                "<ul>"
                + "".join(
                    [
                        f'<li><a href="{url_for("student_detail", mssv=r_mssv)}">{escape(r_mssv)} - {escape(r_name)}</a></li>'
                        for r_mssv, r_name in results
                    ]
                )
                + "</ul>"
            )

    body = f"""<h1>Tìm kiếm sinh viên</h1>
    <form method="GET" action="{url_for("search")}">
        <input type="text" name="q" value="{safe_q}">
        <button type="submit">Tìm kiếm</button>
    </form>
    <hr>{result_html}"""
    return layout("Tìm kiếm", body)


# --- PHẦN 2: API JSON ---
@app.route("/api/students", methods=["GET"])
def api_students():
    lop_filter = request.args.get("lop")
    min_avg_str = request.args.get("min_avg")

    min_avg_val = None
    if min_avg_str is not None:
        try:
            min_avg_val = float(min_avg_str)
        except ValueError:
            abort(400, description="Tham số min_avg phải là một số.")

    result = []
    for mssv in STUDENTS:
        summ = student_summary(mssv)
        if lop_filter and summ["lop"].upper() != lop_filter.upper():
            continue
        if min_avg_val is not None and (
            summ["average"] is None or summ["average"] < min_avg_val
        ):
            continue
        result.append(summ)
    return result


@app.route("/api/students/<mssv>", methods=["GET"])
def api_student_detail(mssv):
    summ = student_summary(mssv)
    if not summ:
        abort(404, description=f"Không tìm thấy sinh viên {escape(mssv)}.")
    return summ


@app.route(
    "/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE", "POST"]
)
def api_student_score(mssv, course):
    if request.method == "POST":
        abort(405, description="Phương thức không được hỗ trợ.")
    if mssv not in STUDENTS:
        abort(404, description="Không tìm thấy sinh viên.")

    student = STUDENTS[mssv]
    course_upper = course.upper()

    if request.method == "GET":
        if course_upper not in student["scores"]:
            abort(404, description="Học phần chưa có điểm.")
        return {
            "mssv": mssv,
            "course": course_upper,
            "score": student["scores"][course_upper],
        }

    if request.method == "DELETE":
        if course_upper not in student["scores"]:
            abort(404, description="Học phần chưa có điểm.")
        del student["scores"][course_upper]
        return "", 204

    if request.method == "PUT":
        score_str = request.args.get("score")
        if score_str is None:
            abort(400, description="Thiếu tham số score.")
        try:
            score_val = float(score_str)
            if score_val < 0 or score_val > 10:
                raise ValueError
        except ValueError:
            abort(400, description="Điểm phải là số từ 0 đến 10.")

        is_new_course = course_upper not in student["scores"]
        student["scores"][course_upper] = score_val

        response_body = {
            "mssv": mssv,
            "course": course_upper,
            "score": score_val,
            "average": average(student["scores"]),
        }

        if is_new_course:
            resp = make_response(response_body, 201)
            resp.headers["Location"] = url_for(
                "api_student_score", mssv=mssv, course=course_upper
            )
            return resp
        else:
            return response_body, 200
        # --- PHẦN 3: XỬ LÝ LỖI ---


@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    # Trả về JSON nếu là đường dẫn API
    if request.path.startswith("/api/"):
        return {"error": error.name, "detail": error.description}, error.code

    # Trả về HTML dùng layout() nếu là trang thông thường
    error_titles = {
        400: "Dữ liệu không hợp lệ",
        404: "Không tìm thấy",
        405: "Phương thức không được hỗ trợ",
    }
    title = error_titles.get(error.code, "Lỗi")
    body = f"<h1>Lỗi {error.code}: {title}</h1><p>{escape(error.description)}</p>"

    return layout(title, body), error.code


if __name__ == "__main__":
    app.run(debug=True, port=8000)
