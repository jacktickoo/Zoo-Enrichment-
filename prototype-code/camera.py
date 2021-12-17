# Following instructions here
# https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/4
from picamera import PiCamera
from time import sleep

class Camera():

    def __init__(self):

        self.camera = PiCamera()
        self.recording = False


    def is_recording(self):
        return self.recording


    def start_recording(self, videoName, directory):
        # this will determine whether the usb can be opened
        self.camera.start_recording(directory + videoName + '.h264')
        self.recording = True


    def stop_recording(self):
        self.camera.stop_recording()
        self.recording = False


    def start_preview(self):
        # views preview of camera on the attached screen
        self.camera.start_preview()


    def stop_preview(self):
        self.camera.stop_preview()


    def capture_image(self, imageName):
        self.camera.start_preview()
        # Note: it’s important to sleep for at least two seconds
        # before capturing an image, because this gives the camera’s
        # sensor time to sense the light levels.
        path = '/home/pi/sakis-video-tunnel/'
        sleep(5)
        self.camera.capture(path + imageName + '.jpg')
        self.camera.stop_preview()
