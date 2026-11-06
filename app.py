from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"quality_records": [], "supply_records": []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/api/quality', methods=['GET', 'POST'])
def handle_quality():
    data = load_data()
    
    if request.method == 'POST':
        req = request.json
        ph = float(req.get('ph'))
        tds = int(req.get('tds'))
        turbidity = float(req.get('turbidity'))
        microbial = int(req.get('microbial', 0))

        # Compliance Check (WHO / BIS Standards)
        is_safe = (6.5 <= ph <= 8.5) and (tds <= 300) and (turbidity <= 1.0) and (microbial == 0)
        status = "SAFE" if is_safe else "FLAGGED"

        record = {
            "id": len(data["quality_records"]) + 1,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": req.get('source', 'RO Plant'),
            "ph": ph,
            "tds": tds,
            "turbidity": turbidity,
            "microbial": microbial,
            "status": status
        }
        data["quality_records"].append(record)
        save_data(data)
        return jsonify({"message": "Quality record saved", "record": record}), 201

    return jsonify(data["quality_records"])

@app.route('/api/supply', methods=['GET', 'POST'])
def handle_supply():
    data = load_data()
    
    if request.method == 'POST':
        req = request.json
        delivery = {
            "id": len(data["supply_records"]) + 1,
            "customer": req.get('customer'),
            "liters": int(req.get('liters')),
            "date": req.get('date', str(datetime.date.today())),
            "batch_id": req.get('batch_id')
        }
        data["supply_records"].append(delivery)
        save_data(data)
        return jsonify({"message": "Supply record logged", "delivery": delivery}), 201

    return jsonify(data["supply_records"])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
