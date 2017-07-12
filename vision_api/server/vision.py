from flask import Flask, render_template, jsonify, Response, request
from selenium import webdriver
import requests, time, os, json

app = Flask(__name__)

@app.route("/")
def hello():
    return "It's working"

SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
BASE_URL = os.environ.get('BASE_URL')

def googleVision(category="Labels"):

    # open virtual display
    # display = Display(visible=0, size=(800, 600))
    # display.start()

    # open chrome web driver
    driver = webdriver.Chrome()

    # move to google vision api web page
    driver.get('https://cloud.google.com/vision/')

    # set analytics image url
    # image_url = "/home/ubuntu/vision/analytics.png" # server path
    image_url = "/Users/rada/Documents/code/git/useful/vision_api/server/analytics.png" # local path

    # move focus to ifamge
    iframe = driver.find_element_by_css_selector("#vision_demo_section iframe")
    driver.switch_to_frame(iframe)

    # image file upload
    driver.find_element_by_id("input").send_keys(image_url)

    # wait analytics time
    delay = 0
    for _ in range(30):
        if driver.find_element_by_id("results").text != '':
            break
        time.sleep(1)
        delay += 1
    print("delay : {}".format(delay))

    # click category
    if category == "Web":
        driver.find_element_by_css_selector("[data-type=webDetection]").click()
        result = driver.find_element_by_id("results").text.split("\n")[1]
    elif category == "Text":
        driver.find_element_by_css_selector("[data-type=textAnnotations]").click()
        result = driver.find_element_by_css_selector("#results .text").text
    else:
        driver.find_element_by_css_selector("[data-type=labelAnnotations]").click()
        result = driver.find_element_by_id("results").text.split("\n")

    driver.close()
    # display.stop()

    return result

def send_slack(emoji, message, username, channel="#general", attachments=[]):
    payload = {
        "channel": channel,
        "username": username,
        "icon_emoji": emoji,
        "text": message,
        "attachments": attachments
    }
    response = requests.post(
        BASE_URL,
        data = json.dumps(payload),
    )
    print(BASE_URL)
    return response

@app.route("/sendslack", methods=['GET'])
def send_slack_test():
    send_slack("", "test str", "test")
    return Response(), 200

@app.route("/visiontest", methods=['GET'])
def vision_test():
    data = {
            "category":"Labels",
            "image_url":"https://www.w3schools.com/css/img_fjords.jpg",
        }

    # image down load
    f = open('analytics.png','wb')
    f.write(requests.get(data["image_url"]).content)
    f.close()

    # google vision api
    result = googleVision()

    return jsonify({"result": result})

@app.route("/vision", methods=['POST'])
def vision():

    username = request.form.get('user_name')
    result = ""

    if username != 'slackbot':

        text = request.form.get('text')

        data = {
                "category":text.split(" ")[2],
                "image_url":text.split(" ")[1].replace("<", "").replace(">", ""),
            }

        print("recieve data - {}".format(data))

        # image down load
        f = open('analytics.png','wb')
        f.write(requests.get(data["image_url"]).content)
        f.close()

        # google vision api
        result = googleVision(data["category"])
        print("Result - {}".format(result))

        send_slack("", str(result), "visionbot")

    return Response(), 200

@app.route('/info', methods=['GET'])
def info():
    SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
    BASE_URL = os.environ.get('BASE_URL')
    print(SLACK_WEBHOOK_SECRET, FORECAST_TOKEN, BASE_URL)
    return Response('Check server log!')
