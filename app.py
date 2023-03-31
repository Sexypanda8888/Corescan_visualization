from asyncio.windows_events import NULL
from random import randrange

from flask import Flask, render_template,request
import json
from pyecharts import options as opts
from pyecharts.charts import Graph
from pyecharts.commons.utils import JsCode
from core import GraphDrawer

app = Flask(__name__, static_folder="templates")


# def bar_base() -> Bar:
#     c = (
#         Bar()
#         .add_xaxis(["衬衫", "羊毛衫", "雪纺衫", "裤子", "高跟鞋", "袜子"])
#         .add_yaxis("商家A", [randrange(0, 100) for _ in range(6)])
#         .add_yaxis("商家B", [randrange(0, 100) for _ in range(6)])
#         .set_global_opts(title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"))
#     )
#     return c

def graph_base(address,token=None):
    a = GraphDrawer(address,token)
    a.run()
    nodes_data = [  {
                        "name":i["address"],
                        "fixed":False,
                        "symbolSize":i["value"]*25/a.total_nodes_value,
                        "value":round(i["value"],2),
                        "label":{
                            "show": True,
                            "margin": 8,
                            "formatter": i["address"][-4:]
                        },
                    }
                        for i in a.nodes]
    links_data = [  {
                        "source":i["from"], 
                        "target":i["to"],
                        "symbol":["none","arrow",
                            i["data"]
                        ],
                        "symbolSize": max(i["total_value"]*40/a.total_edges_value,10),
                        "lineStyle":{
                            "show": True,
                            "width": i["total_value"]*30/a.total_edges_value,
                            "opacity": 1,
                            "curveness": 0.3,
                            "type": "solid"
                        }     
                    }
                        for i in a.edges]
    list_html ="""
    	<table class="table">
		<thead>
			<tr>
				<th>Address</th>
			</tr>
		</thead>
		<tbody>
        {}
		</tbody>
	</table>
    """.format(''.join(['<tr> <td>{}</td>'.format(i) for i in a.nodeslist]))
    
    data ={
        "links_data":links_data,
        "nodes_data":nodes_data,
        "nodes_list":list_html,
        "token_name":a.token_name
    }
    return data

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/token")
def index_token():
    return render_template("index-token.html")

@app.route("/graph",methods=['POST'])
def get_graph_data():
    address = request.form.get("address")
    token_address =request.form.get("token_address")
    # print(address)
    data = graph_base(address,token_address)
    return json.dumps(data)


if __name__ == "__main__":
    app.run()