from flask import request, jsonify, Blueprint, Response
from flask_jwt_extended import jwt_required
from models import Event
from datetime import datetime 
import json

event_bp = Blueprint('event_bp', __name__)

@event_bp.route('/get_event')
def report():
    event = Event.query.filter(        
        Event.start_date <= datetime.now(),
        Event.end_date >= datetime.now()).first()

    if event: 
        json_str = json.dumps(event.to_dict,ensure_ascii=False).encode('utf-8')
        response = Response(json_str, content_type='application/json; charset=utf-8')        
        return response        
    else:
        return jsonify({'message': 'event not found'}), 500