from flask import Flask, request
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

BROADCASTER_ID = "557633478"

WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CALLBACK = os.getenv("CALLBACK_URL")


def get_token():

    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    ).json()

    return r["access_token"]


def subscribe_event():

    token = get_token()

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "type": "channel.raid",
        "version": "1",
        "condition": {
            "to_broadcaster_user_id": BROADCASTER_ID
        },
        "transport": {
            "method": "webhook",
            "callback": CALLBACK,
            "secret": "raidsecret"
        }
    }

    requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers=headers,
        json=body
    )


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    # Twitch verification
    if request.headers.get("Twitch-Eventsub-Message-Type") == "webhook_callback_verification":
        return data["challenge"]

    if data["subscription"]["type"] == "channel.raid":

        raider = data["event"]["from_broadcaster_user_name"]
        viewers = data["event"]["viewers"]

        embed = {
            "title": "⚡ Twitch RAID",
            "description": f"**{raider}** がレイドしました",
            "url": f"https://twitch.tv/{raider}",
            "color": 9148193,
            "fields": [
                {
                    "name": "👥 Viewers",
                    "value": f"{viewers}",
                    "inline": True
                }
            ],
            "thumbnail": {
                "url": f"https://static-cdn.jtvnw.net/jtv_user_pictures/xarth/404_user_70x70.png"
            },
            "footer": {
                "text": "Twitch Raid Monitor"
            }
        }

        requests.post(WEBHOOK, json={"embeds":[embed]})

    return "ok"


@app.route("/")
def home():
    return "Raid Bot Running"


if __name__ == "__main__":

    subscribe_event()

    app.run(host="0.0.0.0", port=3000)
