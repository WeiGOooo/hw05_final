# hw05_final
### Проект hw05_final
***

### Возможности:
* создание постов с картинками
* комментирование постов
* подписка на автора поста

***
### Как запустить проект:
```
git clone https://github.com/WeiGOooo/hw05_final.git
```
Создать и активировать виртуальное окружение:
```
python -m venv env

source venv/bin/activate
```
Обновить pip
```
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Выполнить миграции:
```
python manage.py migrate
```
Запустить сервер:
```
python manage.py runserver
```
Ссылка на локальный сервер:
http://127.0.0.1:8000/
