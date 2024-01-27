from extensions import db
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, NVARCHAR, BOOLEAN, VARCHAR
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 
from sqlalchemy import func

def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return value.strftime("%Y-%m-%d %H:%M:%S")

class User(db.Model):
    __tablename__ = "tblUser"
    user_pk = Column(Integer, primary_key=True)
    name = Column(NVARCHAR(100),nullable=False)
    email = Column(NVARCHAR(100),nullable=False)
    siteurl = Column(VARCHAR(50),nullable=False)
    create_date = Column(DateTime,nullable=True)
    update_date = Column(DateTime,nullable=True)
    password = Column(VARCHAR(100),nullable=False)
    lang = Column(VARCHAR(2),nullable=True)

    def __repr__(self):
        return f"<User {self.siteurl}>"
    
    def set_password(self, password):
        self.password=generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_user_by_siteurl(cls, siteurl):
        return cls.query.filter_by(siteurl=siteurl).first()
    
    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def check_siteurl_exists(cls, siteurl):
        return cls.query.filter_by(siteurl=siteurl).count() > 0     
   
    @classmethod
    def check_email_exists(cls, email):
        return cls.query.filter_by(email=email).count() > 0

    def save(self):
        try:
            db.session.add(self)            
            db.session.commit()
            return True 
        except:
            return False 


    @property
    def to_dict(self):
       """Return object data in easily serializable format"""
       return {
           "user_pk"          : self.user_pk,
           "name"             : self.name,
           "email"            : self.email,
           "siteurl"          : self.siteurl,
           "create_date"      : dump_datetime(self.create_date)
       }

    
class Event(db.Model):
    __tablename__ = "tblEvent"
    event_pk = Column(Integer, primary_key=True)
    name = Column(NVARCHAR(200),nullable=False)
    start_date = Column(DateTime,nullable=True)
    end_date = Column(DateTime,nullable=True)
    description = Column(NVARCHAR(1000),nullable=True)
    url = Column(NVARCHAR(500),nullable=True)
    create_date = Column(DateTime,nullable=True)
    update_date = Column(DateTime,nullable=True)

    def __repr__(self):
        return f"<Event {self.name}>"
    
    @property
    def to_dict(self):
       """Return object data in easily serializable format"""
       return {
           "event_pk"         : self.event_pk,
           "name"             : self.name,
           "start_date"       : dump_datetime(self.start_date),
           "end_date"         : dump_datetime(self.end_date),
           "description"      : self.description,
           "url"              : self.url
       }


class EventJoin(db.Model):
    __tablename__ = "tblEventJoin"
    event_fk = Column(Integer, primary_key=True)
    user_fk = Column(Integer, primary_key=True)
    create_date = Column(DateTime,nullable=True)
    update_date = Column(DateTime,nullable=True)
    url = Column(NVARCHAR(500),nullable=True)
    video_name = Column(NVARCHAR(100),nullable=True)
    image_name = Column(NVARCHAR(100),nullable=True)
    video_desc = Column(NVARCHAR(500),nullable=True)
    is_publish = Column(BOOLEAN,nullable=True)
    
    def __repr__(self):
        return f"<EventJoin {self.video_name}  {self.url}>"
    
    @property
    def to_dict(self):
       """Return object data in easily serializable format"""
       return {
           "event_fk"         : self.event_fk,
           "user_fk"          : self.user_fk,
           "url"              : self.url,
           "video_name"       : self.video_name,
           "image_name"       : self.image_name,
           "video_desc"       : self.video_desc,
           "is_publish"       : self.is_publish
    }

class OTP(db.Model):
    __tablename__ = "tblOTP"
    otp_pk = Column(Integer, primary_key=True)
    #siteurl = Column(VARCHAR(50),nullable=False)  
    otp_type = Column(VARCHAR(10),nullable=False)   
    otp = Column(VARCHAR(6),nullable=False)
    create_date = Column(DateTime,nullable=True)
    expiry_date = Column(DateTime,nullable=True)
    email = Column(NVARCHAR(100),nullable=False)    
    is_used = Column(Boolean,nullable=False)    

    def save(self):
        try:
            db.session.add(self)            
            db.session.commit()
            return True 
        except:
            return False 
    
    @classmethod
    def fetch_otp(self,email,otp,otp_type):        
        try:
            otp_record=self.query.filter(self.email==email, self.expiry_date >= datetime.now(), self.otp_type==otp_type, self.otp==otp).first()
   
            return otp_record 
        except:
            return None
        
    @classmethod
    def verify_otp(cls, email, otp, otp_type):
        verify_otp=cls.query.filter(cls.email==email, cls.expiry_date >= datetime.now(), cls.otp_type==otp_type, cls.is_used==False).order_by(cls.expiry_date.desc()).first()
        
        if verify_otp:
            if verify_otp.otp.strip()==otp.strip():
                return True
                
        return False
        