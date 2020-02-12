import picamera

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.start_recording('video.h264')
camera.wait_recording(15)
camera.stop_recording()
