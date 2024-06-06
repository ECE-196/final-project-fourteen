{May 18}

Contributors:

all

Added:

We added a skeleton of how our website will function, with different pages to be served on the raspberryPi, also tested the face recognition on its own to assure it works. We had been working with OCR only up until this point, but performance was horrible.

Changed:

Removed:

n/a

{DATE}

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

{DATE}

Contributors:

Added:

Wrote load_faces_and_encodings() to rebuild user face data after rebooting the pi. Before this, we needed to create a new user each time the program ran. It stored face data on RAM instead of Disk, so we needed a way to access the face data each capture call.Improved newUserPage UI for visibility and worked around bugs.

Changed:

Removed:

n/a

{DATE}

Contributors:

Added:

Added updated html files to improve the visibility. Also added code to our main python script to help with serial communication errors due to port overloading.

Changed:

Removed:

n/a

{DATE}

Contributors:

Added:

Improved seeeduino for pcb functionality (i.e. button push and buzzer)

Changed:

Removed:

n/a

{DATE}

Contributors:

Added:

Updated the functions for more readability in main, recognizing and saving images uses takes parameter directory as opposed to user, and we continue to work with the seeduino and pcb abandoning our attempt to send higher resolution photos for less bugs.

Changed:

Removed:

n/a

{DATE}

Contributors:

Added:

Cleaned up code (htmls and main) and added improved error handling with regards to threading issue we have been facing.

Changed:

Removed:

n/a
