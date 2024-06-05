We added a skeleton of how our website will function, with different pages to be served on the raspberryPi, also tested the face recognition on its own to assure it works.

Improved readability and added functions to support Object Character Recognition for our website to recognize groceries through the label. Also improved capture new user to minimize bugs.

Added code for the arduino, able to capture a picture with command from arduino and esp32. Added the camera functionality to our main python code to acheive face detection outside of just the laptop camera.

Wrote load_faces_and_encodings() to rebuild user face data after rebooting the pi. Before this, we needed to create a new user each time the program ran. It stored face data on RAM instead of Disk, so we needed a way to access the face data each capture call.Improved newUserPage UI for visibility and worked around bugs.



