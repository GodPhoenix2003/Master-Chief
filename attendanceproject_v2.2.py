import tkinter as tk
from tkinter import ttk
from datetime import datetime, date  # Add this import
import cv2
import numpy as np
import face_recognition
import os
import csv
from email.message import EmailMessage
import ssl
import smtplib

class FaceRecognitionApp:
    def start_attendance(self):
        path = 'C:/Coding/Personal Project (Face Detection)/FaceRecog_Project_Attendance System/Student DataBase'
        stud_db = []
        studNames = []
        studList = os.listdir(path)
        for stud in studList:
            currentImg = cv2.imread(os.path.join(path, stud))
            stud_db.append(currentImg)
            studNames.append(os.path.splitext(stud)[0])

        encode_list_known = self.find_encodings(stud_db)

        stud = cv2.VideoCapture(0)

        dir = 'C:/Coding/Personal Project (Face Detection)/FaceRecog_Project_Attendance System/Attendance/'

        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except PermissionError:
                print(f"PermissionError: Unable to create directory {dir}. Check permissions.")

        filename = str(date.today())
        dir = os.path.join(dir, filename)

        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except PermissionError:
                print(f"PermissionError: Unable to create directory {dir}. Check permissions.")

        col_header = ["Name", "Time"]

        time = datetime.now().strftime('%H-%M-%S')
        filename = filename + '-' + time
        filename = filename + ".csv"

        with open(os.path.join(dir, filename), "w") as f:
            studList = csv.writer(f)
            studList.writerow(col_header)

        while True:
            success, stud_img = stud.read()
            stud_img_s = cv2.resize(stud_img, (0, 0), None, 0.25, 0.25)

            stud_face_loc = face_recognition.face_locations(stud_img_s)
            stud_encode = face_recognition.face_encodings(stud_img_s, stud_face_loc)

            for encode_stud, face_loc_stud in zip(stud_encode, stud_face_loc):
                matches = face_recognition.compare_faces(encode_list_known, encode_stud)
                face_dis = face_recognition.face_distance(encode_list_known, encode_stud)
                match_index = np.argmin(face_dis)

                if matches[match_index]:
                    name = studNames[match_index].upper()
                    y1, x2, y2, x1 = face_loc_stud
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(stud_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(stud_img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(stud_img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    self.mark_attendance(name, time)

            cv2.imshow("Input", stud_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        stud.release()
        cv2.destroyAllWindows()

    def find_encodings(self, stud_img):
        encode_list = []
        for stud in stud_img:
            stud = cv2.cvtColor(stud, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(stud)[0]
            encode_list.append(encode)

        return encode_list

    def mark_attendance(self, stud_name, time):
        dir = 'C:/Coding/Personal Project (Face Detection)/FaceRecog_Project_Attendance System/Attendance'
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
            except PermissionError:
                print(f"PermissionError: Unable to create directory {dir}. Check permissions.")

        filename = str(date.today())
        dir = os.path.join(dir, filename)
        filename = filename + '-' + time
        filename = filename + ".csv"
        dir = os.path.join(dir, filename)

        if not os.path.exists(os.path.dirname(dir)):
            os.makedirs(os.path.dirname(dir))

        with open(dir, 'a+') as f:
            f.seek(0)
            my_stud_list = f.readlines()
            stud_name_list = []
            for line in my_stud_list:
                entry = line.split(',')
                stud_name_list.append(entry[0])
            if stud_name not in stud_name_list:
                timestr = datetime.now().strftime('%H:%M:%S')
                f.writelines(f"\n{stud_name},{timestr}")

                stud_email = []
                email_loc = 'C:/Coding/Personal Project (Face Detection)/FaceRecog_Project_Attendance System/email.csv'

                if not os.path.exists(email_loc):
                    try:
                        os.makedirs(email_loc, exist_ok=True)
                    except PermissionError:
                        print(f"PermissionError: Unable to create directory {email_loc}. Check permissions.")

                with open(email_loc) as em:
                    email_data = csv.reader(em, delimiter=',')
                    next(email_data)
                    for row in email_data:
                        stud_email.append(row)

                for row in stud_email:
                    if stud_name == row[0]:
                        self.send_mail(row[1])
                        break

    def send_mail(self, receiver):
        email_sender = 'sagnikchatterjee2003.official@gmail.com'
        email_password = 'qwtthafcsfqcvwuc'
        email_receiver = receiver

        subject = 'Attendance Recorded'
        body = f"""
        Date: {date.today()}
        Time: {datetime.now().strftime('%H:%M:%S')}
        """

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

    def stop_attendance(self):
        # Your code to stop the attendance process (e.g., release camera, close windows, etc.)
        cv2.waitKey(0)
        cv2.destroyAllWindows()  # Close any OpenCV windows
        # You might need additional steps to stop any ongoing processes or loops

        # Optional: Add any additional actions you need when stopping attendance

    # Other methods remain the same...


# Initialize the Tkinter application
root = tk.Tk()

app = FaceRecognitionApp()

root.title("Face Recognition Attendance System")

# Replace with your Figma label design
label = ttk.Label(root, text="Face Recognition Attendance System", font=("Arial", 16))
label.pack(pady=10)

# Replace with your Figma button design
start_button = ttk.Button(root, text="Start Attendance", command=app.start_attendance)
start_button.pack(pady=10)

# Add a "Stop Attendance" button
stop_button = ttk.Button(root, text="Stop Attendance", command=app.stop_attendance)
stop_button.pack(pady=10)

# Replace with your Figma text widget design
text_widget = tk.Text(root, height=10, width=50)
text_widget.pack(pady=10)

root.mainloop()
