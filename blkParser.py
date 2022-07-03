import os
import hashlib
import BlockParser
import json
from multiprocessing import Process

class RPC():
    
    def __init__(self, _block_path: str, _result_path: str) -> None:
        self.block_path = _block_path
        self.result_path = _result_path

        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)


    def get_list_blocks_file(self) -> list:
        data = []
        
        for file in os.listdir(self.block_path):
            if file.startswith("blk"):
                data.append(file)
                
        return data


    def save_result(self, path_result: str, obj: dict) -> None:
        with open(path_result, "w") as file:
            json.dump(obj, file, indent=4)
            
class ParserBlk:
    
    def __init__(self, _block_path: str, _result_path: str, _count_thread: int = 0) -> None:
        self.block_path = _block_path
        self.result_path = _result_path
        
        self.rpc = RPC(self.block_path, self.result_path)
        self.count_thread = _count_thread
            
        if not os.path.exists(self.result_path):
            os.makedirs(self.result_path)

        self.fileList = self.GetFilesList()
    

    def GetFilesList(self):
        
        data = []
        
        for file in self.rpc.get_list_blocks_file():
            fname = f"{file.split('.')[0]}.json"
            
            if fname not in os.listdir(self.rpc.result_path):
                data.append(fname)

    def GetFilesListsForThread(self) -> list:
        data = []
        count_in_thread = len(self.fileList) // self.count_thread
        
        while count_in_thread * self.count_thread < len(self.fileList):
            count_in_thread += 1
        
        for i in range(self.count_thread):
            fileForThr = self.fileList[i*count_in_thread : (i + 1) * count_in_thread]
            data.append(fileForThr)
            
        return data
    
    def RunThread(self,fileList: list) -> None:
        for file in fileList:
            data = BlockParser.parseBlock(self.rpc.block_path + file)
            self.rpc.save_result(self.rpc.result_path + f"{file.replace('.dat', '')}.json", data)
                
    def Run(self, fileList : list = []) -> None:
        if len(fileList) != 0:
            self.fileList = fileList
        else:
            self.fileList = self.GetFilesList()
            
        if self.count_thread == 0:
            if len(self.fileList) < 12:
                self.count_thread = len(self.fileList)
            else:
                self.count_thread = 1
        
        filesForThread = self.GetFilesListsForThread()
        
        for files in filesForThread:
            Process(target=self.RunThread, args=(files,)).start()
    
    def Repair(self, file) -> None:
        self.RunThread([file])
        
if __name__ == "__main__":
    
    block_path = "D:/Bitcoin/Data/Blocks/"
    result_path = "G:/Result/ParserBlk/"
    
    blkParser = ParserBlk(block_path, result_path)

    fileList = ["blk00000.dat"]
    blkParser.fileList = fileList
    
    blkParser.Run()