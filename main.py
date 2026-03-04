from flask import Flask, request
import requests
import os

app = Flask(__name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
CALLBACK = os.getenv("CALLBACK_URL")

BROADCASTER_ID = "557633478"
BROADCASTER_LOGIN = "dj___shige"


def get_token():

    print("Getting Twitch token...")

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

    print("Subscribing to EventSub...")

    token = get_token()

    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # RAID IN
    body_in = {
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

    # RAID OUT
    body_out = {
        "type": "channel.raid",
        "version": "1",
        "condition": {
            "from_broadcaster_user_id": BROADCASTER_ID
        },
        "transport": {
            "method": "webhook",
            "callback": CALLBACK,
            "secret": "raidsecret"
        }
    }

    r1 = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers=headers,
        json=body_in
    )

    print("Raid IN status:", r1.status_code)

    r2 = requests.post(
        "https://api.twitch.tv/helix/eventsub/subscriptions",
        headers=headers,
        json=body_out
    )

    print("Raid OUT status:", r2.status_code)


@app.route("/")
def home():
    return "Raid Bot Running"


@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    # Twitch verification
    if request.headers.get("Twitch-Eventsub-Message-Type") == "webhook_callback_verification":
        return data["challenge"]

    if data["subscription"]["type"] == "channel.raid":

        raider = data["event"]["from_broadcaster_user_name"]
        target = data["event"]["to_broadcaster_user_name"]
        viewers = data["event"]["viewers"]

        # RAID IN
        if target.lower() == BROADCASTER_LOGIN:

            embed = {
                "title": "⚡ RAID IN",
                "description": f"**{raider} → {target}**",
                "color": 9148193,
                "fields": [
                    {
                        "name": "👥 Viewers",
                        "value": str(viewers),
                        "inline": True
                    }
                ]
            }

        # RAID OUT
        else:

            embed = {
                "title": "🚀 RAID OUT",
                "description": f"**{raider} → {target}**",
                "color": 15158332,
                "fields": [
                    {
                        "name": "👥 Viewers",
                        "value": str(viewers),
                        "inline": True
                    }
                ]
            }

        requests.post(WEBHOOK, json={"embeds":[embed]})

    return "ok"


if __name__ == "__main__":

    subscribe_event()

    app.run(host="0.0.0.0", port=3000)
