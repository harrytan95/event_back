from flask import Flask, send_from_directory, jsonify, request
from auth.auth import auth_bp as auth_blueprint
from event.event import event_bp as event_blueprint
from event_join.event_join import event_join_bp as event_join_blueprint
from flask_cors import CORS
from extensions import db, jwt
# from configmodule import DevelopmentConfig, ProductionConfig, TestingConfig
from dotenv import dotenv_values
from models import User 
from flask_limiter.util import get_remote_address
from flask_limiter import Limiter
from werkzeug.exceptions import HTTPException
from tasks import flask_app, long_running_task
from celery.result import AsyncResult
import os

#TODO
#Log, alert, cache
#Adust token expired time
app = flask_app

# if dotenv_values(".env")["FLASK_ENV"]=='DEV':  
#     config=DevelopmentConfig    
# elif dotenv_values(".env")["FLASK_ENV"]=='PROD':   
#     config=ProductionConfig
# elif dotenv_values(".env")["FLASK_ENV"]=='QA':   
#     config=TestingConfig

# app=config.create_app()
# config.init()
# app.config.from_object(config())

#app.config.from_prefixed_env()

print(app.config['SECRET_KEY'])
print(app.config['SQLALCHEMY_DATABASE_URI'])
print(app.config['TOKEN_VALID_MIN'])

## Register Blueprint
app.register_blueprint(auth_blueprint, url_prefix='/api/auth/')
app.register_blueprint(event_blueprint, url_prefix='/api/event/')
app.register_blueprint(event_join_blueprint, url_prefix='/api/event_join/')


db.init_app(app)
jwt.init_app(app)

# RATE LIMIT CONFIG
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60/minute"],
    storage_uri="memory://",
)

# CORS
cors = CORS(app, resources={
    r"/api/*": {"origins": ["http://127.0.0.1:5000", "http://127.0.0.1:3000", "http://194.233.94.72","http://localhost:5173"]}},
    supports_credentials=True)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code

    url = request.url
    logstr = f"IP address: {request.remote_addr}, Error at {url}: {str(e)}"
    #logger.error(logstr)
    #alert.send_alert(logstr)

    return jsonify(error=logstr), code


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    # print(jwt_header)    
    # print(jwt_data)    
    return jsonify({"message":"Token has expired", "error":"token_expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    #print(error)
    return jsonify({"message":error, "error":"invalid_token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    #print(error)
    return jsonify({"message":error, "error":"authorization_header"}), 401

@jwt.additional_claims_loader
def make_additional_claims(identity):    
    if identity=="qatesthk":
        return {"is_qa":True}
    return {"is_qa":False}

@jwt.user_lookup_loader
def user_lookup_callback(jwt_headers, jwt_data):    
    identity=jwt_data['sub']    
    # print(identity)
    return User.query.filter_by(siteurl=identity).one_or_none()

@app.post("/trigger_task")
def start_task() -> dict[str, object]:
    iterations = request.args.get('iterations')
    # print(iterations)
    result = long_running_task.delay(int(iterations))
    # result=celery_app.send_task('tasks.runtask', queue='event',args=[12])

    return {"result_id": result.id}

@app.get("/get_result")
def task_result() -> dict[str, object]:
    result_id = request.args.get('result_id')
    print(result_id)
    result = AsyncResult(result_id)#-Line 4
    if result.ready():#-Line 5
        # Task has completed
        if result.successful():#-Line 6
    
            return {
                "ready": result.ready(),
                "successful": result.successful(),
                "value": result.result,#-Line 7
            }
        else:
        # Task completed with an error
            return jsonify({'status': 'ERROR', 'error_message': str(result.result)})
    else:
        # Task is still pending
        return jsonify({'status': 'Running'})
    
if __name__ == "__main__":
    app.run(debug=True)