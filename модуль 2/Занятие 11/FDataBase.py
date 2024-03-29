import sqlite3
import time
import math
import re
from flask import url_for

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким url уже существует")
                return False

            base = url_for('static', filename='images_html')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД "+str(e))
            return False

        return True
    
    def getPost(self, alias):
        sql = f"SELECT title, text FROM posts WHERE url = {alias} LIMIT 1"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchone()
            if res == True:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД"+ str(e))
        return (False , False)
    def getPostAnonce(self):
        sql = "SELECT url, title, text FROM posts ORDER BY time DESC"
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения анонсов статей из БД"+ str(e))
        return []
    def addUser(self, name, email, hpsw):
        sql = "INSERT INTO users(name, email, psw) VALUES(name,email,hpsw)"
        try:
            self.__cur.execute(sql)
            return True
        except sqlite3.Error as e:
            print("Ошибка получения анонсов статей из БД"+ str(e))
        return False