from flask import Flask, request
import requests
import os

app = Flask(__name__)

WEBHOOK = os.getenv("DISCORD_WEBHOOK")

@app.route("/", methods=["POST"])
def twitch_event():

    data = request.json

    if "challenge" in data:
        return data["challenge"]

    event = data["event"]

    from_user = event["from_broadcaster_user_name"]
    to_user = event["to_broadcaster_user_name"]
    viewers = event["viewers"]

    embed = {
        "title": "🚀 レイド発生",
        "description": f"**{from_user} → {to_user}**",
        "url": f"https://twitch.tv/{to_user}",
        "fields": [
            {
                "name": "👀 レイド人数",
                "value": str(viewers),
                "inline": True
            }
        ],
        "color": 16744192,
        "footer": {
            "text": "Twitch Raid Monitor"
        }
    }

    requests.post(WEBHOOK, json={"embeds":[embed]})

    return "", 200


app.run(host="0.0.0.0", port=3000)
