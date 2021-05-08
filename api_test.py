from requests import get, post, delete

print(get('http://127.0.0.1:5000/api/books').json())

print(get('http://127.0.0.1:5000/api/books/1').json())

print(post('http://127.0.0.1:5000/api/books').json())

print(post('http://127.0.0.1:5000/api/books', json={'title': 'Заголовок'}).json())

print(post('http://127.0.0.1:5000/api/books',
           json={'title': 'Заголовок',
                 'author': 'Пушкин',
                 'year': 2019,
                 'user_id': 1,
                 'is_private': False}).json())

print(delete('http://localhost:5000/api/books/999').json())
# новости с id = 999 нет в базе

print(delete('http://localhost:5000/api/books/1').json())
