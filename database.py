import uuid
import sqlite3
from datetime import datetime


class Status():
    def __init__(self):
        self.uploaded = "UPLOADED"
        self.processing = "PROCESSING"
        self.completed = "COMPLETED"
        self.error = "ERROR"
        self.removed = "REMOVED"

STATUS = Status()
class Database():
    def __init__(self, path:str) :
        self.path = path
        self.create_database()

    def get_connection(self):
        return sqlite3.connect(self.path)
    
    def create_database(self) -> bool:
        try:
            connection = self.get_connection()
            connection.cursor().execute('''CREATE TABLE IF NOT EXISTS videos
                        (id TEXT PRIMARY KEY ,
                        name TEXT,
                        upload_datetime DATETIME,
                        proportion FLOAT,
                        audio INT,
                        type TEXT,
                        saved_name TEXT,
                        summary_name TEXT,
                        status TEXT)''')
            connection.commit()
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False
        
    def insert_video(self, video_name:str, type:str, datetime:datetime, proportion:float, audio:int, saved_name:str, status:str=STATUS.uploaded):
        try:
            connection = self.get_connection()
            id = str(uuid.uuid4())
            connection.cursor().execute("INSERT INTO videos VALUES (?,?,?,?,?,?,?,?,?)",
                                        (id, video_name, datetime, proportion, audio, type, saved_name, "", status))
            connection.commit()
            connection.close()
            return id
        except Exception as e:
            print(e)
            return None
        
    
    def remove_video(self, video_id):
        connection = self.get_connection()
        connection.cursor().execute("DELETE FROM videos WHERE id=?", (video_id))
        connection.commit()
        connection.close()

    def get_video_field(self, video_id:str, field:str):
        try:
            connection = self.get_connection()
            result = connection.cursor().execute(f"SELECT {field.lower()} FROM videos WHERE id=?", (video_id,)).fetchone()
            connection.close()
            if result is not None:
                return result[0]
            return result
        except Exception as e:
            print(e)
            return None
        
    
    def update_video(self, video_id:str, field:str, value):
        try:
            connection = self.get_connection()
            connection.cursor().execute(f"UPDATE videos SET {field.lower()}=? WHERE id=?", (value, video_id))
            connection.commit()
            connection.close()
        except Exception as e:
            print(e)

    def get_video_to_process(self):
        try:
            connection = self.get_connection()
            result = connection.cursor().execute(f"SELECT * FROM videos WHERE status = '{STATUS.uploaded}' ORDER BY upload_datetime ASC").fetchall()
            connection.close()
            if result is not None:
                if len(result) > 0:
                    result = result[0]
                    video = {}
                    video['id'] = result[0]
                    video['name'] = result[1]
                    video['upload_datetime'] = result[2]
                    video['proportion'] = result[3]
                    video['audio'] = result[4]
                    video['type'] = result[5]
                    video['saved_name'] = result[6]
                    video['summary_name'] = result[7]
                    video['status'] = result[8]
                    return video
            return None
        except Exception as e:
            print(e)
            return None

DATABASE = Database('videos.db')