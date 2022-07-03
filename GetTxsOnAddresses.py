import json
import os
from multiprocessing import Process

default_path = "G:/Result/"
save_path = "C:/Bitcoin/Result/Senders/"

def GetJson(filePath: str):
    with open(filePath, "r") as file:
        return json.load(file, strict=False)

class GetAddressOnTx:
    
    def __init__(self, _block_path: str, _result_path: str, _count_thread: int = 0) -> None:
        self.block_path = _block_path
        self.result_path = _result_path
        
        self.count_thread = _count_thread
    
    def GetFilesList(self):
        self.fileList = os.listdir(self.block_path)
    
    def GetFilesListsForThread(self) -> list:
        data = []
        count_in_thread = len(self.fileList) // self.count_thread
        
        while count_in_thread * self.count_thread < len(self.fileList):
            count_in_thread += 1
        
        for i in range(self.count_thread):
            data.append(self.fileList[i * count_in_thread : (i + 1) * count_in_thread])
        
        return data
    
    def Thread(self, listBlockFile):
        for file in listBlockFile:
        
            txidLst = {}
            hashLst = {}
            
            data = GetJson(self.block_path + file)
            
            for block in data:
                for txs in block["txs"]:
                    
                    hashTx = txs["hash"]
                    inputTx = []
                    
                    for inputt in txs["inputs"]:
                        if inputt["txid"] == "0000000000000000000000000000000000000000000000000000000000000000":
                            continue
                        if None in inputt["dataSig"].values():
                            continue
                        
                        inputTx.append(inputt)
                    
                    hashLst[hashTx] = inputTx
                    
                    for tx in inputTx:
                        txid = tx["txid"]
                        data = tx["dataSig"]
                        if txid in txidLst.keys():
                            txidLst[txid].append(data)
                        else:
                            txidLst[txid] = [data]
                                    
            senders = {}
            
            for txid in txidLst.keys():
                if txid in hashLst.keys():
                    for tx in hashLst[txid]:
                        pubSenders = tx["dataSig"]["Pub"]
                        
                        R = tx["dataSig"]["R"]
                        S = tx["dataSig"]["S"]
                        save = [txid,R,S]
                        
                        if pubSenders in senders.keys():
                            if save not in senders[pubSenders]:
                                senders[pubSenders].append(save)
                        else:
                            senders[pubSenders] = [save]
                    

            with open(save_path + f"senders-{file.split('.')[0]}.json", "w") as file:
                json.dump(senders, file, indent=4) 
    
    def Recovery(self, file):
        self.Thread([file])
            
    def Start(self, fileList: list = []):
        self.fileList = fileList

        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)
        
        if len(fileList) == 0:
            self.GetFilesList()
            
        if self.count_thread == 0:
            if len(self.fileList) < 12:
                self.count_thread = len(self.fileList)
            else:
                self.count_thread = 1
        
        filesForThread = self.GetFilesListsForThread()
        
        for i in range(self.count_thread):
            Process(target=self.Thread, args=(filesForThread[i],)).start()
            
            
if __name__ == "__main__":
    default_path = "G:/Result/ParserBlk/"
    save_path = "C:/Bitcoin/Result/Senders/"
    
    fileList = ["blk00000.json"]
    adressesTx = GetAddressOnTx(default_path, save_path)
    adressesTx.Start(fileList)