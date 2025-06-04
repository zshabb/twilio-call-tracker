from flask import Flask, request, jsonify
from twilio.rest import Client
import os

app = Flask(__name__)

@app.route('/api/calls', methods=['GET'])
def get_calls():
    advertiser_key = request.args.get('key')

    # Map keys to subaccount SIDs
    mapping = {
        "abcmarketing": "ACxxxxxxxxxxxxxxx1",
        "xyzmedia": "ACyyyyyyyyyyyyyyy2"
    }

    sub_sid = mapping.get(advertiser_key)
    if not sub_sid:
        return jsonify({"error": "Invalid key"}), 403

    parent_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    client = Client(parent_sid, auth_token)
    subclient = client.accounts(sub_sid)

    calls = subclient.calls.list(limit=50)
    return jsonify([
        {
            "from": c.from_,
            "to": c.to,
            "start_time": str(c.start_time),
            "duration": c.duration,
            "status": c.status
        } for c in calls
    ])
