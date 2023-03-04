import csv, sqlite3
from django.core.management.base import BaseCommand
from reviews.models import *

from api_yamdb.settings import BASE_DIR

from pathlib import Path

class Command(BaseCommand):
    """
    Эта команда предназначена для импорта csv-файлов в БД.
    Названия файлов должны совпадать с БД.
    Файлы должны содержать правильные названия полей,
    правильные значения полей.
    Также присутствует зависимость от названия приложения,
    в котором создавалась БД, и от места расположения папки
    с файлами в каталоге проекта.
    """

    def handle(self, *args, **options):
        directory = BASE_DIR / 'static/data'
        pathlist = Path(directory).glob('*.csv')
        NAME = [path.stem for path in pathlist]

        con = sqlite3.connect("db.sqlite3")
        cur = con.cursor()

        for k in range(0,len(NAME)):
            with open(f'static/data/{NAME[k]}.csv','r', encoding='utf-8') as fin:
                dr = csv.DictReader(fin)
                to_db = [tuple(i.values()) for i in dr]

            cur.executemany(f"INSERT INTO reviews_{NAME[k]} {tuple(dr.fieldnames)} VALUES (" + "?, "*(len(dr.fieldnames)-1) + "?);", to_db)
            con.commit()

        con.close()