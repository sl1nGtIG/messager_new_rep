"""
pg_lsclusters
sudo chmod 700 /var/lib/postgresql/16/main
sudo chown -R postgres:postgres /var/lib/postgresql/16/main
sudo pg_ctlcluster 16 main start
"""

# for test
# post chat
{
    "message": {
        "message_id": "1",
        "id_chat": "chatid",
        "id_sender": "user1",
        "content": "text by user1",
        "time": 10,
        "type": 1,
    },
    "chat": {"chat_id": "chatid", "user_id_1": "user1", "user_id_2": "user2"},
}

# post message
{
    "message_id": "3",
    "id_chat": "chatid",
    "id_sender": "user1",
    "content": "text by user2",
    "time": 30,
    "type": 2,
}
