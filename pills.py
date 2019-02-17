import picamera, time, cv2, io, fractions, json, datetime
import numpy as np
from flask import Flask, request

app = Flask(__name__, static_url_path='')
log = [{'color': "", 'state': "", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))}]
counter = 1


def detect_colors(camera):
    # saving the picture to an in-program stream rather than a file
    stream = io.BytesIO()

    # capture into stream
    time.sleep(1)

    # capture into stream
    camera.capture(stream, format='jpeg')
    # convert image into numpy array
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    # turn the array into a cv2 image
    img = cv2.imdecode(data, 1)
    # Resizing the image, blur the image and convert it to HSV values for better recognition
    height, width = img.shape[:2]
    img = cv2.resize(img, (int(1 / 2 * width), int(1 / 2 * height)))
    temp = cv2.GaussianBlur(img, (5, 5), 0)
    dilation = np.ones((15, 15), "uint8")

    img_red = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
    red_lower = np.array([0, 100, 100], np.uint8)
    red_upper = np.array([10, 255, 255], np.uint8)
    red_binary = cv2.inRange(img_red, red_lower, red_upper)
    red_binary = cv2.dilate(red_binary, dilation)
    red_contours, _ = cv2.findContours(red_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    save_contours(img_red, red_contours, "red.jpg")

    img_blue = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
    blue_lower = np.array([100, 100, 150], np.uint8)
    blue_upper = np.array([110, 255, 255], np.uint8)
    blue_binary = cv2.inRange(img_blue, blue_lower, blue_upper)
    blue_binary = cv2.dilate(blue_binary, dilation)
    blue_contours, _ = cv2.findContours(blue_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    save_contours(img_blue, blue_contours, "blue.jpg")

    img_green = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
    green_lower = np.array([45, 100, 50], np.uint8)
    green_upper = np.array([80, 255, 255], np.uint8)
    green_binary = cv2.inRange(img_green, green_lower, green_upper)
    green_binary = cv2.dilate(green_binary, dilation)
    green_contours, _ = cv2.findContours(green_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    save_contours(img_green, green_contours, "green.jpg")

    img_yellow = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
    yellow_lower = np.array([15, 100, 100], np.uint8)
    yellow_upper = np.array([30, 255, 255], np.uint8)
    yellow_binary = cv2.inRange(img_yellow, yellow_lower, yellow_upper)
    yellow_binary = cv2.dilate(yellow_binary, dilation)
    yellow_contours, _ = cv2.findContours(yellow_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    save_contours(img_yellow, yellow_contours, "yellow.jpg")

    # img_purple = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
    # purple_lower = np.array([115, 100, 50], np.uint8)
    # purple_upper = np.array([130, 255, 255], np.uint8)
    # purple_binary = cv2.inRange(img_purple, purple_lower, purple_upper)
    # purple_binary = cv2.dilate(purple_binary, dilation)
    # purple_contours, _ = cv2.findContours(purple_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # save_contours(img_purple, purple_contours, "purple.jpg")

    return {'red': not red_contours == [], 'blue': not blue_contours == [], 'green': not green_contours == [],
            'yellow': not yellow_contours == []}  # , {"purple": not purple_contours == []}]


def save_boxes(img, keypoints, name):
    im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0, 0, 255),
                                          cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv2.imwrite(name, im_with_keypoints)


def save_contours(img, contours, name):
    im_with_contours = cv2.drawContours(img, contours, -1, (0, 255, 0), 3)
    cv2.imwrite(name, im_with_contours)


@app.route("/get-data")
def getData():
    return json.dumps(log)


@app.route('/')
def root():
    data = open('index.html').read()
    return data


@app.route("/start")
def hello1():
    global running
    running = False
    if not running:
        running = True
        with picamera.PiCamera() as camera:
            camera.resolution = (320 * 8, 240 * 8)
            camera.iso = 800
            counter = 1
            while True:
                colors = detect_colors(camera)
                print(colors)
                if (log[counter - 1]['color'] == "red" and log[counter - 1]['state'] == "removed") and colors['red']:
                    log.append({'color': "red", 'state': "replaced", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1
                elif (not (log[counter - 1]['color'] == "red" and log[counter - 1]['state'] == "removed")) and not colors['red']:
                    log.append({'color': "red", 'state': "removed", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1

                if (log[counter - 1]['color'] == "blue" and log[counter - 1]['state'] == "removed") and colors['blue']:
                    log.append({'color': "blue", 'state': "replaced", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1
                elif (not (log[counter - 1]['color'] == "blue" and log[counter - 1]['state'] == "removed")) and not colors['blue']:
                    log.append({'color': "blue", 'state': "removed", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1

                if (log[counter - 1]['color'] == "green" and log[counter - 1]['state'] == "removed") and colors['green']:
                    log.append({'color': "green", 'state': "replaced", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1
                elif (not (log[counter - 1]['color'] == "green" and log[counter - 1]['state'] == "removed")) and not colors['green']:
                    log.append({'color': "green", 'state': "removed", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1

                if (log[counter - 1]['color'] == "yellow" and log[counter - 1]['state'] == "removed") and colors['yellow']:
                    log.append({'color': "yellow", 'state': "replaced", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1
                elif (not (log[counter - 1]['color'] == "yellow" and log[counter - 1]['state'] == "removed")) and not colors['yellow']:
                    log.append({'color': "yellow", 'state': "removed", 'time': str(datetime.datetime.now().strftime('%Y-%m-%dT  %H:%M:%S'))})
                    counter += 1
    return "hi"


if __name__ == "__main__":
    print("staring server")
    app.run(host='0.0.0.0')
