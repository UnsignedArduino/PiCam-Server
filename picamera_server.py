import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from pkg_resources import require

PAGE="""\
<!DOCTYPE html>
<html lang="en-US">
<html>
  <head>
    <title>
      PiCamera MJPEG Stream on Raspberry Pi
    </title>
      <style>
        .centerscr {
          display: block;
  	  margin-left: auto;
 	  margin-right: auto;
  	  width: 75%;
        }
      </style>
    </head>
    <body style="background-color:powderblue;">
      <h1 style="font-family:courier;text-align:center;">
        PiCamera MJPEG Stream
      </h1>
        <p style="font-family:courier;text-align:center;">
          Raspberry Pi Camera Server run by
            <a href="https://www.python.org/">
              Python 3
            </a>
        </p>
      <img src="stream.mjpg" width="640" height="480" alt="PiCamera Stream using MJPEG" title="PiCamera Stream using MJPEG" class="centerscr" />
        <h1 style="font-family:courier;text-align:center;">
          What is this?
        </h1>
        <p style="font-family:courier;text-align:center;">
          This is a Raspberry Pi Camera stream. The server, which is a <a href="https://www.raspberrypi.org/">Raspberry Pi</a>, streams data from the <a href="https://www.raspberrypi.org/products/camera-module-v2/">Pi Camera</a> using <a href="https://en.wikipedia.org/wiki/Motion_JPEG">MJPEG</a> to your browser, allowing you to see what the camera sees!
        </p>
        <h1 style="font-family:courier;text-align:center;">
          Help! I can't see the stream! And other FAQ
        </h1>
        <p style="font-family:courier;text-align:center;">
          <code>
            Q:
          </code>
          I can't see the stream! What do I do?
        </p>
        <p style="font-family:courier;text-align:center;">
          <code>
            A:
          </code>
        <h1 style="font-family:courier;text-align:center;">
          Stats, models, and versions
        </h1>
    </body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
