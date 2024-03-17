import aiopg, json
from app import config, schemas


################################ CRUD for User #################################
# Log in for User
async def get_log_in_user(email: str, password: str):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users")
            all_users = await cursor.fetchall()

            for user in all_users:
                if user[8] == email and user[9] == password:
                    user_id = user[0]
                    return user_id
            return False


# Post for User
# fmt: on
async def create_user(data: schemas.UserCreate):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            # Checking if there is a user with the same user_id
            await cursor.execute("SELECT * FROM users WHERE email = %s", (data.email,))
            existing_user = await cursor.fetchone()
            if existing_user:
                return {"error": "пользователь с таким логином уже зарегестрирован"}

            await cursor.execute(
                "INSERT INTO users (user_id, firstname, secondname, school, city, age, targetclass, avatar, email, password) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    data.user_id,
                    data.firstname,
                    data.secondname,
                    data.school,
                    data.city,
                    data.age,
                    data.targetClass,
                    data.avatar,
                    data.email,
                    data.password,
                ),
            )


# Get for User
# fmt: off
class GetProfileInfo:
    def __init__(self, user_id, firstname, secondname, school, 
                 city, age, targetClass, avatar, email, password):
        self.user_id = user_id
        self.firstname = firstname
        self.secondname = secondname
        self.school = school
        self.city = city
        self.age = age
        self.targetClass = targetClass
        self.avatar = avatar
        self.email = email
        self.password = password

# fmt: on


async def get_user_by_user_id(user_id: str):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user_data = await cursor.fetchone()

            # Checking if the user exists
            if not user_data:
                return {"error": "пользователь не найден"}

            # The user exists
            if user_data:
                profileinfo = GetProfileInfo(
                    user_id=user_data[0],
                    firstname=user_data[1],
                    secondname=user_data[2],
                    school=user_data[3],
                    city=user_data[4],
                    age=user_data[5],
                    targetClass=user_data[6],
                    avatar=user_data[7],
                    email=user_data[8],
                    password=user_data[9],
                )
                result = {"user": profileinfo.__dict__}
                return result


# Update for User
async def update_user(data: schemas.UserUpdate, user_id: str):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            # Проверяем существование user по его user_id
            await cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            existing_user = await cursor.fetchone()
            if not existing_user:
                return {"error": "Пользователь не существует"}

            # Обновляем данные пользователя
            await cursor.execute(
                "UPDATE users SET firstname = %s, secondname = %s, avatar = %s WHERE user_id = %s",
                (data.newFirstName, data.newSecondName, data.fileName, user_id),
            )

            return {"message": "Пользователь успешно обновлено"}


################################################################################

############################## CRUD for message ################################
# Post for Message


async def add_message(message: schemas.MessageBase):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:

            await cursor.execute(
                "SELECT * FROM chats WHERE chat_id = %s", (message.id_chat,)
            )
            chat_query = await cursor.fetchone()

            if not chat_query:
                return {"error": "не существует чата с таким id"}

            current_messages = chat_query[3] or []
            new_message = {
                "message_id": message.message_id,
                "id_sender": message.id_sender,
                "id_chat": message.id_chat,
                "content": message.content,
                "time": message.time,
                "type": message.type,
            }
            current_messages.append(new_message)

            new_text = "Голосовое сообщение" if message.type == 2 else message.content
            # print(f'new_text - {new_text}')

            await cursor.execute(
                "UPDATE chats SET messages = %s, mes_text = %s, mes_time = %s WHERE chat_id = %s",
                (json.dumps(current_messages), new_text, message.time, message.id_chat),
            )
            return {"message": "Сообщение успешно добавлено"}


# Get for Messages
async def get_messages(chat_id):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM chats WHERE chat_id = %s", (chat_id,))
            entry = await cursor.fetchone()
            messages = entry[3] if entry else []
            return messages[::-1]


################################################################################


############################### CRUD for chat ##################################
# post for Chat
async def create_chat(data: schemas.ChatCreate):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            # Checking if there is a chat with the same chat_id
            await cursor.execute(
                "SELECT * FROM chats WHERE chat_id = %s", (data.chat_id,)
            )
            existing_chat = await cursor.fetchone()
            if existing_chat:
                return {"error": "чат уже существует"}

            await cursor.execute(
                "INSERT INTO chats (chat_id, user_id_1, user_id_2, messages, mes_text, mes_time) \
                    VALUES (%s, %s, %s, %s, %s, %s)",
                (data.chat_id, data.user_id_1, data.user_id_2, json.dumps([]), "", 0),
            )
            # добавляем chat_id в список всех чатов для пользователя
            await add_another_users_id(
                user_id=data.user_id_1, another_id=data.user_id_2
            )
            await add_another_users_id(
                user_id=data.user_id_2, another_id=data.user_id_1
            )


# Get for Chat
class ChatForGet:
    def __init__(
        self, chat_id, user_id_1, user_id_2, mes_text, mes_time, avatar, nickname
    ):
        self.chat_id = chat_id
        self.user_id_1 = user_id_1
        self.user_id_2 = user_id_2
        self.mes_text = mes_text
        self.mes_time = mes_time
        self.nickname = nickname
        self.avatar = avatar


def elem_of_chats_db(chat):
    chat_id = chat[0]
    user_id_1 = chat[1]
    user_id_2 = chat[2]
    messages = chat[3]
    return (chat_id, user_id_1, user_id_2, messages)


def chat_construct(user_data, chat_id, user_id_1, user_id_2, messages):
    firstname = user_data[1]
    secondname = user_data[2]
    avatar = user_data[7]
    nickname = f"{firstname} {secondname}"

    chat_to_get = ChatForGet(
        chat_id=chat_id,
        user_id_1=user_id_1,
        user_id_2=user_id_2,
        mes_text=messages[-1]["content"],
        mes_time=messages[-1]["time"],
        nickname=nickname,
        avatar=avatar,
    )
    return chat_to_get


async def get_chats(user_id: str):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            # предполагаем что заправшиваемый user имеет id_1 (в рамках чата)
            await cursor.execute("SELECT * FROM chats WHERE user_id_1 = %s", (user_id,))
            chats_db_1 = await cursor.fetchall()

            if chats_db_1:

                response = []
                for chat in chats_db_1:
                    chat_id, user_id_1, user_id_2, messages = elem_of_chats_db(chat)
                    # получаем информацию от второго usera
                    await cursor.execute(
                        "SELECT * FROM users WHERE user_id = %s", (user_id_2,)
                    )
                    user_data = await cursor.fetchone()
                    if user_data:
                        chat_to_get = chat_construct(
                            user_data, chat_id, user_id_1, user_id_2, messages
                        )
                        response.append(chat_to_get.__dict__)
                    else:
                        return {"error": "второй пользователь не найден"}
                # если все успешно
                if response:
                    return response
            else:
                # запрашиваемый user имеет id_2 (в рамках чата)
                await cursor.execute(
                    "SELECT * FROM chats WHERE user_id_2 = %s", (user_id,)
                )
                chats_db_2 = await cursor.fetchall()

                response = []
                for chat in chats_db_2:
                    chat_id, user_id_1, user_id_2, messages = elem_of_chats_db(chat)

                    # получаем информацию от второго usera
                    await cursor.execute(
                        "SELECT * FROM users WHERE user_id = %s", (user_id_1,)
                    )
                    user_data = await cursor.fetchone()
                    if user_data:
                        chat_to_get = chat_construct(
                            user_data, chat_id, user_id_1, user_id_2, messages
                        )
                        response.append(chat_to_get.__dict__)
                    else:
                        return {"error": "второй пользователь не найден"}
                if response:
                    return response
                return []


async def del_chats(data):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:

            for chat_id in data:
                # получаем user_id_1 и user_id_2 из чата перед его удалением
                await cursor.execute(
                    "SELECT * FROM chats WHERE chat_id = %s", (chat_id,)
                )
                chat = await cursor.fetchone()
                user_id_1 = chat[1]
                user_id_2 = chat[2]

                # удаление чата
                await cursor.execute("DELETE FROM chats WHERE chat_id = %s", (chat_id,))
                if cursor.rowcount == 0:
                    return {"error": "один из чатов не был найден"}

                # удаляем user_id второго для 1 пользователя
                await cursor.execute(
                    "SELECT * FROM anotherusers WHERE user_id = %s", (user_id_1,)
                )
                user1 = await cursor.fetchone()
                ids_for_user1 = user1[1]
                ids_for_user1.remove(user_id_2)

                await cursor.execute(
                    "UPDATE anotherusers SET another_users_id = %s WHERE user_id = %s",
                    (json.dumps(ids_for_user1), user_id_1),
                )

                # удаляем user_id первого для 2 пользователя
                await cursor.execute(
                    "SELECT * FROM anotherusers WHERE user_id = %s", (user_id_2,)
                )
                user2 = await cursor.fetchone()
                ids_for_user2 = user2[1]
                ids_for_user2.remove(user_id_1)

                await cursor.execute(
                    "UPDATE anotherusers SET another_users_id = %s WHERE user_id = %s",
                    (json.dumps(ids_for_user2), user_id_2),
                )


################################################################################

################################################################################
# Anotherusers


async def add_another_users_id(user_id: str, another_id: str):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            # Проверяем, существует ли запись с данным user_id
            await cursor.execute(
                "SELECT * FROM anotherusers WHERE user_id = %s", (user_id,)
            )
            existing_entry = await cursor.fetchone()
            if existing_entry:
                # Проверяем, есть ли указанный another_id в списке
                if another_id not in existing_entry[1]:
                    new_another_id = existing_entry[1]
                    new_another_id.append(another_id)
                    await cursor.execute(
                        "UPDATE anotherusers SET another_users_id = %s WHERE user_id = %s",
                        (json.dumps(new_another_id), user_id),
                    )

            # Добавляем новую запись
            else:
                new_another_id = []
                new_another_id.append(another_id)
                await cursor.execute(
                    "INSERT INTO anotherusers (user_id, another_users_id) VALUES (%s, %s)",
                    (
                        user_id,
                        json.dumps(new_another_id),
                    ),
                )


# Get choose for User
class usersForChoose:
    def __init__(self, id, foto, nickname):
        self.id = id
        self.foto = foto
        self.nickname = nickname


async def get_choose_user(user_id: str):
    async with aiopg.connect(**config.db_params) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM anotherusers WHERE user_id = %s", (user_id,)
            )
            entry = await cursor.fetchone()
            another_users_id = entry[1] if entry else []
            another_users_id.append(user_id)

            await cursor.execute("SELECT * FROM users")
            all_users = await cursor.fetchall()

            result = []
            for user in all_users:
                if user[0] not in another_users_id:
                    get_user = usersForChoose(
                        id=user[0], foto=user[7], nickname=user[1] + user[2]
                    )
                    result.append(get_user.__dict__)
            return {"UsersForNewChatResponse": result}


################################################################################


async def pagination(page: int, size: int) -> list:
    corrected_page = page - 1 if page > 0 else 0
    offset_min = corrected_page * size
    offset_max = (corrected_page + 1) * size
    return offset_min, offset_max


################################################################################
