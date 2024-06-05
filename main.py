import cv2
import pytesseract
from flask import Flask, render_template, request, Response, redirect, url_for
from PIL import Image
from io import BytesIO
import numpy as np
import os
import face_recognition
from PIL import Image
from datetime import datetime
from io import BytesIO
import base64
import string
import serial
import struct
import time
import threading


## TODO
## 2. If no user_faces folder at runtime, make one
## 3. Read JPG images into folder<username>
## 4. Back buttons
## 5. Clean code, make functions 
## 6. rename variables, pages, and functions better
## 7. Delete photo option
## 7. Full storage 


## Scaling necessary for face_recognition, depends on esp vs webcam
scale_up = 4
scale_down = .25
##ser = serial.Serial('COM8', 115200, timeout=100)
# Check for ESP32??? Correct Scaling
try:
    ser = serial.Serial('COM8', 115200, timeout=100)
    scale_up = 2
    scale_down = .5
    ser.close()
except serial.SerialException as e:
    print("Please check the port and try again.")

# Need LeBron to poulate np array correctly
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

            # Find the face locations and encodings in the image
            face_encodings = face_recognition.face_encodings(image)

            # Assuming there is one face per image, take the first encoding
            if face_encodings:
                known_face_encodings = np.append(known_face_encodings, [face_encodings[0]], axis=0)
                known_users.append(os.path.splitext(file_name)[0])
            else:
                print(f"No faces found in image: {file_name}")

user_directory = os.path.join(os.getcwd(), "user_faces")
load_faces_and_encodings(user_directory)

stop_event = threading.Event()

def listen_for_trigger():
    try:
        ser = serial.Serial('COM8', 115200, timeout=100)
        ser.open()
    except serial.SerialException as e:
        print("Please check the port and try again.")
    while not stop_event.is_set():
        if not ser.is_open:
            ser.open()
        try:
            line = ser.readline().decode('utf-8').rstrip()
            if line == "Take_Photo":
                capture()
        except Exception as e:
            print(f"Error reading from serial: {e}")
        finally:
            ser.close()
        time.sleep(0.5)  # Adjust the sleep time as needed

#listener_thread = threading.Thread(target=listen_for_trigger, daemon=True)

def start_listener():
    global listener_thread
    # Reset the stop event
    stop_event.clear()
    # Create a new thread instance and start it
    listener_thread = threading.Thread(target=listen_for_trigger, daemon=True)
    listener_thread.start()

def stop_listener(listener_thread):
    stop_event.set()
    listener_thread.join()

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def read_image_from_serial(ser):
    ser.write(b'TRIGGER')
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
    return img

# Function to perform OCR on an image
def ocr(image):
    text = pytesseract.image_to_string(image)
    return text if text.strip() else "no text found"

def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def get_RGB(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def remove_noise(image):
    return cv2.medianBlur(image,5)
 
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)
    
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

def canny(image):
    return cv2.Canny(image, 100, 200)

def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 

def pre_OCR_image_processing(image):
    clean = remove_noise(image)
    gray = get_grayscale(image)
    rgb = get_RGB(image)
    image = get_RGB(image)
    opened = opening(clean)
    thresh = thresholding(gray)
    cannied = canny(clean)
    return gray 

def reformat_image(image):
    pil_image = Image.fromarray(image)
    img_buffer = BytesIO()
    pil_image.save(img_buffer, format="JPEG")
    img_str = img_buffer.getvalue()
    img_base64 = base64.b64encode(img_str).decode('utf-8')
    return img_base64 

def take_photo():
    camera = cv2.VideoCapture(0)
    return_value, image = camera.read()
    camera.release()
    try:
        ser.close()
        ser.open()
        anImage = read_image_from_serial(ser)
        ser.close()
        time.sleep(.05)
        image = anImage
        serialCam = True
        scale_up = 2
        scale_down = .5
    except Exception as e:
        serialCam = False
        scale_up = 4
        scale_down = .25
        print("Please check the port and try again.")
    return image    

def recognize_n_save(image):
    small_image = cv2.resize(image, (0, 0), fx=scale_down, fy=scale_down)
    rgb_small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations