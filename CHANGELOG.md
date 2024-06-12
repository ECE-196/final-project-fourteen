{May 18}

Contributors:

all

Added:

We added a skeleton of how our website will function, with different pages to be served on the raspberryPi, also tested the face recognition on its own to assure it works. We had been working with OCR only up until this point, but performance was horrible.

Changed:

Removed:

n/a

{May 19}

Contributors:

all

Added:

Improved readability and added functions to support Object Character Recognition for our website to recognize groceries through the label. Also improved capture new user to minimize bugs.

Changed:

Removed:

n/a

{DATE}

Contributors:

Added:

Added code for the arduino, able to capture a picture with command from arduino and esp32. Added the camera functionality to our main python code to acheive face detection outside of just the laptop camera.

Changed:

Removed:

n/a

{May 20}

Contributors:

All

Added:

Wrote load_faces_and_encodings() to rebuild user face data after rebooting the pi. Before this, we needed to create a new user each time the program ran. It stored face data on RAM instead of Disk, so we needed a way to access the face data each capture call.Improved newUserPage UI for visibility and worked around bugs.

Changed:

Removed:

n/a

{May 20}

Contributors:

Cyrus

Added:

Added updated html files to improve the visibility. Also added code to our main python script to help with serial communication errors due to port overloading.

Changed:

Removed:

n/a

{May 22}

Contributors:

Theo

Added:

Improved seeeduino for pcb functionality (i.e. button push and buzzer)

Changed:

Removed:

n/a

{May 27}

Contributors:

all

Added:

Updated the functions for more readability in main, recognizing and saving images uses takes parameter directory as opposed to user, and we continue to work with the seeduino and pcb abandoning our attempt to send higher resolution photos for less bugs. Added a try again image for users who spam the buttons. 

Changed:

Removed:

OCR. It sucked

n/a

{May 28}

Contributors:

all

Added:

Cleaned up code (htmls and main) for more back buttons, and added improved error handling with regards to threading issue we have been facing, displaying error issues to the user preventing our program from crashing. The threading and serial port issue was our biggest culprit. 

Changed:

Removed:

n/a

{May 29}

Contributors:

Johnathan

Added:

Uploaded working object detection model with its own main.py ready for integration into our main code
 
Changed:

Removed:

n/a

{May 30/31}

Contributors:

all

Added:

Added Object detection. Cyrus parsed the returned object recognition results and We started naming images based on the othe best result. Modified and cleaned recognize n save. Recognize and save holding all core functionality - face and object recognition. Added a delete button
 
Changed:

Removed:

n/a

{June 2}

Contributors:

all

Added:

Object detection was returning incorrect inferences so we Started training our own object detection. Johnathan trianed his model with over a thousand images taken with the seeed of common food. Started working on notifications. Added a second thread operation to track the length items have been in the fridge
 
Changed:

Removed:

n/a

{June 5}

Contributors:

all

Added:

Uploaded final code. Finalized object detection model, auto delete and notification functions, crisp error handling, face detection doesnt get it wrong.
 
Changed:

Removed:

n/a
