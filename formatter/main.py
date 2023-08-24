import re

from flask import Flask, jsonify, request
from slack_sdk import WebClient

app = Flask(__name__)

# Initialize Slack API client
slack_token = "YOUR_SLACK_TOKEN"
client = WebClient(token=slack_token)

# Event subscription endpoint
@app.route("/slack/events", methods=["POST"])
def slack_events():
        data = request.json
            
    if "event" in data and data["event"]["type"] == "message" and "text" in data["event"]:
        text = data["event"]["text"]
        user_id = data["event"]["user"]
                                        
        keywords = ["priority", "task", "important", "need", "error", "crash"]
        matched_keywords = [keyword for keyword in keywords if keyword in text]
                                                                
        if len(matched_keywords) >= 2:
            formatted_message = format_message(text, matched_keywords)
        # Send preview message to sender for confirmation
        client.chat_postMessage(channel=user_id, text=formatted_message, blocks=[
            {
                "type": "section",
                "text": {
                            "type": "mrkdwn",
                            "text": formatted_message
                },
                "accessory": {
                                                                                                                                                                                                                                            "type": "actions",
                                                                                                                                                                                                                                                                    "elements": [
                                                                                                                                                                                                                                                                                                    {
                                                                                                                                                                                                                                                                                                                                        "type": "button",
                                                                                                                                                                                                                                                                                                                                                                        "text": {
                                                                                                                                                                                                                                                                                                                                                                                                                "type": "plain_text",
                                                                                                                                                                                                                                                                                                                                                                                                                                                    "text": "Confirm"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    },
                                                                                                                                                                                                                                                                                                                                                                                                        "style": "primary",
                                                                                                                                                                                                                                                                                                                                                                                                                                        "value": "confirm"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    },
                                                                                                                                                                                                                                                                                                                                {
                                                                                                                                                                                                                                                                                                                                                                    "type": "button",
                                                                                                                                                                                                                                                                                                                                                                                                    "text": {
                                                                                                                                                                                                                                                                                                                                                                                                                                            "type": "plain_text",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                "text": "Cancel"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                },
                                                                                                                                                                                                                                                                                                                                                                                                                                    "style": "danger",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                    "value": "cancel"
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                }
                                                                                                                                                                                                                                                                                                                                                        ]
                                                                                                                                                                                                                                                                                        }
                                                                                                                                                                                                                                }
                                                                                                                                                            ])
                                                                                                                                
                                                                                                                                return jsonify({"status": "success"})

                                                                                                                            def format_message(text, matched_keywords):
                                                                                                                                    # Format the message using the matched keywords
                                                                                                                                        priority = "High (default)"
                                                                                                                                            if "priority" in matched_keywords:
                                                                                                                                                        # Extract priority level from text
                                                                                                                                                                priority_match = re.search(r'priority:\s*(\w+)', text, re.IGNORECASE)
                                                                                                                                                                        if priority_match:
                                                                                                                                                                                        priority = priority_match.group(1)
                                                                                                                                                                                            
                                                                                                                                                                                                formatted_message = f"Task: {text}\nPriority: {priority}\nDescription: {text}"
                                                                                                                                                                                                    return formatted_message

                                                                                                                                                                                                if __name__ == "__main__":
                                                                                                                                                                                                        app.run(host="0.0.0.0", port=3000)

