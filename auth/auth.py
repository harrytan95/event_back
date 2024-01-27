from flask import request, jsonify, make_response, Blueprint, current_app
from datetime import datetime, timedelta 
from flask_jwt_extended import (create_access_token, 
                                create_refresh_token, 
                                jwt_required, 
                                current_user,
                                get_jwt_identity,
                                set_access_cookies, 
                                set_refresh_cookies)
from models import User, OTP
from utils.otp import gen_otp
from tasks import celery_app
#TODO

auth_bp = Blueprint('auth_bp', __name__)
    
@auth_bp.post('/jwt_login')
def login_user():
    credentials_header = request.headers.get('Authorization')
    print("Credentials Header:", credentials_header)

    data=request.get_json()
    
    user=User.get_user_by_siteurl(siteurl=data.get('siteurl').strip())

    if user and (user.check_password(password=data.get('password').strip())):      
        access_token = create_access_token(identity=user.siteurl,expires_delta=timedelta(minutes=int(current_app.config['TOKEN_VALID_MIN'])))
        refresh_token = create_refresh_token(identity=user.siteurl)

        response = jsonify(
        {
            'code' : '301',
            'message': 'Logged in'
            # ,'token': {
            #     'access':access_token,
            #     'refresh':refresh_token
            # }
        })
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        return response, 200

    else:
        return jsonify({'code': '302', 'message': 'unauthorized'}),401

@auth_bp.post('/forgot_p')
def forgot_pwd():
    data=request.get_json()
    email=data.get('email').strip()    
    new_pwd=data.get('new_pwd').strip()
    otp=data.get('otp').strip()
    otp_type='CHG'

    if OTP.verify_otp(email,otp,otp_type):     
        user=User.get_user_by_email(email)
        if user:
            user.set_password(new_pwd)
            if user.save():
                otp_object=OTP.fetch_otp(email,otp,otp_type)
                otp_object.is_used=True
                otp_object.save()
                return jsonify({'code': '204', 'message': 'Password has been changed'}),200
    else:
        return jsonify({'code': '202', 'message': 'OTP mismatch'}),200       
        
    return jsonify({'code': '205', 'message': 'User failed to change'}),200

@auth_bp.post('/signup')
def signup():
    data=request.get_json()
    siteurl=data.get('siteurl').strip()
    # otp=data.get('otp').strip()    
    name=data.get('name').strip()
    email=data.get('email').strip()    
    lang=data.get('lang').strip()
    user=User.get_user_by_siteurl(siteurl=siteurl)    
    otp_type='REG'
    if user is None:
        user=User.get_user_by_email(email=email)       

    if user is None:
        if True:
        # if OTP.verify_otp(email,otp,otp_type):     
            new_user = User(
                name = name,
                email = email,
                siteurl = siteurl,
                create_date = datetime.now(),
                update_date = datetime.now(),
                lang=lang.upper()
            )     
        
            new_user.set_password(data.get('password'))
            if new_user.save():
                #otp_object=OTP.fetch_otp(email,otp,otp_type)
                #otp_object.is_used=True
                #otp_object.save()
                pass

                return jsonify({'code': '201', 'message': 'User has been added'}),200
        else:
            return jsonify({'code': '202', 'message': 'OTP mismatch'}),200
    else: 
        return jsonify({'code': '203', 'message': 'User already exists'}),200
    
@auth_bp.post('/get_otp')
def otp():
    data=request.get_json()   
    email=data.get('email').strip()    
    otp_type=data.get('otp_type').strip()

    if otp_type=="REG" and User.check_email_exists(email):
        return jsonify({'code': '102', 'message': 'email exists'}), 200
    
    otp = gen_otp()   
    new_otp = OTP(         
            otp_type=data.get('otp_type','REG'),
            otp = otp,
            create_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(minutes=10),
            email=email,
            is_used=False
    )
    new_otp.save()    
    #send email with otp
    if otp_type.strip()=="REG":
        email_sent=celery_app.send_task('tasks.send_otp_email', queue='event', args=[email, otp])    
    elif otp_type.strip()=="CHG":
        email_sent=celery_app.send_task('tasks.send_change_pwd_email', queue='event', args=[email, otp])    

    if email_sent:
        return jsonify({'code': '103', 'message': 'otp sent successfully'}),200
    else:
        return jsonify({'code':'104', 'message': 'otp failed to send'}),200


@auth_bp.get('/whoami')
@jwt_required()
def whoami():
    #print(current_user)
    return jsonify({"user_details": {"user_siteurl": current_user.siteurl, "user_email": current_user.email}})

@auth_bp.get('/refresh')
@jwt_required(refresh=True)
def refresh_access(): 
    identity = get_jwt_identity()
    new_access_token=create_access_token(identity=identity,expires_delta=timedelta(minutes=int(current_app.config['TOKEN_VALID_MIN'])))
    response= jsonify(
    {
        'message': 'Token refreshed',
        'token': {
            'access':new_access_token
        }
    })
    set_access_cookies(response, new_access_token)    
    return response, 200




