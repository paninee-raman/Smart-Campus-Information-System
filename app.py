# Smart Campus Information System Website using Flask
# Save this file as app.py

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

students = []
courses = []
graph_url = None
analytics_data = {}
file_report = {}
fee_data = {}
search_result = {}
course_message = ""
sort_message = ""
student_message = ""

# ---------------------------------------------------
# HOME ROUTE
# ---------------------------------------------------

@app.route('/')
def home():

    return render_template("index.html",
                           students=students,
                           courses=courses,
                           graph_url=graph_url,
                           analytics_data=analytics_data,
                           file_report=file_report,
                           fee_data=fee_data,
                           search_result=search_result,
                           course_message=course_message,
                           sort_message=sort_message,
                           student_message=student_message)

# ---------------------------------------------------
# REGISTER STUDENT
# ---------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
    global student_message

    name = request.form['name']
    sid = int(request.form['id'])
    age = int(request.form['age'])
    score = float(request.form['score'])
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "F"
    student = {
        "ID": sid,
        "Name": name,
        "Age": age,
        "Score": score,
        "Grade": grade
    }
    students.append(student)
    student_message = "Student Registered Successfully with Grade " + grade
    return home()

# ---------------------------------------------------
# COURSE ENROLLMENT
# ---------------------------------------------------

@app.route('/course', methods=['POST'])
def course():

    global course_message
    course_name = request.form['course']
    credits = int(request.form['credits'])
    if credits <= 0:
        course_message = "Invalid Credit Value"
        return home()
    courses.append((course_name, credits))
    course_message = "Course Added Successfully"
    return home()

# ---------------------------------------------------
# FEE CALCULATION
# ---------------------------------------------------

@app.route('/fee', methods=['POST'])
def fee():

    global fee_data
    tuition = float(request.form['tuition'])
    hostel = float(request.form['hostel'] or 0)
    transport = float(request.form['transport'] or 0)
    total = tuition + hostel + transport
    fee_data = {
        "tuition": tuition,
        "hostel": hostel,
        "transport": transport,
        "total": total
    }
    return home()

# ---------------------------------------------------
# SEARCH STUDENT
# ---------------------------------------------------

@app.route('/search', methods=['POST'])
def search():

    global search_result
    search_id = int(request.form['search_id'])
    found = False
    for s in students:
        if s["ID"] == search_id:
            search_result = {
                "found": True,
                "name": s["Name"],
                "score": s["Score"],
                "grade": s["Grade"]
            }
            found = True
            break

    if not found:
        search_result = {
            "found": False
        }
    return home()

# ---------------------------------------------------
# SORT STUDENTS
# ---------------------------------------------------

@app.route('/sort', methods=['POST'])
def sort_students():
    global sort_message
    n = len(students)
    for i in range(n):
        for j in range(0, n - i - 1):
            if students[j]["ID"] > students[j + 1]["ID"]:
                students[j], students[j + 1] = students[j + 1], students[j]
    sort_message = "Students Sorted Successfully by ID"
    return home()

# ---------------------------------------------------
# FILE HANDLING
# ---------------------------------------------------

@app.route('/save', methods=['POST'])
def save():

    global file_report
    if len(students) == 0:
        file_report = {
            "message": "No Student Records Available"
        }
        return home()

    # Save records into file
    file = open("student_records.txt", "w")

    for s in students:
        file.write(str(s) + "\n")
    file.close()

    # Generate Report

    total_students = len(students)

    scores = []
    for s in students:
        scores.append(s["Score"])

    average_marks = sum(scores) / len(scores)

    topper = students[0]
    for s in students:
        if s["Score"] > topper["Score"]:
            topper = s

    file_report = {
        "total": total_students,
        "average": round(average_marks, 2),
        "topper_name": topper["Name"],
        "topper_score": topper["Score"]
    }

    return home()


# ---------------------------------------------------
# PERFORMANCE ANALYTICS
# ---------------------------------------------------

@app.route('/analytics', methods=['POST'])
def analytics():

    global graph_url
    global analytics_data

    if len(students) == 0:

        analytics_data = {
            "message": "No Student Data Available"
        }
        return home()

    # Create DataFrame
    df = pd.DataFrame(students)
    scores = df["Score"].to_numpy()
    mean = np.mean(scores)
    median = np.median(scores)
    std = np.std(scores)

    # -----------------------------
    # Matplotlib Graph
    # -----------------------------

    plt.figure(figsize=(6,4))
    plt.bar(df["Name"], df["Score"], color="pink")
    plt.title("Student Performance")
    plt.xlabel("Students")
    plt.ylabel("Scores")
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    analytics_data = {
        "mean": mean,
        "median": median,
        "std": std
    }
    
    return home()

# ---------------------------------------------------
# RUN WEBSITE
# ---------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)