# PiCam-Server
PiCam is a Raspberry Pi web server that can stream a video from the Raspberry Pi Camera to your browser.

# How to Install
1. [Set up your Raspberry Pi](https://www.raspberrypi.org/documentation/installation/)
2. [Install Python 3](https://realpython.com/installing-python/) if needed.
3. Download this repository.
4. Navigate to the repository using a file manager or `cd [DIRECTORY WHERE YOU DOWNLOADED THE REPOSITORY]`.
5. Unzip the repository if needed.
6. [Install PiCamera](https://pypi.org/project/picamera/) using `pip install picamera` or your favorite package manager.
7. Make sure that `picamera_server_faq.html`, `picamera_server_index.html`, and `picamera_server_mobile_index.html` are in the same directory as `picamera_server.py`.
8. Run `picamera_server.py` by double-clicking the file in the file manager or running `python3 picamera_server.py`.
9. NOTE! You might need to run `picamera_server.py` with administrative privileges using `sudo`.
10. [If you want to, you can set the script to run on each boot of the Raspberry Pi](https://raspberrypi.stackexchange.com/questions/8734/execute-script-on-start-up)
11. Watch and star this repository for new updates!
