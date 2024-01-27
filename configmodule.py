from dotenv import dotenv_values
from flask import Flask
from celery import Celery, Task

class Config(object):    
    config=None   
    SECRET_KEY=''
    SQLALCHEMY_DATABASE_URI=''
    TOKEN_VALID_MIN=60
    JWT_TOKEN_LOCATIONS=''
    JWT_COOKIE_SECURE=False
   
    @classmethod
    def init(cls):  # Note: all caps
        Config.SQLALCHEMY_DATABASE_URI='mssql+pyodbc:///?odbc_connect={}'.format(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={cls.config['SQLALCHEMY_SERVER_NAME']};"
        f"DATABASE={cls.config['SQLALCHEMY_DB_NAME'] };"
        r"Trusted_Connection=yes;"
        )
        Config.SECRET_KEY=cls.config['FLASK_SECRET_KEY']        
        Config.TOKEN_VALID_MIN=cls.config['TOKEN_VALID_MIN']  
        # Config.JWT_TOKEN_LOCATION=cls.config['JWT_TOKEN_LOCATION']  
        Config.JWT_TOKEN_LOCATION=["cookies"]
        Config.JWT_COOKIE_SECURE=cls.config['JWT_COOKIE_SECURE']
    
    @classmethod
    def create_app(cls) -> Flask:
        cls.init()
        app = Flask(__name__)  
        app.config.from_mapping(
            CELERY=dict(
                broker_url=f"redis://{cls.config['REDIS_IP']}:{cls.config['REDIS_PORT']}/0",
                result_backend=f"redis://{cls.config['REDIS_IP']}:{cls.config['REDIS_PORT']}/0",
                task_ignore_result=True,
            ),
        )
        cls.celery_init_app(app)
        app.config.from_object(cls)
        return app
    
    @classmethod
    def celery_init_app(cls, app: Flask) -> Celery:
        class FlaskTask(Task):
            def __call__(self, *args: object, **kwargs: object) -> object:
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery_app = Celery(app.name, task_cls=FlaskTask)
        celery_app.config_from_object(app.config["CELERY"])
        celery_app.set_default()
        app.extensions["celery"] = celery_app
        return celery_app
   
class ProductionConfig(Config):
    config=dotenv_values("env/.prod")
   
class DevelopmentConfig(Config):
    config=dotenv_values("env/.dev")
 
class TestingConfig(Config):
    config=dotenv_values("env/.qa")
  
