from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/calls', methods=['GET'])
def get_calls():
    advertiser_key = request.args.get('key')
    from_date_str = request.args.get('from_date')
    to_date_str = request.args.get('to_date')

    mapping = {
        "abcmarketing": os.environ.get("SUBACCOUNT_ABC"),
        "xyzmedia": os.environ.get("SUBACCOUNT_XYZ")
    }

    sub_sid = mapping.get(advertiser_key)
    if not sub_sid:
        return jsonify({"error": "Invalid advertiser key"}), 200

    parent_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    client = Client(parent_sid, auth_token)
    subclient = client.api.accounts(sub_sid)

    # Optional date filtering
    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d") if from_date_str else None
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d") if to_date_str else None
    except Exception as e:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 200

    try:
        all_calls = subclient.calls.list(limit=1000)
        inbound_calls = [
            c for c in all_calls 
            if c.direction == "inbound"
            and (not from_date or c.start_time.date() >= from_date.date())
            and (not to_date or c.start_time.date() <= to_date.date())
        ]

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

# Keep this at the bottom
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
