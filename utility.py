from tkinter.tix import Tree
import requests
from requests.adapters import HTTPAdapter
request = requests.Session()
request.mount('http://', HTTPAdapter(max_retries=3))
request.mount('https://', HTTPAdapter(max_retries=3))
import json
import time
from datetime import datetime, timedelta
class AddressData:
    def __init__(self,address,is_user):
        self.address = address
        self.is_user = is_user
    def __str__(self) -> str:
        return str({
            "address":self.address,
            "is_user":self.is_user
        })
    __repr__=__str__
    def __getitem__(self,attribute):
        return self.__dict__[attribute]
class Transaction:
    def __init__(self,hash:str,address_from:AddressData,address_to:AddressData,time,value):
        self.hash = hash
        self.address_from = address_from
        self.address_to = address_to
        self.time = time
        self.value = value
    def __str__(self) -> str:
        return str({
            "hash":self.hash,
            "address_from":self.address_from,
            "address_to":self.address_to,
            "time":self.time,
            "value":self.value
        })
    __repr__=__str__
    def __getitem__(self,attribute):
        return self.__dict__[attribute]

# 在字符串指定位置插入字符
# str_origin：源字符串  pos：插入位置  str_add：待插入的字符串
#
def str_insert(str_origin, pos, str_add):
    str_list = list(str_origin)    # 字符串转list
    str_list.insert(pos, str_add)  # 在指定位置插入字符串
    str_out = ''.join(str_list)    # 空字符连接
    return  str_out


def getAddressDetail(address):
    url = 'https://scan.coredao.org/api/chain/address_detail'
    headers = {
        'content-type' : 'application/json;charset=UTF-8'
    }
    data = {
        "addressHash" : address
    }
    res = request.post(url,headers=headers,data=json.dumps(data))
    return json.loads(res.text)

def getAddressTrans(address:str) -> list:
    """
    Returns all the transaction data as a list
    """
    url = 'https://scan.coredao.org/api/chain/search_transaction'
    headers = {
        'content-type' : 'application/json;charset=UTF-8'
    }
    data={
        "a": address,
        "pageNum": 1,
        "pageSize": 25
    }
    res = request.post(url,headers=headers,data=json.dumps(data))
    res = json.loads(res.text)
    total = res['data']['total']
    pages = total // 100 + 1
    data["pageSize"] = 100
    total_trans = []
    for i in range(1,pages+1):
        data["pageNum"] = i
        res = request.post(url,headers=headers,data=json.dumps(data))
        res = json.loads(res.text)
        total_trans.extend(res["data"]["records"])
    return total_trans

def getAddressTokenTrans(address,tokenaddress):
    """
    先判断是不是token，然后再进行处理
    """
    pass

def getAddressTrans_my(address:str) -> list:
    def check_is_user(datablock):
        if datablock['type'] == "2":
            return True
        else :
            return False

    raw_trans = getAddressTrans(address)
    total_trans = []
    for single in raw_trans:
        hash = single['hash']
        from_address_address = single["fromHashAddress"]["hash"]
        from_address_is_user = check_is_user(single["fromHashAddress"])
        fromAddress = AddressData(from_address_address,from_address_is_user)
        to_address_address = single["toHashAddress"]["hash"]
        to_address_is_user = check_is_user(single["toHashAddress"])
        toAddress = AddressData(to_address_address,to_address_is_user)
        
        trans_time = single["timestamp"][:-9]
        utc = datetime.strptime(trans_time,"%Y-%m-%dT%H:%M:%S")
        bjt = utc + timedelta(hours=8)
        trans_time = bjt.strftime("%Y-%m-%d %H:%M:%S")

        demical = 18
        value = single["value"]
        if len(value) < demical:
            value = "".join(["0" for _ in range(demical-len(value))]) + value
        value = round(float(str_insert(value,-demical,".")),2)
        
        total_trans.append(Transaction(
            hash = hash,
            address_from = fromAddress,
            address_to = toAddress,
            time = trans_time,
            value = value
        ))
    return total_trans


def getTokenTrans(token,address):
    """
    得到token的交易记录
    只能找到erc20的
    """
    url = 'https://scan.coredao.org/api/chain/token_transfer'
    headers = {
        'content-type' : 'application/json;charset=UTF-8'
    }
    data={
        "addressHash": token,
        "eip": 20,
        "pageNum": 1,
        "pageSize": 25,
        "searchParam": address,
        "tokenPage": True
    }
    res = request.post(url,headers=headers,data=json.dumps(data))
    res = json.loads(res.text)
    total = res['data']['total']
    pages = total // 100 + 1
    data["pageSize"] = 100
    total_trans = []
    for i in range(1,pages+1):
        data["pageNum"] = i
        res = request.post(url,headers=headers,data=json.dumps(data))
        res = json.loads(res.text)
        total_trans.extend(res["data"]["records"])
    return total_trans

def getTokenTrans_my(token,address):
    def check_is_user(datablock):
        if datablock['type'] == "2":
            return True
        else :
            return False

    raw_trans = getTokenTrans(token,address)
    total_trans = []
    for single in raw_trans:
        hash = single['txnHash']
        from_address_address = single["fromHashAddress"]["hash"]
        from_address_is_user = check_is_user(single["fromHashAddress"])
        fromAddress = AddressData(from_address_address,from_address_is_user)
        to_address_address = single["toHashAddress"]["hash"]
        to_address_is_user = check_is_user(single["toHashAddress"])
        toAddress = AddressData(to_address_address,to_address_is_user)
        
        trans_time = single["createTime"][:-9]
        utc = datetime.strptime(trans_time,"%Y-%m-%dT%H:%M:%S")
        bjt = utc + timedelta(hours=8)
        trans_time = bjt.strftime("%Y-%m-%d %H:%M:%S")

        demical = 18
        value = single["value"]
        if len(value) < demical:
            value = "".join(["0" for _ in range(demical-len(value))]) + value
        value = round(float(str_insert(value,-demical,".")),2)
        
        total_trans.append(Transaction(
            hash = hash,
            address_from = fromAddress,
            address_to = toAddress,
            time = trans_time,
            value = value
        ))
    return total_trans

if __name__=="__main__":
    # a = getAddressDetail("0xBb5e1777A331ED93E07cF043363e48d320eb96c4")
    # print(a)
    a = getTokenTrans_my("0xea3740e2dfeedd2e2aa1e86277d6e97c4c746053","0xD1C530Dfb6D4b64e56c75203E2aD87C93F38Fb59")
    print(a)