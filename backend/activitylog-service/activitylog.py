from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/activitylog"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class ActivityLog(db.Model):
    __tablename__ = 'ActivityLog'
    ActivityID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    UserID = db.Column(db.Integer, nullable=True)
    OrderID = db.Column(db.Integer, nullable=True)
    EventType = db.Column(db.String(100), nullable=False)
    Details = db.Column(db.Text, nullable=True)

    def json(self):
        return {
            "ActivityID": self.ActivityID,
            "Timestamp": self.Timestamp,
            "UserID": self.UserID,
            "OrderID": self.OrderID,
            "EventType": self.EventType,
            "Details": self.Details
        }

@app.route('/api/health')
def health_check():
    return jsonify({"message": "Activity Log API is running!"})

@app.route("/activity", methods=["POST"])
def log_activity():
    data = request.json
    user_id = data.get("UserID")
    order_id = data.get("OrderID")
    event_type = data.get("EventType")
    details = data.get("Details")

    if not event_type:
        return jsonify({"message": "EventType is required"}), 400

    new_activity = ActivityLog(
        UserID=user_id,
        OrderID=order_id,
        EventType=event_type,
        Details=details
    )

    db.session.add(new_activity)
    db.session.commit()

    return jsonify({"message": "Activity logged successfully", "activity": new_activity.json()}), 201

@app.route("/activity", methods=["GET"])
def get_all_activities():
    activities = ActivityLog.query.all()
    return jsonify([a.json() for a in activities])

@app.route("/activity/<int:activity_id>", methods=["GET"])
def get_activity_by_id(activity_id):
    activity = ActivityLog.query.get(activity_id)
    if not activity:
        return jsonify({"message": "Activity not found"}), 404
    return jsonify(activity.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
