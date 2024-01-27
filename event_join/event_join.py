from flask import request, jsonify, Blueprint, Response
from flask_jwt_extended import jwt_required
from models import EventJoin, Event
from datetime import datetime
import json

event_join_bp = Blueprint('event_join_bp', __name__)

@event_join_bp.route('/get_event_join')
def report():
    event = Event.query.filter(        
    Event.start_date <= datetime.now(),
    Event.end_date >= datetime.now()).first()
    # print(event.event_pk)  
    ej_obj = {}
    if event:       
        ej_obj["code"] = "401"
        ej_obj["message"] = "Video join list"
        ej_obj["videos"] = [e.to_dict for e in EventJoin.query.filter(EventJoin.event_fk==event.event_pk, EventJoin.is_publish==True).all()]
        json_str = json.dumps(ej_obj,ensure_ascii=False).encode('utf-8')
        response = Response(json_str, content_type='application/json; charset=utf-8')        
        response.status_code = 200
        return response 
    else:
        return jsonify({'message': 'event not found'}), 200