from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/calls', methods=['GET'])
def get_calls():
    advertiser_key = request.args.get('key')

    # 🔒 Mapping of advertiser keys to Twilio Subaccount SIDs
    mapping = {
        "abcmarketing": os.environ.get("SUBACCOUNT_ABC"),
        "xyzmedia": os.environ.get("SUBACCOUNT_XYZ")
        # Add more advertisers and their subaccount SIDs as needed
    }

    sub_sid = mapping.get(advertiser_key)
    if not sub_sid:
        return jsonify({"error": "Invalid advertiser key"}), 403

    # Load main account SID and auth token securely
    parent_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    if not parent_sid or not auth_token:
        return jsonify({"error": "Missing Twilio credentials"}), 500

    try:
        client = Client(parent_sid, auth_token)
        subclient = client.api.accounts(sub_sid)
        calls = subclient.calls.list(limit=50)
        inbound_calls = [c for c in calls if c.direction == "inbound"]
        return jsonify([
            {
                "from": c.from_formatted,
                "to": c.to_formatted,
                "start_time": str(c.start_time),
                "duration": c.duration,
                "status": c.status
            } for c in inbound_calls
        ])

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔧 Required for Render deployment — binds to assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
