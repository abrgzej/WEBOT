from requests import get

di = {
    "email": "test4@test.ru",
    "password": "qwe",
    "chat_id": "1",
    "message": "test",
}

print(get('http://127.0.0.1:5055/api/message', json=di).json())