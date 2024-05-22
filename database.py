from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import sessionmaker

# base model class
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(64), unique=True)
    password = Column(String(64))
    created_at = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.username


class JobDescription(Base):
    __tablename__ = 'job_description'
    id = Column(Integer, primary_key=True)
    job_title = Column(String(100), nullable=False)
    job_description = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, nullable=False)

    def __str__(self):
        return self.job_title


class Resume(Base):
    __tablename__ = 'resumes'
    id = Column(Integer, primary_key=True)
    resume_file = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer, nullable=False)

    def __str__(self):
        return self.full_name



# more classes for other tables

# utility functions
def open_db():
    engine = create_engine('sqlite:///project.db', echo=True)
    session = sessionmaker(bind=engine)
    return session()


def add_to_db(object):
    db = open_db()
    db.add(object)
    db.commit()
    db.close()


if __name__ == "__main__":
    # create engine
    # mysql settings
    # database_name = 'projectdb'
    # host = 'localhost'
    # username = 'root'
    # password = 'root'
    # port = 3306
    # engine = engine.create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}')
    # demo
    engine = create_engine('sqlite:///project.db', echo=True)
    Base.metadata.create_all(engine)