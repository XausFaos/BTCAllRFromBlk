
import os
import datetime
import hashlib
import json
import hashlib

delkeyinputs = ["vout",
                "sigSize",
                "sig",
                #"dataSig",
                "sequence"
                #"txid",
                ]

delkeysave =   ["version",
                "inputCount",
                #"inputs",
                #"hash",
                "outCount",
                "outs",
                "witness",
                "lock time",
                "raw"
                ]

delkeyblock = ["magic",
                "size",
                #"txs"
                ]

def invStr(data: str):
    res = ""
    data = [data[i:i+2] for i in range(0, len(data), 2)]

    return "".join(data[::-1])


def selectVariant(file):

    if type(file) == str:
        data = int(file, 16)
        if data < 253:
            return data
        if data >= 253 and data <= 0xffff:
            return 4
        if data >= 0x10000 and data <= 0xffffffff:
            return 8
        if data >= 0x100000000 and data <= 0xffffffffffffffff:
            return 16
        
    else:    
        data = file.read(1).hex()
    
        lndata = int(data, 16)

        if lndata < 253:
            return data
        if lndata >= 253 and lndata <= 0xffff:
            return invStr(file.read(2).hex())
        if lndata >= 0x10000 and lndata <= 0xffffffff:
            return invStr(file.read(4).hex())
        if lndata >= 0x100000000 and lndata <= 0xffffffffffffffffff:
            return invStr(file.read(8).hex())

    return None

def str_to_bytes(data):
    data = [data[i:i + 2] for i in range(0,len(data),2)]
    return data

def readBytes(data, count):
    dataRet = "".join(data[:count])
    
    if dataRet == "":
        return None
    
    data = data[count:]

    return data, dataRet

def get_info_from_sig(sig: str):
    R,S,Pub = None, None, None
    try:
        sig = str_to_bytes(sig)
        
        sig, _ = readBytes(sig, 4)
        sig, lenR = readBytes(sig, 1)
        
        lenR = int(lenR, 16)
        sig, R = readBytes(sig, lenR)
        
        sig, _ = readBytes(sig, 1)

        sig, lenS = readBytes(sig, 1)
        
        lenS = int(lenS,16)
        sig, S = readBytes(sig, lenS)
        
        sig, _ = readBytes(sig, 1)
        
        sig, lenPub = readBytes(sig, 1)
        
        lenPub = int(lenPub, 16)
        sig, Pub = readBytes(sig, lenPub)
        
    except TypeError:
        pass
        
    return R, S, Pub
    
def parseBlock(filePath: str):
    with open(filePath, "rb") as file:

        blocks = []

        while file.tell() != os.path.getsize(filePath):
            magic = invStr(file.read(4).hex())
            size = invStr(file.read(4).hex())
            head = file.read(80).hex()

            txs = []

            txCount = selectVariant(file)

            for i in range(int(txCount, 16)):
                witness = False
                version = invStr(file.read(4).hex())
                inputCount = selectVariant(file)
                if int(inputCount,16) == 0:
                    witness = True
                    file.read(1)
                    inputCount = selectVariant(file)

                inputs = []
                outs = []
                for j in range(int(inputCount, 16)):
                    txid = invStr(file.read(32).hex())

                    vout = invStr(file.read(4).hex())

                    sigSize = selectVariant(file)
                    sig = file.read(int(sigSize, 16)).hex()
                    
                    if txid != "0000000000000000000000000000000000000000000000000000000000000000":
                        data = get_info_from_sig(sig)
                    else:
                        data = [None,None,None]
  
                    
                    sequence = invStr(file.read(4).hex())
                    inputs.append({"txid": txid,
                                   "vout": vout,
                                   "sigSize": sigSize,
                                   "sig": sig,
                                   "dataSig" : {"R": data[0],
                                                "S": data[1],
                                                "Pub" : data[2]},
                                   
                                   "sequence": sequence
                                   })

                outCount = selectVariant(file)

                for j in range(int(outCount, 16)):
                    value = invStr(file.read(8).hex())

                    sigSize = selectVariant(file)
                    scriptPub = file.read(int(sigSize, 16)).hex()

                    outs.append({"value": value,
                                 "sigSize": sigSize,
                                 "scriptPub": scriptPub})

                witnesses = []
                if witness:
                    tempW = []
                    for j in range(int(inputCount,16)):
                        witnessCount = selectVariant(file)
                        for m in range(int(witnessCount,16)):
                            lenghtItem = selectVariant(file)
                            item = file.read(int(lenghtItem,16)).hex()
                            tempW.append(item)

                    witnesses.append(tempW)

                locktime = invStr(file.read(4).hex())

                raw = invStr(version) + inputCount

                for inputData in inputs:
                    raw += invStr(inputData["txid"]) + invStr(inputData["vout"]) + \
                        inputData["sigSize"] + inputData["sig"] + \
                        invStr(inputData["sequence"])

                raw += outCount

                for outData in outs:
                    raw += invStr(outData["value"]) + \
                        outData["sigSize"] + outData["scriptPub"]

                if len(witnesses) != 0:
                    lenght = lambda x, y: "0" * (y - len(x) % y) + x if len(x) % y != 0 else x

                    for dataW in witnesses:
                        raw += lenght(hex(len(dataW))[2:],2)
                        for item in dataW:
                            raw += lenght(hex(len(item))[2:],2) + item

                raw += invStr(locktime)

                hash = invStr(hashlib.sha256(hashlib.sha256(bytes.fromhex(raw)).digest()).hexdigest())
                

                for i in range(len(inputs)):
                    data = inputs[i]
                    inputs[i] = {key:data[key] for key in data if key not in delkeyinputs}
                
                saveTxs =  {"version": version,
                            "hash": hash,
                            "inputCount": inputCount,
                            "inputs": inputs,
                            "outs": outs,
                            "lock time": locktime,
                            "witness" : witnesses,
                            "raw": raw
                            }      
                
                saveTxs = {i:saveTxs[i] for i in saveTxs.keys() if i not in delkeysave}
                txs.append(saveTxs)
                 
            saveBlocks = {"magic": magic,
                          "size": size,
                          "txs": txs
                          }
            
            saveBlocks = {i:saveBlocks[i] for i in saveBlocks.keys() if i not in delkeyblock}
                
            blocks.append(saveBlocks)

        return blocks