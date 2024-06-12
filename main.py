import cv2
#import pytesseract
from flask import Flask, render_template, request, Response, redirect, url_for, json, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from PIL import Image
from io import BytesIO
import numpy as np
import os
import face_recognition
from datetime import datetime, timedelta
import base64
import string
import serial
import struct
import time
import threading
from inference_sdk import InferenceHTTPClient
from inference import get_model
import supervision as sv
import roboflow
import re
import ast
from urllib.parse import urlparse

## TODO
## 2. If no user_faces folder at runtime, make one
## 3. Read JPG images into folder<username>
## 4. Back buttons
## 5. Clean code, make functions 
## 6. rename variables, pages, and functions better
## 7. Delete photo option
## 7. Full storage 

EMAIL_ADDRESS = 'fridgeid@outlook.com'
EMAIL_PASSWORD = 'FRIDGE196'
SMTP_SERVER = 'smtp.outlook.com'
SMTP_PORT = 587

lastCaptureTime = 0
captureInterval = 5

## Scaling necessary for face_recognition, depends on esp vs webcam
scale_up = 2
scale_down = .5

from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="3KBf2PlWJgxw65tAUXJA"
)

def send_initial_email(to_email, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(attachment_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
    msg.attach(part)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo() #setting the ESMTP protocol
        server.starttls() #setting up to TLS connection
        server.ehlo() #calling the ehlo() again as encryption happens on calling startttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
    print('Email sent succesfully')
    server.quit()

# Check for ESP32??? Correct Scaling
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=100)
    scale_up = 2
    scale_down = .5
    #ser.close()
except serial.SerialException as e:
    print("Please check the port and try again.")

# Need LeBron to poulate np array correctly
honey_path = os.path.join(os.getcwd(), "tryAgain.jpg")
honey_image = face_recognition.load_image_file(honey_path)
lebron_path = os.path.join(os.getcwd(), "lebron.jpg")
lebron_image = face_recognition.load_image_file(lebron_path)
lebron_face_encoding = face_recognition.face_encodings(lebron_image)[0]
app = Flask(__name__) 

known_users = ["LBJ"]
known_face_encodings = np.array([lebron_face_encoding])

# Scans user_faces and reloads known_faces after reboot
def load_faces_and_encodings(directory):
    global known_users
    global known_face_encodings
    for file_name in os.listdir(directory):
        # Check if the file is an image (you can add more extensions if needed)
        if file_name.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(directory, file_name)
            image = face_recognition.load_image_file(image_path)

            # Find the face locations and encodings in the imagew
            face_encodings = face_recognition.face_encodings(image)

            # Assuming there is one face per image, take the first encoding
            if face_encodings:
                known_face_encodings = np.append(known_face_encodings, [face_encodings[0]], axis=0)
                known_users.append(os.path.splitext(file_name)[0])
            else:
                print(f"No faces found in image: {file_name}")

user_directory = os.path.join(os.getcwd(),"static", "user_faces")
load_faces_and_encodings(user_directory)

def listen_for_trigger():
    global ser
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').rstrip()
                if line == "Take_Photo":
                    #ser.reset_input_buffer()
                    capture()
                    
        except Exception as e:
            pass
        time.sleep(0.1)  # Adjust the sleep time as needed

def send_reminder_email(to_email, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    attachment = open(attachment_path, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {os.path.basename(attachment_path)}")
    msg.attach(part)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo() #setting the ESMTP protocol
        server.starttls() #setting up to TLS connection
        server.ehlo() #calling the ehlo() again as encryption happens on calling startttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
    print('Email sent succesfully')
    server.quit()

def daily_check():
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)
    for user in os.listdir(user_directory):
        user_path = os.path.join(user_directory, user)
        if os.path.isdir(user_path):
            user_email_file = os.path.join(user_path, 'email.txt')
            if os.path.exists(user_email_file):
                with open(user_email_file, 'r') as f:
                    user_email = f.read().strip()

                for photo in os.listdir(user_path):
                    if photo.endswith('.jpg'):
                        photo_name = os.path.splitext(photo)[0]  # Get the filename without extension
                        try:
                            # Assuming the format "wordYYYY-MM-DD-HH-MM-SS.jpg"
                            date_str = photo_name[-19:]  # Extract the date part
                            photo_date = datetime.strptime(date_str, '%Y-%m-%d-%H-%M-%S')
                            if photo_date < one_week_ago:
                                photo_path = os.path.join(user_path, photo)
                                try:
                                    print("lol")
                                    send_reminder_email(
                                        to_email=user_email,
                                        subject="New Photo Captured",
                                        body=f"{name},\n\nYour {word} has been in your fridge for a week:",
                                        attachment_path=photo_path
                                    )
                                except:  
                                    print("lol")
                        except ValueError:
                            continue


def start_listener():
    # Create a new thread instance and start it
    listener_thread = threading.Thread(target=listen_for_trigger, daemon=True)
    listener_thread.start()

def run_daily_task():
    while True:
        daily_check()
        time.sleep(86400)

def start_weekly_checker():
    email_thread = threading.Thread(target=run_daily_task)
    email_thread.daemon = True  # This makes sure the thread will exit when the main program exits
    email_thread.start()

face_locations = []
face_encodings = []
face_names = []

def read_image_from_serial(ser):
    ser.write(b'TRIGGER')
    ser.flushInput()
    ser.flushOutput()
    # Read the length of the image
    img_len_bytes = ser.read(4)
    img_len = int.from_bytes(img_len_bytes, 'little')
    print(f"Image length: {img_len}")

    # Read the image data
    img_data = ser.read(img_len)
    if len(img_data) != img_len:
        print(f"Failed to read the full image. Read {len(img_data)} bytes.")
        return None

    # Decode the image
    img_array = np.frombuffer(img_data, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    #//recognize_n_save(img)
    ser.flushInput()
    ser.flushOutput()
    return img

def get_RGB(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def extract_prefix_before_number(url):
    path = urlparse(url).path
    image_name = path.split('/')[-1]
    match = re.match(r'^[^\d]*', image_name)
    if match:
        return match.group()
    else:
        return ""

def reformat_image(image):
    pil_image = Image.fromarray(image)
    img_buffer = BytesIO()
    pil_image.save(img_buffer, format="JPEG")
    img_str = img_buffer.getvalue()
    img_base64 = base64.b64encode(img_str).decode('utf-8')
    return img_base64 

def full_buffer():
    global lastCaptureTime
    currentTime = time.time()
    if currentTime - lastCaptureTime < 3:
        return True
    lastCaptureTime = currentTime
    return False

def take_photo():
    global ser
    global honey_image
    try:
        image = read_image_from_serial(ser)
    except Exception as e:
        #image = honey_image
        print("Please check the port and try again.(187)")
    return image

def recognize_n_save(image):
    global ser
    small_image = cv2.resize(image, (0, 0), fx=scale_down, fy=scale_down)
    rgb_small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_small_image)
    new_face_encodings = face_recognition.face_encodings(rgb_small_image, face_locations)
    face_names = []
    for face_encoding in new_face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "???"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_users[best_match_index]
            print(name)
            now = datetime.now()
            pil_image = Image.fromarray(image)
            result = CLIENT.infer(image, model_id="food-4-project/6") #Start Object Detection
            res = str(result)
            result_dict = ast.literal_eval(res) 
            try:
                pred_classes = result_dict["predictions"][0]
                pred = pred_classes["class"]
            except:
                pred = "unknown"
            word = str(pred).strip() # End object Detection
            word = word.replace(" ", "_")
            print(word)
            target_dir = os.path.join(user_directory, name, word+now.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg")
            pil_image.save(target_dir)
            face_names.append(name)
            email_file_path = os.path.join(user_directory, name, "email.txt")
            if os.path.exists(email_file_path):
                with open(email_file_path, 'r') as email_file:
                    user_email = email_file.read().strip()
                try:
                    send_initial_email(
                        to_email=user_email,
                        subject="New Photo Captured",
                        body=f"{name},\n\nYou added {word} to your fridge. See below:",
                        attachment_path=target_dir
                    )
                    print("Email sent successfully")
                except Exception as e:  
                    print(e)  
        else:
            face_names.append("???")
            
    if(len(face_names) == 0): # Does the same thing but directs photos to"Unrecognized"
        print("no face found")
        now = datetime.now()
        pil_image = Image.fromarray(image)
        word = "food"
        misc_dir = os.path.join(user_directory, "Unrecognized", word+now.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg")
        pil_image.save(misc_dir)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the image we detected in was scaled to 1/4 size
        top *= scale_up
        right *= scale_up 
        bottom *= scale_up
        left *= scale_up
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    return image  

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/users')
def users():
    folders = get_folders(user_directory)
    return render_template('userPage.html', folders=folders)

@app.route('/newUser')
def newUser():
    return render_template('newUserPage.html')

@app.route('/folder/<folder_name>')
def folder(folder_name):
    folder_path = os.path.join(user_directory, folder_name)
    contents = os.listdir(folder_path)
    image_files = [f for f in contents if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]  # Filter only image files
    image_data = []
    for image_file in image_files:
        additional_string = extract_prefix_before_number(image_file)
        image_url = url_for('static', filename=os.path.join('user_faces', folder_name, image_file).replace('\\', '/'))
        image_data.append({
            'url': image_url,
            'original_name': image_file,
            'added_string': additional_string
        })

    return render_template('folder.html', folder_name=folder_name, image_data=image_data)

@app.route('/delete', methods=['POST'])
def delete_image():
    data = request.get_json()
    print(data)
    image_url = data['image_url']
    full_url = os.getcwd() + image_url
    print(full_url)
    try:
        os.remove(full_url)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_folders(directory):
    folders = []
    for item in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, item)):
            folders.append(item)
    return folders

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    username = str(username).strip()
    email = request.form['email']
    image_data = request.form['image_data']
    known_users.append(username)
    image_bytes = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_bytes))
    save_path = os.path.join(user_directory, username + ".jpg")
    image.save(save_path)
    this_image = face_recognition.load_image_file(save_path)
    this_face_encoding = face_recognition.face_encodings(this_image)
    if this_face_encoding:
        global known_face_encodings
        known_face_encodings = np.vstack([known_face_encodings, this_face_encoding[0]])
    else:
        return render_template('unconfirmed.html')
    newUser_path = os.path.join(user_directory, username)
    if not os.path.exists(newUser_path):
        os.makedirs(newUser_path)
    email_file_path = os.path.join(newUser_path, "email.txt")
    with open(email_file_path, 'w') as email_file:
        email_file.write(email)

    return render_template('confirm.html', username = username, email = email)


@app.route('/capture', methods=['POST'])
def capture(): ## Triggered by physical and virtual button push
    global honey_image
    global ser
    ser.flushInput()
    ser.flushOutput()
    if(full_buffer()):
        image = get_RGB(honey_image) ## Try again image
        img_base64 = reformat_image(image) ## Convert to JPG, return as as bitstream
        return {'text': '', 'image': img_base64}
    image = take_photo() ## Get image from XIAO S3 Sense
    image = get_RGB(image) ## Convert to RGB
    recognized_image = recognize_n_save(image) ## Match face, draw box, save to user
    img_base64 = reformat_image(recognized_image) ## Convert to JPG, return as as bitstream
    ser.flushInput()
    ser.flushOutput()
    return {'text': '', 'image': img_base64}

@app.route('/captureNewUser', methods=['POST'])
def newUserCapture():
    # DO NOT REMOVE
    image = take_photo()
    image = get_RGB(image)
    img_base64 = reformat_image(image)
    return {'text': ' ', 'image': img_base64}

if __name__ == '__main__':
    start_listener()
    #start_weekly_checker()
    app.run(host = "0.0.0.0", port=8000)
    ##python -m http.server 8000 --bind 0.0.0.0