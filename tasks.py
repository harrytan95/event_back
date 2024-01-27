# from config import create_app 
from celery import shared_task 
from time import sleep
from celery.utils.log import get_task_logger
from dotenv import dotenv_values
from configmodule import DevelopmentConfig, ProductionConfig, TestingConfig
from utils.email_by_task import OTPEmail, Change_Pwd_Email

if dotenv_values(".env")["FLASK_ENV"]=='DEV':  
    config=DevelopmentConfig    
elif dotenv_values(".env")["FLASK_ENV"]=='PROD':   
    config=ProductionConfig
elif dotenv_values(".env")["FLASK_ENV"]=='QA':   
    config=TestingConfig

flask_app=config.create_app()
# config.init()
flask_app.config.from_object(config())

# flask_app = create_app() 
celery_app = flask_app.extensions["celery"] 
logger = get_task_logger(__name__)

# @shared_task(name='tasks.runtask',ignore_result=False) 
# @celery_app.task(name='tasks.runtask',ignore_result=False)
@shared_task(ignore_result=False,queue='event') 
def long_running_task(iterations) -> int:    
    result = 0
    logger.info('longing running')
    for i in range(iterations):
        result += i
        sleep(2) 
    # print(result)
    return result 

@shared_task(ignore_result=True,queue='event') 
def send_otp_email(email,otp):
    try:
        
        logger.info('Email : {}'.format(email))
        otp_email = OTPEmail(email)        
        otp_email.send_otp_email(email,otp)
        return True 
    except Exception as e:
        print(f"Signup Email : {e}")
        logger.info(f"Signup Email : {e}")
        return False 


@shared_task(ignore_result=True,queue='event') 
def send_change_pwd_email(email,otp):
    try:
        
        logger.info('Email : {}'.format(email))
        change_pwd_email = Change_Pwd_Email(email)        
        change_pwd_email.send_otp_email(email,otp)
        return True 
    except Exception as e:
        print(f"Change PWD Email : {e}")
        logger.info(f"Change PWD Email : {e}")
        return False 

if __name__ == '__main__':
    print(__name__)
