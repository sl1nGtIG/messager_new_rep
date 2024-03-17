from pydantic import BaseModel


################################################################################
# User schema

class LoginRequest(BaseModel):
    email: str
    password: str


class UserBase(BaseModel):
    user_id: str
    firstname: str
    secondname: str
    email: str
    school: str
    city: str
    age: str
    targetClass: str
    avatar: str
    email: str
    password: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    pass

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    newFirstName: str
    newSecondName: str
    fileName: str


################################################################################

################################################################################
# Message shema


class MessageBase(BaseModel):
    message_id: str
    id_chat: str
    id_sender: str
    content: str
    time: int
    type: int


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    pass

    class Config:
        from_attributes = True


################################################################################

################################################################################
# Chat schema


class ChatBase(BaseModel):
    chat_id: str
    user_id_1: str
    user_id_2: str


class ChatCreate(ChatBase):
    messages: list


class Chat(ChatBase):
    pass

    class Config:
        from_attributes = True


class ChatDelete(BaseModel):
    chatsId: list


class DataForCreateChat(BaseModel):
    message: Message
    chat: ChatBase


################################################################################


class ListForDeleteChat(BaseModel):
    chatsForDelete: list
