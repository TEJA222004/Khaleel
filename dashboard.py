from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

csv_file = "attendance.csv"

# Load existing attendance data
def load_attendance():
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file).to_dict(orient="records")
    return []

@app.route("/")
def index():
    attendance_data = load_attendance()
    return render_template("dashboard.html", attendance=attendance_data)

@app.route("/update_attendance", methods=["POST"])
def update_attendance():
    data = request.get_json()
    name = data.get("name")
    timestamp = data.get("timestamp")

    df = pd.DataFrame([[name, timestamp]], columns=["Name", "Timestamp"])
    
    if os.path.exists(csv_file):
        existing_df = pd.read_csv(csv_file)
        df = pd.concat([existing_df, df], ignore_index=True)
    
    df.to_csv(csv_file, index=False)

    return jsonify({"message": "Attendance updated successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
