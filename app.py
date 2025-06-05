from flask import Flask, request, jsonify
from flask_cors import CORS
from twilio.rest import Client
from datetime import datetime
import pytz
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

    try:
        from_date = datetime.strptime(from_date_str, "%Y-%m-%d").date() if from_date_str else None
        to_date = datetime.strptime(to_date_str, "%Y-%m-%d").date() if to_date_str else None
    except:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 200

    eastern = pytz.timezone("US/Eastern")

    try:
        all_calls = subclient.calls.list(limit=1000)
        inbound_calls = [
            c for c in all_calls
            if c.direction == "inbound"
            and (not from_date or c.start_time.astimezone(eastern).date() >= from_date)
            and (not to_date or c.start_time.astimezone(eastern).date() <= to_date)
        ]

        return jsonify([
            {
                "from": c.__dict__.get('from_formatted', ''),
                "to": c.to,
                "start_time": str(c.start_time),
                "duration": c.duration,
                "status": c.status
            } for c in inbound_calls
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/numbers', methods=['GET'])
def get_numbers():
    advertiser_key = request.args.get('key')

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

    try:
        numbers = subclient.incoming_phone_numbers.list()
        return jsonify([
            {
                "phone_number": n.phone_number,
                "friendly_name": n.friendly_name or n.phone_number
            } for n in numbers
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
