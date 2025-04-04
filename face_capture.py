import cv2
import face_recognition
import sqlite3
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox, ttk

# Create folder to store images if not exists
if not os.path.exists("faces"):
    os.makedirs("faces")

# Connect to database
conn = sqlite3.connect("faces.db")
cursor = conn.cursor()

# Ensure table structure is correct
cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        year TEXT NOT NULL,
        branch TEXT NOT NULL,
        section TEXT NOT NULL,
        encoding BLOB NOT NULL,
        image_path TEXT NOT NULL
    )
''')
conn.commit()

# Start Webcam
video_capture = cv2.VideoCapture(0)

print("Press 's' to capture a face. Press 'q' to quit.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Convert to RGB (face_recognition uses RGB images)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_frame)

    # Draw rectangles around detected faces
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    cv2.imshow("Face Capture", frame)

    key = cv2.waitKey(1) & 0xFF

    # Press 's' to save face
    if key == ord('s') and face_locations:
        print("✅ Face captured! Checking for duplicates...")

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        if face_encodings:
            new_encoding = np.array(face_encodings[0])

            # Fetch all stored face encodings from database
            cursor.execute("SELECT name, encoding FROM students")
            stored_faces = cursor.fetchall()

            for stored_name, stored_encoding in stored_faces:
                stored_encoding = np.frombuffer(stored_encoding, dtype=np.float64)
                matches = face_recognition.compare_faces([stored_encoding], new_encoding, tolerance=0.5)

                if True in matches:
                    print(f"⚠ Face of {stored_name} already exists! Try another person.")
                    messagebox.showwarning("Duplicate Face", f"⚠ {stored_name} already registered!")
                    break
            else:
                # If no match found, open Tkinter form
                def save_face():
                    name = name_entry.get().strip()
                    year = year_var.get()
                    branch = branch_var.get()
                    section = section_var.get()

                    if not name:
                        messagebox.showwarning("Input Error", "Name is required!")
                        return

                    # Save image
                    image_filename = f"faces/{name}{year}{section}_{branch}.jpg"
                    cv2.imwrite(image_filename, frame)

                    # Save to database
                    encoding_data = new_encoding.tobytes()
                    cursor.execute("INSERT INTO students (name, year, branch, section, encoding, image_path) VALUES (?, ?, ?, ?, ?, ?)", 
                                   (name, year, branch, section, encoding_data, image_filename))
                    conn.commit()
                    print(f"✅ Face of {name} stored successfully! Image saved as {image_filename}")
                    messagebox.showinfo("Success", f"✅ {name} registered successfully!")

                    form.destroy()  # Close form

                # Create Tkinter form
                form = tk.Tk()
                form.title("Register Face")
                form.geometry("400x350")
                form.configure(bg="#2C3E50")  # Dark background

                # Styling function for hover effect
                def on_enter(e):
                    e.widget.config(bg="#3498db", fg="white")

                def on_leave(e):
                    e.widget.config(bg="#2980b9", fg="white")

                # Create a stylish frame
                frame_main = tk.Frame(form, bg="#34495E", bd=2, relief="solid")
                frame_main.pack(pady=20, padx=20, fill="both", expand=True)

                # Title
                tk.Label(frame_main, text="Register Face", font=("Arial", 16, "bold"), bg="#34495E", fg="white").pack(pady=10)

                # Name field
                tk.Label(frame_main, text="Enter Name:", font=("Arial", 12), bg="#34495E", fg="white").pack(pady=2)
                name_entry = tk.Entry(frame_main, font=("Arial", 12), width=30)
                name_entry.pack(pady=2)

                # Year dropdown
                tk.Label(frame_main, text="Select Year:", font=("Arial", 12), bg="#34495E", fg="white").pack(pady=2)
                year_var = ttk.Combobox(frame_main, values=["1st Year", "2nd Year", "3rd Year", "4th Year"], font=("Arial", 12), state="readonly")
                year_var.pack(pady=2)
                year_var.current(0)

                # Branch dropdown
                tk.Label(frame_main, text="Select Branch:", font=("Arial", 12), bg="#34495E", fg="white").pack(pady=2)
                branch_var = ttk.Combobox(frame_main, values=["CSE", "ECE", "MECH", "CSE-AI"], font=("Arial", 12), state="readonly")
                branch_var.pack(pady=2)
                branch_var.current(0)

                # Section dropdown
                tk.Label(frame_main, text="Select Section:", font=("Arial", 12), bg="#34495E", fg="white").pack(pady=2)
                section_var = ttk.Combobox(frame_main, values=["A", "B"], font=("Arial", 12), state="readonly")
                section_var.pack(pady=2)
                section_var.current(0)

                # Save button with hover effect
                save_btn = tk.Button(frame_main, text="Save", command=save_face, font=("Arial", 12, "bold"), bg="#2980b9", fg="white", padx=10, pady=5, relief="raised")
                save_btn.pack(pady=15)
                save_btn.bind("<Enter>", on_enter)
                save_btn.bind("<Leave>", on_leave)

                form.mainloop()

    elif key == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
conn.close()
