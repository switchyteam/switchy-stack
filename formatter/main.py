import json
import re

from flask import Flask, jsonify, request
from slack_sdk import WebClient

app = Flask(__name__)

# Initialize Slack API client
# slack_token = "qkJFyOcb41yrMZaa2uJWoOcL"
slack_token = "xoxb-732476777527-5788784121718-60WaI3d1Tnh14sHShA1KRcz4"
client = WebClient(token=slack_token)


@app.route("/get_challenge", methods=["POST"])
def get_challenge():
    """Function to validate current route in our server with slack."""
    data = request.get_json()  # Assuming the incoming data is in JSON format
    print("incoming request: {}".format(data))
    challenge = data.get(
        "challenge", None
    )  # Extract the 'challenge' field from the data

    if challenge is None:
        return jsonify({"error": "Missing challenge field"}), 400

    return jsonify({"challenge": challenge})


# Event subscription endpoint
@app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    An incoming message recieved, this function will format is and return the formatted version for final confirmation. 
    On confirmation/abort the developer will be redirected to google.com.
    """
    data = request.get_json()  # Assuming the incoming data is in JSON format
    print("\nincoming request: {}\n".format(data))

    if (
        "event" in data
        and data["event"]["type"] == "message"
        and "text" in data["event"]
    ):
        text = data["event"]["text"]
        user_id = data["event"]["user"]

        keywords = ["priority", "task", "important", "need", "error", "crash"]
        matched_keywords = [keyword for keyword in keywords if keyword in text]

        if len(matched_keywords) >= 2:
            formatted_message = format_message(text, matched_keywords)

            blocks = [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": formatted_message},
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Confirm",
                                "emoji": True,
                            },
                            "style": "primary",
                            "value": "confirm",
                            "url": "https://google.com",
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Cancel"},
                            "style": "danger",
                            "value": "cancel",
                            "url": "https://google.com",
                        },
                    ],
                },
            ]

            print("\nBlocks response: {}\n".format(blocks))

            # Send preview message to sender for confirmation
            client.chat_postMessage(
                channel=user_id, text=formatted_message, blocks=json.dumps(blocks)
            )

    return jsonify({"status": "success"})


def format_message(text, matched_keywords):
    # Format the message using the matched keywords
    priority = "High (default)"
    if "priority" in matched_keywords:
        # Extract priority level from text
        priority_match = re.search(r"priority:\s*(\w+)", text, re.IGNORECASE)
        if priority_match:
            priority = priority_match.group(1)

    formatted_message = f"Task: {text}\nPriority: {priority}\nDescription: {text}"
    return formatted_message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
