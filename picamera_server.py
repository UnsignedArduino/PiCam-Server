import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

index_page_file = open("picamera_server_index.html", "r")
index_mobile_page_file = open("picamera_server_mobile_index.html", "r")
faq_page_file = open("picamera_server_faq.html", "r")
index_page = index_page_file.read()
index_mobile_page = index_mobile_page_file.read()
faq_page = faq_page_file.read()
index_page_file.close()
index_mobile_page_file.close()
faq_page_file.close()

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            content = index_page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/mobile.html":
            content = index_mobile_page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/faq.html":
            content = faq_page.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as error:
                logging.warning("Removed streaming client {0}: {1}".format(self.client_address, str(error)))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution="640x480", framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format="mjpeg")
    try:
        address = ("", 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    except Exception as error:
        logging.warning("An exception occurred!\n{0}".format(str(error)))
    finally:
        camera.stop_recording()