import os, forecastio, requests, json
from flask import Flask, request, Response
from slackclient import SlackClient

app = Flask(__name__)
# outgoing webhook token
# $ export SLACK_WEBHOOK_SECRET='xxxxxxxxxxx'
SLACK_WEBHOOK_SECRET = os.environ.get('SLACK_WEBHOOK_SECRET')
# dark sky api token
FORECAST_TOKEN = os.environ.get('FORECAST_TOKEN')
# incomming webhhok url
BASE_URL = os.environ.get('BASE_URL')

def send_slack(emoji, message, username, channel="#general"):
    payload = {
        "channel": channel,
        "username": username,
        "icon_emoji": emoji,
        "text": message,
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


@app.route('/slack', methods=['POST'])
def inbound():
    username = request.form.get('user_name')
    print('username', username)
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel_name = request.form.get('channel_name')
        channel_id = request.form.get('channel_id')
        print('channel_id', channel_id)
        username = request.form.get('user_name')
        text = request.form.get('text')

        if "날씨" in text:
            message = forecast()
        else:
            message = username + " in " + channel_name + " says: " + text
        send_slack(":partly_sunny:", message, "weatherbot")

    return Response(), 200


@app.route('/', methods=['GET'])
def test():
    return Response('It works!')


if __name__ == "__main__":
    app.run(debug=True)
