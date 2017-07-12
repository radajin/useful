import os, forecastio, requests, json
from flask import Flask, request, Response
from slackclient import SlackClient
from bs4 import BeautifulSoup

app = Flask(__name__)
# outgoing webhook token
# $ export SLACK_WEBHOOK_SECRET='xxxxxxxxxxx'
SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
# dark sky api token
FORECAST_TOKEN = os.environ.get('FORECAST_TOKEN')
# incomming webhhok url
BASE_URL = os.environ.get('BASE_URL')


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
    return response


def forecast():
    lat = 37.5124413
    lng = 126.9540519
    forecast = forecastio.load_forecast(FORECAST_TOKEN, lat, lng)
    byHour = forecast.hourly()
    return byHour.summary

def naverRank():
    url = "http://naver.com"
    response = requests.get(url)
    dom = BeautifulSoup(response.content, "html.parser")
    keywords = dom.select(".ah_roll .ah_l .ah_item")
    keyword_list = []
    for keyword in keywords:
        keyword_list.append({
            "title": keyword.select_one(".ah_r").text + " " + keyword.select_one(".ah_k").text,
            "title_link": "https://search.naver.com/search.naver?query="+ keyword.select_one(".ah_k").text,
        })
    return keyword_list

@app.route('/slack', methods=['POST'])
def inbound():
    username = request.form.get('user_name')
    if username != 'slackbot':
        if request.form.get('token') == SLACK_WEBHOOK_SECRET:
            channel_name = request.form.get('channel_name')
            channel_id = request.form.get('channel_id')
            username = request.form.get('user_name')
            text = request.form.get('text')
            if "날씨" in text:
                message = forecast()
                send_slack(":partly_sunny:", message, "weatherbot")
            elif "네이버순위" in text:
                send_slack("", '네이버 실시간 키워드 순위', "rankbot", "#general", naverRank())
            else:
                message = username + " in " + channel_name + " says: " + text
                send_slack("", message, "bot")

    return Response(), 200


@app.route('/info', methods=['GET'])
def info():
    SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
    FORECAST_TOKEN = os.environ.get('FORECAST_TOKEN')
    BASE_URL = os.environ.get('BASE_URL')
    print(SLACK_WEBHOOK_SECRET, FORECAST_TOKEN, BASE_URL)
    return Response('Check server log!')


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == "__main__":
    app.run(debug=True)
