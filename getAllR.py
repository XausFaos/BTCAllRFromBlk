import json
import os
import sqlite3 as sql
import time


class RSaver:
    
    def __init__(self, path_save_db: str,name_db: str, path_to_data: str):
        if not os.path.exists(path_save_db):
            os.makedirs(path_save_db)
            
        self.path_save_db = path_save_db
        self.path_to_data = path_to_data
        self.name_db = name_db
        
        self.InitDb()
        
    
    def InitDb(self):
        self.db = sql.connect(self.path_save_db + self.name_db)
        with self.db:
            self.db_cursor = self.db.cursor()

            self.db_cursor.execute("CREATE TABLE IF NOT EXISTS 'R'(r TEXT, txid TEXT, pub TEXT, s TEXT)")
            self.db.commit()
    
    
    def SaveDb(self):
        self.db.commit()
        
    
    def AddR(self, r, s, pub, txid):
        self.db_cursor.execute(f"INSERT INTO 'R' VALUES ('{r}','{txid}','{pub}','{s}')")
    
    
    def GetR(self, r):
        self.db_cursor.execute(f"SELECT * FROM 'R' WHERE r='{r}'")
        return self.db_cursor.fetchall()
    
    
    def GetAllData(self):
        self.db_cursor.execute("SELECT * FROM 'R'")
        return self.db_cursor.fetchall()
    
    
    def GetOnlyR(self):
        self.db_cursor.execute("SELECT r FROM 'R'")
        return self.db_cursor.fetchall()
    
    
    def GetCountLine(self):
        self.db_cursor.execute("SELECT COUNT(*) FROM 'R'")
        return self.db_cursor.fetchall()[0][0]
    
    
    def GetFilesList(self) -> list:
        self.fileList = [i for i in os.listdir(self.path_to_data) if i.startswith("senders-")]
        return self.fileList
    
    def Start(self, fileList: list = []):
        if len(fileList) == 0:
            self.GetFilesList()
        else:
            self.fileList = fileList
        
        for file in self.fileList:
            timer = time.time()
            print(f"Start getR: {file}")
            self.thisFile = file
            with open(self.path_to_data + file, "r") as fileData:
                data = json.load(fileData, strict=False)
                print(f"    Count pub: {len(data)}")
                for pub in data.keys():
                    for tx in data[pub]:
                        r = tx[1]
                        s = tx[2]
                        txid = tx[0]
                        
                        self.AddR(r, s, pub, txid)
            print(f"    Save db...")
            self.SaveDb()
            print(f"    Time: {time.time() - timer}")
            print("[==========================================================]")
            
            
if __name__ == "__main__":
    
    path_save_db = "G:/Result/"
    name_db = "R.db"
    path_to_data = "C:/Bitcoin/Result/Senders/"
    
    fileList = ["senders-blk00000.json"]
    rsaver = RSaver(path_save_db, name_db, path_to_data)
    rsaver.Start(fileList)