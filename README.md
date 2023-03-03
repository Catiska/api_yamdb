# Групповой проект по курсу "API: интерфейс взаимодействия программ" - YaMDb

### Описание
Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). 
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.
Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.

### Технологии
![python version](https://img.shields.io/badge/Python-3.9-yellowgreen?logo=python)
![django version](https://img.shields.io/badge/Django-2.2-yellowgreen?logo=django)
![djangorestframework version](https://img.shields.io/badge/djangorestframework-3.12-yellowgreen?logo=django)
![pytest version](https://img.shields.io/badge/pytest-6.2-yellowgreen?logo=pytest)
![sqlite version](https://img.shields.io/badge/SQLite-3-yellowgreen?logo=sqlite)
![requests version](https://img.shields.io/badge/requests-2.26-yellowgreen)

#### Функционал

- Аутентификация по JWT-токену.
- Чтение для анонимных пользователей.
- Управление пользователями.
- Получение списка всех категорий и жанров, добавление и удаление.
- Получение списка всех произведений, их добавление.Получение, обновление и удаление конкретного произведения.
- Получение списка всех отзывов, их добавление.Получение, обновление и удаление конкретного отзыва.  
- Получение списка всех комментариев, их добавление.Получение, обновление и удаление конкретного комментария.
- Возможность получения подробной информации о себе и удаления своего аккаунта.
- Фильтрация по полям.

### Примеры запросов

- Регистрация пользователя:  
``` POST /api/v1/auth/signup/ ```  
- Получение данных своей учетной записи:  
``` GET /api/v1/users/me/ ```  
- Добавление новой категории:  
``` POST /api/v1/categories/ ```  
- Удаление жанра:  
``` DELETE /api/v1/genres/{slug} ```  
- Частичное обновление информации о произведении:  
``` PATCH /api/v1/titles/{titles_id} ```  
- Получение списка всех отзывов:  
``` GET /api/v1/titles/{title_id}/reviews/ ```   
- Добавление комментария к отзыву:  
``` POST /api/v1/titles/{title_id}/reviews/{review_id}/comments/ ```

С полным списком эндпоинтов и примерами запросов/ответов можно ознакомиться после запуска dev-сервера по ссылке:
``` http://localhost:8000/redoc/ ```


### Запуск проекта в dev-режиме

- Клонировать репозиторий и перейти в него в командной строке:
``` git clone <ссылка на репозиторий по ssh-ключу> ```
``` cd api_final_yatube ```
- Cоздать и активировать виртуальное окружение:
``` python -m venv venv ```
``` source venv/Script/activate```
``` python -m pip install --upgrade pip ```
- Установить зависимости из файла requirements.txt:
``` pip install -r requirements.txt ```
- Выполнить миграции:
``` python manage.py migrate ```
- Запустить проект:
``` python manage.py runserver ```

После запуска сервера подробная документация доступна по адресу: http://localhost:8000/redoc/
### Авторы
- 🐱‍💻 Ростислав Житков (Teamlead) - [https://github.com/Zulusssss](https://github.com/Zulusssss)
- 🐱‍👓 Екатерина Мындреско - [https://github.com/Catiska](https://github.com/Catiska)
- 🐱‍👤 Манойлов Илья - [https://github.com/pyttho](https://github.com/pyttho)
