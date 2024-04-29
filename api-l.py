from flask import Flask, request, jsonify, make_response
from flask_httpauth import HTTPBasicAuth
import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()

# Mock data for demonstration
logs = [
    {"id": 1, "timestamp": "2024-04-29T12:00:00", "eventType": "Info", "severity": 5, "message": "System check OK"},
    {"id": 2, "timestamp": "2024-04-29T12:10:00", "eventType": "Warning", "severity": 7, "message": "Memory usage high"}
]

# Authentication
users = {
    "admin": "secret"
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users[username]
    return None

# Error Handler
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# GET Logs
@app.route('/logs', methods=['GET'])
@auth.login_required
def get_logs():
    eventType = request.args.get('eventType', type=str)
    severity = request.args.get('severity', type=int)
    filtered_logs = [log for log in logs if 
                     (eventType is None or log['eventType'] == eventType) and
                     (severity is None or log['severity'] == severity)]
    return jsonify(filtered_logs)

# POST Logs
@app.route('/logs', methods=['POST'])
@auth.login_required
def create_log():
    if not request.json or 'message' not in request.json:
        return make_response(jsonify({'error': 'Bad request'}), 400)
    log = {
        'id': logs[-1]['id'] + 1,
        'timestamp': datetime.datetime.now().isoformat(),
        'eventType': request.json.get('eventType', ""),
        'severity': request.json.get('severity', 1),
        'message': request.json['message']
    }
    logs.append(log)
    return jsonify(log), 201

# PUT Logs
@app.route('/logs/<int:log_id>', methods=['PUT'])
@auth.login_required
def update_log(log_id):
    log = next((item for item in logs if item['id'] == log_id), None)
    if log is None:
        return make_response(jsonify({'error': 'Not found'}), 404)
    log['eventType'] = request.json.get('eventType', log['eventType'])
    log['severity'] = request.json.get('severity', log['severity'])
    log['message'] = request.json.get('message', log['message'])
    return jsonify(log)

# DELETE Logs
@app.route('/logs/<int:log_id>', methods=['DELETE'])
@auth.login_required
def delete_log(log_id):
    global logs
    log = next((item for item in logs if item['id'] == log_id), None)
    if log is None:
        return make_response(jsonify({'error': 'Not found'}), 404)
    logs = [log for log in logs if log['id'] != log_id]
    return jsonify({'result': 'Log deleted'})

if __name__ == '__main__':
    app.run(debug=True)
