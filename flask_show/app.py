from flask import Flask,render_template,request
from time import sleep,ctime
import math
import libscrc
import json

import subprocess
#import sys
#sys.path.append(r'~/P4/behavioral-model/tools')
#from runtime_CLI import *

names=[u'sketch0',u'sketch1',u'sketch2',
       u'sketch_vote0',u'sketch_vote1',u'sketch_vote2',
       u'sketch_1key0',u'sketch_1key1',u'sketch_1key2',
       u'sketch_2key0',u'sketch_2key1',u'sketch_2key2',]

dict_reg={}
len_reg=256

#def runtime_CLI_read():
#     register_name=u'MyIngress.sketch0'
#     args = get_parser().parse_args()
#
#     standard_client, mc_client = thrift_connect(
#         args.thrift_ip, args.thrift_port,
#         RuntimeAPI.get_thrift_services(args.pre)
#     )
#
#     load_json_config(standard_client, args.json)
#
#     for name in names:
#         dict_reg[name] = standard_client.bm_register_read_all(0, u'MyIngress.'+name)
#
#     return sorted(dict_reg.items(), key=lambda d: d[0])

def runtime_CLI_read():
    data=open("./data/now_data",'r').read()
    data.strip('\n')
    dict_reg=json.loads(data)
    return dict_reg

def key2raw(key1,key2):
    myints=[]
    for i in range(7):
        myints.append(bytes([key1 % 256]))
        key1=key1>>8
    for i in range(6):
        myints.append(bytes([key2 % 256]))
        key2 = key2 >>8
    myints.reverse()
    raw=b""
    raw+=b"".join(myints[9:])
    raw+=b"".join(myints[2:6])
    raw+=b"".join(myints[7:9])
    raw+=b"".join(myints[:2])
    raw+=myints[6]
    return raw



def key2info(key1,key2):
    prot=math.floor(float(int(key1)/pow(2,48)))
    sport=math.floor(float(int(key1-prot*pow(2,48))/pow(2,32)))
    sip=int2ip(key1%pow(2,32))
    dport = math.floor(float(int(key2) / pow(2, 32)))
    dip = int2ip(key2 % pow(2, 32))
    if prot==6:
        prot="TCP"
        return [prot,sip,dip,sport,dport]
    elif prot ==17:
        prot= "UDP"
        return [prot, sip, dip, sport, dport]
    else:
        return None

def raw2info(raw):
    myints = []
    for i in range(13):
        myints.append(raw[i])
    sip = ".".join(map(str, myints[0:4]))
    sport = myints[8] * 256 + myints[9]
    dip = ".".join(map(str, myints[4:8]))
    dport = myints[10] * 256 + myints[11]
    prot = myints[12]
    if prot==6:
        prot="TCP"
        return [prot, sip, dip, sport, dport]
    elif prot==17:
        prot="UDP"
        return [prot, sip, dip, sport, dport]
    else:
        return None

def int2ip(ip_int):
    s = []
    for i in range(4):
        ip_part = str(ip_int % 256)
        s.append(ip_part)
        ip_int = math.floor(ip_int / 256)
    return '.'.join(s[::-1])
#
def flow_search(regs):
    raws=[]
    raw_count={}
    for i in range(len_reg):
        raw0=key2raw(regs['sketch_1key0'][i], regs['sketch_2key0'][i])
        if raw0 not in raws:
            raws.append(raw0)
        raw1 = key2raw(regs['sketch_1key1'][i], regs['sketch_2key1'][i])
        if raw1 not in raws:
            raws.append(raw1)
        raw2 = key2raw(regs['sketch_1key2'][i], regs['sketch_2key2'][i])
        if raw2 not in raws:
            raws.append(raw2)
    for raw in raws:
        count0=regs['sketch0'][libscrc.crc32(raw)%len_reg]
        count1 = regs['sketch1'][libscrc.ibm(raw) % len_reg]
        count2=regs['sketch2'][int(raw[7])]
        count = min(count0,count1,count2)
        if count !=0:
            raw_count[raw]=[]
            raw_count[raw].append(count)
    return sorted(raw_count.items(),key=lambda item:item[1],reverse=True)

#
# def getinfoo2show():

        

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def myshow():
    subprocess.call("python ./runtime_Register.py",shell=True)
    info=runtime_CLI_read()
    print(len(info))
    paixu=flow_search(info)
    result=[]
    len_m=min(20,len(paixu))
    for x in range(len_m):
        y=raw2info(paixu[x][0])
        if y:
            y.append(paixu[x][1])
        else:
            continue
        result.append(y)
    count=0

    return render_template("index.html",time=ctime(),info=result,count=count)


if __name__ == '__main__':
    app.run()
