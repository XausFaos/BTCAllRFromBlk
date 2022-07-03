import blkParser
import GetTxsOnAddresses
import getAllR
import json
import os

class Analyzer:
    
    def __init__(self, _blkParser, _getTxsOnAddresses, _getAllR):
        self.blkParser = _blkParser
        self.getTxsOnAddresses = _getTxsOnAddresses
        self.getAllR = _getAllR
    
    def Recovery(self):
        print("[============= Recovery =============]\n")
        errFile = self.getAllR.thisFile
        errFileblk = errFile.replace("senders-", "").replace("json", "dat")
        errFileTx = errFileblk.replace("dat", "json")
        print(f"Error in: {errFile} starting recovery")
        
        print(f"Start parse block: {errFileblk}")
        self.blkParser.Repair(errFileblk)
        
        print(f"Get txs on addresses: {errFileTx}")
        self.getTxsOnAddresses.Recovery(errFileTx)
        
        newFiles = self.getAllR.GetFilesList()
        newIndex = newFiles.index(errFile) - 1
        
        if newIndex < 0:
            newIndex = 0
            
        newFiles = newFiles[newIndex:]
        
        print(f"Clear temp files")
        os.remove(self.blkParser.result_path + errFileTx)
        print(f"Remove: {errFileblk}")
        
        print("[========= Recovery finished ========]\n")

        
        try:
            self.getAllR.Start(newFiles)
        except json.decoder.JSONDecodeError:
            self.Recovery()      
            
    def Start(self):
        try:
            self.getAllR.Start()
            
        except json.decoder.JSONDecodeError:
            self.Recovery()
            
if __name__ == "__main__":
    
    blkParser = blkParser.ParserBlk("D:/Bitcoin/Data/Blocks/", "G:/Result/ParserBlk/")
    getTxsAddr = GetTxsOnAddresses.GetAddressOnTx("G:/Result/ParserBlk/", "C:/Bitcoin/Result/Senders/")
    getR = getAllR.RSaver("G:/Result/", "R.db", "C:/Bitcoin/Result/Senders/")

    analyzer = Analyzer(blkParser, getTxsAddr, getR)
    analyzer.Start()
    # blk -> getTxs -> getR