from utility import getAddressTrans_my,Transaction, getTokenTrans, getTokenTrans_my,request
import json

"""
那么需要整理出来的，
目前只需要看一个人的转出记录
1.算出一个点的size  symbolSize
        {
            "id": "0",
            "name": "Myriel",      #使用地址名字
            "symbolSize": 19.12381,  #通过统计交易的量（包含这个点的全部交易量），使用dict来记录   dict["点id"]=value  ,后面遍历
            "value": 28.685715,
            "label": {
                "normal": {
                    "show": true   #最好是在放在上面再显示？
                }
            },
            "category": 0 #这里不清楚要不要,应该不会要
        },
        nodes_data = [
            opts.GraphNode(name="结点1", symbol_size=10),]  后面需要改变的还有白名单等等，不过不用管
        category： 白名单分类。  在名单上的分类。
2.算出点之间的edge
links_data = [
    opts.GraphLink(source="结点1", target="结点2", value=2,linestyle_opts = opts.LineStyleOpts(width=10,curve=0.3)),]
    还需要一个dict来记录两个节点之间的交易量，分开来，也是source到target。记录两个点某个方向的总的交易量。
    取名可以用     dict["节点1"]={"source":"节点1","target":"节点2","value":float}  用的时候遍历取出来做links_data
"""
def getValuableTrans(total_trans):
    """
    Delete all the trans without core
    input: List of Transactions
    output: Refined list of Transactions
    """
    refined_trans = []
    for single in total_trans:
        if single["value"] > 0:
            refined_trans.append(single)
    return refined_trans
def getTokenName(token_address):
    #TODO:需要判断是否为token
    url = 'https://scan.coredao.org/api/chain/token_info'
    headers = {
        'content-type' : 'application/json;charset=UTF-8'
    }
    data={
        "tokenAddress": "0xea3740e2dfeedd2e2aa1e86277d6e97c4c746053"
    }
    res = request.post(url,headers=headers,data=json.dumps(data))
    res = json.loads(res.text)
    return res["data"]["tokenSymbol"]

class GraphDrawer():
    def __init__(self,address,token=None) -> None:
        self.address = address
        self.token = token
        if self.token == None:
            total_trans = getAddressTrans_my(address)
            total_trans = getValuableTrans(total_trans)
            self.token_name = "CORE"
        else:
            total_trans = getTokenTrans_my(token,address)
            total_trans = getValuableTrans(total_trans)
            self.token_name = getTokenName(token)
            #TODO：这里需要弄到token_name
        self.nodeslist = []
        self.total_trans = total_trans
        self.total_nodes_value = 0  
        self.total_edges_value = 0
        self.nodes = None
        self.edges = None
    def run(self):
        
            self.getNodesData()
            self.getEdgesData()


    def getNodesData(self):
        """
        nodes:[{
            {
                address: str
                is_user: bool #是否为合约地址
                value: float #交易量
            }
        }]
        """
        total_trans = self.total_trans
        nodes = []
        nodestmp = []

        for single in total_trans:
            #value must over 0.0
            #if its first time
            addressfrom = single["address_from"]["address"]
            if addressfrom not in nodestmp:
                nodestmp.append(addressfrom)
                tmp = {}
                tmp["address"] = addressfrom
                tmp["is_user"] = single["address_from"]["is_user"]
                tmp["value"] = single["value"]
                nodes.append(tmp) 
            else:
                nodes[nodestmp.index(addressfrom)]["value"] += single["value"]


            addressto = single["address_to"]["address"]
            if addressto not in nodestmp:
                nodestmp.append(addressto)
                tmp = {}
                tmp["address"] = addressto
                tmp["is_user"] = single["address_to"]["is_user"]
                tmp["value"] = single["value"]
                nodes.append(tmp) 
            else:
                nodes[nodestmp.index(addressto)]["value"] += single["value"]


            self.total_nodes_value += single["value"]*2
        self.nodes = nodes
        self.nodeslist = nodestmp
        



    def getEdgesData(self):
        """
        [{
            from:
            to:
            data:[{
                value:
                time:
            }]
            total_value:
        }]
        """
        total_trans = self.total_trans
        edges=[]
        edgestmp = []
        for single in total_trans:
            addressfrom = single["address_from"]["address"]
            addressto = single["address_to"]["address"]
            if (addressfrom,addressto) not in edgestmp:
                edgestmp.append((addressfrom,addressto))
                tmp = {}
                tmp["from"] = addressfrom
                tmp["to"] = addressto
                tmp["data"] =[{
                    "value": single["value"],
                    "time": single["time"]
                }]
                tmp["total_value"] = single["value"]
                edges.append(tmp)
            else:
                index = edgestmp.index((addressfrom,addressto))
                edges[index]["total_value"] += single["value"]
                edges[index]["data"].append(
                    {
                        "value": single["value"],
                        "time": single["time"]
                    }
                )
            self.total_edges_value += single["value"]
        self.edges = edges
#对所有不为零的交易进行处理

    
if __name__ == "__main__":
    # a = getNodesData("0x9f4cb8c51265B4416d0b84369D90a87Ae1b7720e")
    # print(a)
    a = GraphDrawer("0x9f4cb8c51265B4416d0b84369D90a87Ae1b7720e")
    a.getEdgesData()
    # a.getNodesData()
    print(a.edges)