from sqlalchemy import Column, String, JSON, BigInteger
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, unique=True, index=True)
    firstname = Column(String)
    secondname = Column(String)
    school = Column(String)
    city = Column(String)
    age = Column(String)
    targetclass = Column(String)
    avatar = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(String, primary_key=True, unique=True, index=True)
    user_id_1 = Column(String)
    user_id_2 = Column(String)
    messages = Column(JSON)
    mes_text = Column(String)
    mes_time = Column(BigInteger)


class UsersChats(Base):
    __tablename__ = "anotherusers"

    user_id = Column(String, primary_key=True, unique=True, index=True)
    another_users_id = Column(JSON)
    
