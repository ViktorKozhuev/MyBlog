import math
import re
import sqlite3
import time
from flask import url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addPost(self, title, text, url):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE'{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Статья с таким url уже существует')
                return False

            base = url_for('static', filename='images_html')

            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NUll, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи ' + str(e))
            return False
        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res

        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return (False, False)

    def deletePost(self, alias):
        try:
            self.__cur.execute(f"DELETE FROM posts WHERE url LIKE '{alias}'")
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

    def updatePost(self,alias, title, text):
        try:
            base = url_for('static', filename='images_html')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>",
                          "\\g<tag>" + base + "/\\g<url>>",
                          text)
            url = alias
            self.__cur.execute(f"UPDATE posts SET title=?, text=? WHERE url LIKE'{url}'", (title, text))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка редактирования статьи ' + str(e))
            return False
        return True

    def getPostAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

        return []

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE email LIKE'{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Пользователь с таким email уже существует')
                return False
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NUll, ?, ?, ?, NUll, ?, ?)", (name, email, hpsw, 0, tm))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка добавления пользователя " + str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД getUser " + str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД getUserByEmail " + str(e))
        return False

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id =?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД " + str(e))
            return False

        return True

    def deleteUser(self, user_id):
        try:
            self.__cur.execute(f"DELETE FROM users WHERE id =?", (user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

    def setUserActive(self, user_id):
        try:
            self.__cur.execute(f"UPDATE users SET is_active=1 WHERE id =?", (user_id) )
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))


    def getusersavatar(self, user_id):
        img = None
        try:
            self.__cur.execute(f"SELECT avatar FROM users WHERE id = '{user_id}' LIMIT 1 ")
            img = self.__cur.fetchone()['avatar']
        except sqlite3.Error as e:
            print("Ошибка получения аватара пользователя " + str(e))
        return img


    def addComment(self, user_id, post_url, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute(f"SELECT id FROM posts WHERE url = '{post_url}' ")
            res = self.__cur.fetchone()
            post_id = res[0]
            # print(user_id, post_id,  text,  tm)
            self.__cur.execute(f"INSERT into comments VALUES(NUll, ?, ?, ?, ?)", (user_id, post_id, text,  tm))
            self.__db.commit()

        except sqlite3.Error as e:
            print("Ошибка добавления комментария в БД " + str(e))
            return False

    def showComments(self, post_url):
        lst = []
        try:
            self.__cur.execute(
                f'''SELECT users.id, users.avatar, users.name, comments.text, comments.time 
                FROM comments
                JOIN users ON comments.user_id = users.id
                JOIN posts ON comments.post_id = posts.id
                WHERE posts.url = '{post_url}'
                '''
            )
            lst = self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return lst


    def deletecomment(self, comment_id):
        try:
            self.__cur.execute(f"DELETE FROM comments WHERE id =?", (comment_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))

    def updateresume(self, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute(f"UPDATE resume SET text=?, time=? ", (text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка редактирования резюме ' + str(e))
            return False
        return True

    def getresume(self):
        try:
            self.__cur.execute(f"SELECT text, time FROM resume LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return (False, False)

    def add_message(self, user_id, text):
        try:
            tm = math.floor(time.time())
            self.__cur.execute(f"INSERT into feedback VALUES(NUll, ?, ?, ?)", (user_id, text, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления комментария в БД " + str(e))
        return False

    def show_messages(self):
        lst = []
        try:
            self.__cur.execute(
                f'''SELECT users.name, users.email, feedback.text,  feedback.time 
                        FROM feedback
                        JOIN users ON feedback.user_id = users.id
                        '''
            )
            lst = self.__cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка чтения из БД " + str(e))
        return lst





