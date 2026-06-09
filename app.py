import io
import random
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# This header configuration stops browsers from throwing access/CORS errors locally
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
HOURS_PER_DAY = 8

def is_safe(day, hour, section, teacher, timetable):
    # Check if this specific teacher is already busy in ANY other class during this exact day and hour
    for sec in timetable[day][hour]:
        if timetable[day][hour][sec] and timetable[day][hour][sec]['teacher'] == teacher:
            return False
    return True

def solve_timetable(day_idx, hour_idx, sec_idx, sections, course_requirements, timetable):
    # Base Case 1: If we finished all sections for this hour, move to the next hour
    if sec_idx == len(sections):
        return solve_timetable(day_idx, hour_idx + 1, 0, sections, course_requirements, timetable)
    
    # Base Case 2: If we finished all 8 hours of the day, move to the next day
    if hour_idx == HOURS_PER_DAY:
        return solve_timetable(day_idx + 1, 0, 0, sections, course_requirements, timetable)
        
    # Base Case 3: If we finished all days, check if all course targets reached 0
    if day_idx == len(DAYS):
        for sec in sections:
            for course in course_requirements[sec]:
                if course['remaining'] > 0:
                    return False
        return True

    day = DAYS[day_idx]
    sec = sections[sec_idx]
    courses = list(course_requirements.get(sec, []))
    random.shuffle(courses)

    for course in courses:
        if course['remaining'] > 0:
            if is_safe(day, hour_idx, sec, course['teacher'], timetable):
                # Allocation step
                timetable[day][hour_idx][sec] = {
                    "name": course['name'],
                    "teacher": course['teacher']
                }
                course['remaining'] -= 1

                # Move to next section
                if solve_timetable(day_idx, hour_idx, sec_idx + 1, sections, course_requirements, timetable):
                    return True
                
                # Backtrack step
                course['remaining'] += 1
                timetable[day][hour_idx][sec] = None

    # Fallback option: Assign Free/Library period if this slot cannot host any pending course
    timetable[day][hour_idx][sec] = {"name": "FREE / LIB", "teacher": "-"}
    if solve_timetable(day_idx, hour_idx, sec_idx + 1, sections, course_requirements, timetable):
        return True
    timetable[day][hour_idx][sec] = None
    return False

@app.route('/')
def index():
    return render_template('index.html')

# Explicitly handling POST and OPTIONS requests preventing browser fetch blockages
@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
        
    data = request.json
    num_classes = int(data.get('num_classes', 1))
    raw_course_data = data.get('courseData', {})

    sections = [f"Class {i}" for i in range(1, num_classes + 1)]
    course_requirements = {}
    for sec in sections:
        course_requirements[sec] = []
        user_courses = raw_course_data.get(sec, [])
        for c in user_courses:
            course_requirements[sec].append({
                "name": c['name'].strip().upper(),
                "teacher": c['teacher'].strip().upper(),
                "remaining": int(c['count'])
            })

    # Initialize empty matrix: timetable[DAY][HOUR][SECTION]
    timetable = {day: [ {sec: None for sec in sections} for _ in range(HOURS_PER_DAY) ] for day in DAYS}
    success = solve_timetable(0, 0, 0, sections, course_requirements, timetable)
    
    if success:
        return jsonify({"status": "success", "timetable": timetable, "days": DAYS, "sections": sections})
    else:
        return jsonify({"status": "error", "message": "Could not find a conflict-free match. Try reducing targeted periods or modifying staff assignments."})

# Export directly into Apple Numbers compatible spreadsheet structures
@app.route('/export_numbers', methods=['POST', 'OPTIONS'])
def export_numbers():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})

    data = request.json
    timetable = data.get('timetable', {})
    days = data.get('days', [])
    sections = data.get('sections', [])
    
    # Create an in-memory string buffer for clean data population
    output = io.StringIO()
    
    for sec in sections:
        output.write(f"MASTER TIMETABLE MATRIX: {sec}\n")
        output.write("DAY,Hour 1,Hour 2,Hour 3,BREAK,Hour 4,Hour 5,LUNCH,Hour 6,Hour 7,Hour 8\n")
        
        for day in days:
            row_cells = [day]
            # Mirroring the exact structure of the frontend layout matrix indices
            for h in range(8):
                slot = timetable.get(day, [])[h].get(sec) if timetable.get(day) else None
                
                # Format string output text accurately
                if slot and slot['name'] != "FREE / LIB":
                    cell_text = f"{slot['name']} ({slot['teacher']})"
                else:
                    cell_text = "FREE"
                
                row_cells.append(cell_text)
                
                # Append break intervals exactly inside column cells layout matching the frontend view
                if h == 2:
                    row_cells.append("BREAK")
                elif h == 4:
                    row_cells.append("LUNCH")
                    
            output.write(",".join(row_cells) + "\n")
        output.write("\n\n") # Spacing structural breaks between individual class blocks
        
    buffer = io.BytesIO()
    buffer.write(output.getvalue().encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name="College_Timetable_Export.csv",
        mimetype="text/csv"
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
