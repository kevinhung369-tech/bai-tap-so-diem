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


# --- PHẦN 0: HÀM PHỤ VÀ KHUNG TRANG ---[cite: 6]
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
    # Dùng {{ và }} để escape ngoặc nhọn trong f-string của Python[cite: 3]
    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{escape(title)} - Sổ điểm</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {{ font-family: 'Nunito', sans-serif; background-color: #f4f7f6; color: #2c3e50; }}
            .glass-nav {{ background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); box-shadow: 0 4px 15px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 1000; }}
            .nav-link {{ color: #596275; font-weight: 600; padding: 12px 20px !important; border-radius: 8px; transition: all 0.3s ease; }}
            .nav-link:hover, .nav-link.active {{ background-color: #4a69bd; color: white !important; transform: translateY(-2px); }}
            .custom-card {{ background: white; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: none; padding: 30px; margin-top: 30px; margin-bottom: 40px; transition: transform 0.3s ease; }}
            .hover-lift:hover {{ transform: translateY(-5px); box-shadow: 0 15px 35px rgba(0,0,0,0.08); }}
            .table-custom th {{ background-color: #f1f2f6; color: #2f3640; border-bottom: 2px solid #dfe4ea; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.5px; padding: 15px; }}
            .table-custom td {{ padding: 15px; vertical-align: middle; border-bottom: 1px solid #f1f2f6; }}
            .badge-rank {{ padding: 8px 12px; font-weight: 700; border-radius: 6px; letter-spacing: 0.3px; }}
            .btn-gradient {{ background: linear-gradient(135deg, #4a69bd, #6a89cc); color: white; border: none; font-weight: 700; box-shadow: 0 4px 15px rgba(74, 105, 189, 0.3); transition: all 0.3s; }}
            .btn-gradient:hover {{ transform: scale(1.05); box-shadow: 0 6px 20px rgba(74, 105, 189, 0.4); color: white; }}
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg glass-nav py-3">
            <div class="container">
                <a class="navbar-brand fw-bold text-primary fs-4" href="{url_for("index")}"><i class="fa-solid fa-graduation-cap me-2"></i>EduGrade</a>
                <div class="navbar-nav ms-auto flex-row gap-2">
                    <a class="nav-link" href="{url_for("index")}"><i class="fa-solid fa-house me-1"></i> Trang chủ</a> 
                    <a class="nav-link" href="{url_for("student_list")}"><i class="fa-solid fa-users me-1"></i> Sinh viên</a> 
                    <a class="nav-link" href="{url_for("search")}"><i class="fa-solid fa-magnifying-glass me-1"></i> Tìm kiếm</a>
                </div>
            </div>
        </nav>
        <div class="container">
            {body}
        </div>
    </body>
    </html>
    """


# --- PHẦN 1: GIAO DIỆN WEB ---[cite: 7]
@app.route("/")
def index():
    total_students = len(STUDENTS)
    classes = set(s["lop"] for s in STUDENTS.values())
    body = f"""
    <div class="custom-card text-center py-5 hover-lift">
        <h1 class="display-4 fw-extrabold mb-3" style="color: #1e272e;">Tổng Quan Hệ Thống</h1>
        <p class="text-muted fs-5 mb-5">Quản lý điểm số sinh viên nhanh chóng, tiện lợi và an toàn.</p>
        
        <div class="row justify-content-center gap-4 mb-5">
            <div class="col-md-4">
                <div class="card bg-primary text-white border-0 shadow-lg rounded-4 p-4 hover-lift">
                    <i class="fa-solid fa-user-graduate fs-1 mb-3 opacity-75"></i>
                    <h5 class="fw-normal">Tổng Sinh Viên</h5>
                    <div class="display-3 fw-bold">{total_students}</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card bg-success text-white border-0 shadow-lg rounded-4 p-4 hover-lift">
                    <i class="fa-solid fa-chalkboard-user fs-1 mb-3 opacity-75"></i>
                    <h5 class="fw-normal">Lớp Học Phần</h5>
                    <div class="display-3 fw-bold">{len(classes)}</div>
                </div>
            </div>
        </div>
        
        <div class="d-flex justify-content-center gap-3">
            <a href="{url_for("student_list")}" class="btn btn-gradient btn-lg px-5 rounded-pill"><i class="fa-solid fa-list me-2"></i>Mở danh sách</a>
            <a href="{url_for("api_students")}" class="btn btn-outline-dark btn-lg px-5 rounded-pill"><i class="fa-solid fa-code me-2"></i>API JSON</a>
        </div>
    </div>
    """
    return layout("Trang chủ", body)


@app.route("/students")
def student_list():
    filter_lop = request.args.get("lop", "").upper()
    all_classes = sorted(list(set(s["lop"] for s in STUDENTS.values())))

    filter_links = [
        f'<a class="btn btn-sm {"btn-dark" if not filter_lop else "btn-outline-dark"} rounded-pill px-3" href="{url_for("student_list")}">Tất cả</a>'
    ]
    for c in all_classes:
        btn_class = "btn-dark" if filter_lop == c else "btn-outline-dark"
        filter_links.append(
            f'<a class="btn btn-sm {btn_class} rounded-pill px-3" href="{url_for("student_list", lop=c)}">{escape(c)}</a>'
        )

    html_rows = ""
    for mssv, data in STUDENTS.items():
        if filter_lop and data["lop"].upper() != filter_lop:
            continue
        summ = student_summary(mssv)
        avg_display = (
            f"<strong class='fs-5 text-primary'>{summ['average']}</strong>"
            if summ["average"] is not None
            else '<span class="text-muted fst-italic"><i class="fa-solid fa-circle-minus me-1"></i>Chưa có</span>'
        )

        rank_badge = "bg-secondary"
        icon = ""
        if summ["rank"] == "Giỏi":
            rank_badge, icon = "bg-success text-white", "fa-star"
        elif summ["rank"] == "Khá":
            rank_badge, icon = "bg-info text-dark", "fa-thumbs-up"
        elif summ["rank"] == "Trung bình":
            rank_badge, icon = "bg-warning text-dark", "fa-minus"
        elif summ["rank"] == "Yếu":
            rank_badge, icon = "bg-danger text-white", "fa-triangle-exclamation"

        html_rows += f"""<tr>
            <td><a href="{url_for("student_detail", mssv=mssv)}" class="fw-bold text-decoration-none text-primary"><i class="fa-regular fa-id-card me-2 text-muted"></i>{escape(mssv)}</a></td>
            <td class="fw-semibold text-dark">{escape(summ["name"])}</td>
            <td><span class="badge bg-light text-dark border border-2 px-3 py-2 rounded-pill">{escape(summ["lop"])}</span></td>
            <td>{avg_display}</td>
            <td><span class="badge-rank {rank_badge}"><i class="fa-solid {icon} me-1"></i> {escape(summ["rank"])}</span></td>
            <td><a href="{url_for("student_detail", mssv=mssv)}" class="btn btn-sm btn-light text-primary fw-bold rounded-pill"><i class="fa-solid fa-arrow-right"></i></a></td>
        </tr>"""

    table_html = (
        """
        <div class="alert alert-warning border-0 shadow-sm rounded-4 mt-4" role="alert"><i class="fa-solid fa-box-open me-2"></i>Không tìm thấy sinh viên nào trong danh sách.</div>
        """
        if not html_rows
        else f"""
        <div class="table-responsive mt-4 rounded-4 shadow-sm border border-light">
            <table class="table table-custom table-hover text-center mb-0 bg-white">
                <thead>
                    <tr><th>Mã Sinh Viên</th><th>Họ & Tên</th><th>Lớp</th><th>Điểm TB</th><th>Đánh Giá</th><th>Chi Tiết</th></tr>
                </thead>
                <tbody>{html_rows}</tbody>
            </table>
        </div>"""
    )

    body = f"""
    <div class="custom-card">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h2 class="fw-bold mb-0 text-dark"><i class="fa-solid fa-address-book text-primary me-2"></i>Danh Sách Lớp</h2>
            <div class="d-flex gap-2 align-items-center">
                <span class="text-muted small fw-bold text-uppercase tracking-wider"><i class="fa-solid fa-filter me-1"></i>Bộ Lọc:</span>
                {"".join(filter_links)}
            </div>
        </div>
        {table_html}
    </div>
    """
    return layout("Danh sách sinh viên", body)


@app.route("/students/<mssv>")
def student_detail(mssv):
    summ = student_summary(mssv)
    if not summ:
        abort(404, description=f"Không có sinh viên với MSSV = {escape(mssv)}.")
    avg_display = (
        f"<span class='text-primary'>{summ['average']}</span>"
        if summ["average"] is not None
        else "Chưa có"
    )

    score_rows = ""
    for subject, score in summ["scores"].items():
        score_rows += f"<tr><td class='fw-bold text-dark'>{escape(subject)}</td><td class='fs-5 fw-bold text-primary'>{score}</td></tr>"

    score_table = (
        f"""
    <table class="table table-custom table-hover text-center align-middle mb-0">
        <thead><tr><th>Tên Học Phần</th><th>Điểm Số</th></tr></thead>
        <tbody>{score_rows}</tbody>
    </table>"""
        if score_rows
        else '<div class="alert alert-light text-center border text-muted"><i class="fa-regular fa-folder-open mb-2 fs-3 d-block"></i>Chưa cập nhật điểm học phần.</div>'
    )

    short_link = url_for("short_link", mssv=mssv, _external=True)

    body = f"""
    <div class="row mt-4">
        <div class="col-md-4">
            <div class="custom-card text-center hover-lift border-top border-primary border-5 mt-0">
                <div class="bg-light rounded-circle mx-auto d-flex align-items-center justify-content-center mb-3" style="width: 100px; height: 100px;">
                    <i class="fa-solid fa-user-graduate fs-1 text-primary"></i>
                </div>
                <h3 class="fw-bold text-dark">{escape(summ["name"])}</h3>
                <p class="text-muted mb-4 fs-5">{escape(mssv)}</p>
                <div class="d-grid gap-2">
                    <div class="bg-light p-3 rounded-3 d-flex justify-content-between align-items-center">
                        <span class="text-muted fw-bold small text-uppercase">Lớp</span>
                        <a href="{url_for("student_list", lop=summ["lop"])}" class="badge bg-primary fs-6 text-decoration-none">{escape(summ["lop"])}</a>
                    </div>
                    <div class="bg-light p-3 rounded-3 d-flex justify-content-between align-items-center">
                        <span class="text-muted fw-bold small text-uppercase">Xếp Loại</span>
                        <span class="fw-bold text-dark">{escape(summ["rank"])}</span>
                    </div>
                    <div class="bg-light p-3 rounded-3 d-flex justify-content-between align-items-center">
                        <span class="text-muted fw-bold small text-uppercase">Điểm TB</span>
                        <span class="fw-extrabold fs-4">{avg_display}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-8">
            <div class="custom-card mt-0">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="fw-bold m-0"><i class="fa-solid fa-chart-line text-success me-2"></i>Chi Tiết Điểm Số</h4>
                    <a href="{url_for("export_csv", mssv=mssv)}" class="btn btn-outline-success btn-sm rounded-pill fw-bold px-3">
                        <i class="fa-solid fa-file-csv me-1"></i> Xuất file CSV
                    </a>
                </div>
                <div class="border rounded-4 overflow-hidden shadow-sm">
                    {score_table}
                </div>
                
                <div class="mt-5 p-4 bg-light rounded-4 d-flex align-items-center justify-content-between border">
                    <div>
                        <h6 class="fw-bold mb-1"><i class="fa-solid fa-link text-primary me-2"></i>Đường dẫn chia sẻ (Rút gọn)</h6>
                        <span class="text-muted small">Sử dụng liên kết này để gửi cho sinh viên xem điểm trực tiếp</span>
                    </div>
                    <a href="{url_for("short_link", mssv=mssv)}" class="badge bg-white text-primary border border-primary p-2 fs-6 text-decoration-none hover-lift">{short_link}</a>
                </div>
            </div>
        </div>
    </div>
    """
    return layout(f"Hồ sơ: {mssv}", body)


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
    safe_q = escape(q)  # Cực kỳ quan trọng để chống XSS[cite: 11]
    results = [
        (mssv, data["name"])
        for mssv, data in STUDENTS.items()
        if q and (q.lower() in data["name"].lower() or q.lower() in mssv.lower())
    ]

    result_html = ""
    if q:
        result_html += f'<h5 class="mt-5 mb-4 text-muted">Tìm thấy <span class="badge bg-primary">{len(results)}</span> kết quả phù hợp với <strong>"{safe_q}"</strong></h5>'
        if results:
            result_html += '<div class="row g-3">'
            for r_mssv, r_name in results:
                result_html += f"""
                <div class="col-md-6">
                    <a href="{url_for("student_detail", mssv=r_mssv)}" class="text-decoration-none">
                        <div class="card border-0 shadow-sm rounded-4 p-3 hover-lift h-100 bg-white">
                            <div class="d-flex align-items-center">
                                <div class="bg-primary text-white rounded-circle d-flex justify-content-center align-items-center me-3" style="width: 45px; height: 45px;">
                                    <i class="fa-regular fa-user"></i>
                                </div>
                                <div>
                                    <h6 class="mb-0 fw-bold text-dark">{escape(r_name)}</h6>
                                    <small class="text-muted">{escape(r_mssv)}</small>
                                </div>
                                <div class="ms-auto"><i class="fa-solid fa-chevron-right text-muted"></i></div>
                            </div>
                        </div>
                    </a>
                </div>"""
            result_html += "</div>"
        else:
            result_html += '<div class="alert text-center py-5"><i class="fa-regular fa-face-frown fs-1 text-muted d-block mb-3"></i>Không tìm thấy dữ liệu trùng khớp.</div>'

    body = f"""
    <div class="custom-card max-w-75 mx-auto">
        <h2 class="fw-bold mb-4 text-center"><i class="fa-solid fa-magnifying-glass text-primary me-2"></i>Tra Cứu Thông Tin</h2>
        <form method="GET" action="{url_for("search")}" class="mt-4">
            <div class="input-group input-group-lg shadow-sm rounded-pill overflow-hidden border">
                <span class="input-group-text bg-white border-0 ps-4 text-muted"><i class="fa-solid fa-search"></i></span>
                <input type="text" name="q" value="{safe_q}" class="form-control border-0 shadow-none px-3" placeholder="Nhập tên hoặc MSSV để tìm kiếm..." autocomplete="off">
                <button type="submit" class="btn btn-primary fw-bold px-5">TÌM KIẾM</button>
            </div>
        </form>
        {result_html}
    </div>
    """
    return layout("Tìm kiếm", body)


# --- PHẦN 2: API JSON ---[cite: 13, 14]
@app.route("/api/students", methods=["GET"])
def api_students():
    lop_filter = request.args.get("lop")
    min_avg_str = request.args.get("min_avg")
    min_avg_val = None
    if min_avg_str is not None:
        try:
            min_avg_val = float(min_avg_str)
        except ValueError:
            abort(400, description="Tham số min_avg phải là một số hợp lệ.")

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
        abort(404, description=f"Không tìm thấy sinh viên mã {escape(mssv)}.")
    return summ


@app.route(
    "/api/students/<mssv>/scores/<course>", methods=["GET", "PUT", "DELETE", "POST"]
)
def api_student_score(mssv, course):
    if request.method == "POST":
        abort(405, description="Phương thức POST không được hỗ trợ.")
    if mssv not in STUDENTS:
        abort(404, description="Không tìm thấy mã sinh viên trong hệ thống.")

    student = STUDENTS[mssv]
    course_upper = course.upper()

    if request.method == "GET":
        if course_upper not in student["scores"]:
            abort(404, description="Học phần này chưa được cập nhật điểm.")
        return {
            "mssv": mssv,
            "course": course_upper,
            "score": student["scores"][course_upper],
        }

    if request.method == "DELETE":
        if course_upper not in student["scores"]:
            abort(404, description="Học phần này chưa được cập nhật điểm.")
        del student["scores"][course_upper]
        return "", 204

    if request.method == "PUT":
        score_str = request.args.get("score")
        if score_str is None:
            abort(400, description="Thiếu tham số 'score' trên URL.")
        try:
            score_val = float(score_str)
            if score_val < 0 or score_val > 10:
                raise ValueError
        except ValueError:
            abort(400, description="Điểm số phải nằm trong khoảng từ 0 đến 10.")

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
        return response_body, 200


# --- PHẦN 3: XỬ LÝ LỖI CHUNG ---[cite: 16]
@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(405)
def handle_error(error):
    if request.path.startswith("/api/"):
        return {"error": error.name, "detail": error.description}, error.code

    error_titles = {
        400: "Lỗi Dữ Liệu",
        404: "Không Tìm Thấy Trang",
        405: "Phương Thức Bị Chặn",
    }
    title = error_titles.get(error.code, "Đã xảy ra lỗi")

    icon_class = (
        "fa-triangle-exclamation"
        if error.code == 400
        else "fa-route"
        if error.code == 404
        else "fa-hand"
    )

    body = f"""
    <div class="d-flex justify-content-center align-items-center my-5 py-5">
        <div class="text-center p-5 bg-white shadow-lg rounded-4 border-top border-danger border-5" style="max-width: 500px;">
            <i class="fa-solid {icon_class} text-danger opacity-75 mb-3" style="font-size: 5rem;"></i>
            <h1 class="display-3 fw-black text-dark mb-0">{error.code}</h1>
            <h3 class="fw-bold mb-3">{title}</h3>
            <p class="text-muted fs-6 mb-4">{escape(error.description)}</p>
            <a href="{url_for("index")}" class="btn btn-dark rounded-pill px-4 py-2 hover-lift"><i class="fa-solid fa-arrow-left me-2"></i>Trở về an toàn</a>
        </div>
    </div>
    """
    return layout(title, body), error.code


if __name__ == "__main__":
    app.run(debug=True, port=8000)
