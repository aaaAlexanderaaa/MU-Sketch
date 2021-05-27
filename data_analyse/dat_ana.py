#1.相对误差图：相对误差随包的总体数量增加的变化
#2.绝对误差图：绝对误差随总体数量变化的图
#3.准确率：准确率随包的总体数量的变化的图


import json
import math
import operator


import libscrc

names=[u'sketch0',u'sketch1',u'sketch2',
       u'sketch_vote0',u'sketch_vote1',u'sketch_vote2',
       u'sketch_1key0',u'sketch_1key1',u'sketch_1key2',
       u'sketch_2key0',u'sketch_2key1',u'sketch_2key2',]

def cksum16(sketchkey):
    mybytes=[]
    for i in bytes.fromhex('{:026X}'.format(int(sketchkey,16))):
        mybytes.append(i)
    sum=0
    a1=mybytes[:8]
    a1.reverse()
    a2=mybytes[8:12]
    a2.reverse()
    a3=mybytes[12]
    temp=0
    for a in a1:
        temp=temp<<8
        temp+=a
    sum+=temp
    temp = 0
    for a in a2:
        temp=temp<<8
        temp+=a
    sum+=temp
    sum+=a3
    if sum >=pow(2,64):
        sum=sum%pow(2,64)+1
    t1=sum>>32
    t2=sum%pow(2,32)+t1
    if t2 >=pow(2,32):
        t2=t2%pow(2,32)+1
    t3=t2>>16
    t4=t3+t2%pow(2,16)
    if t4>=pow(2,16):
        t4=t4%pow(2,16)+1
    t5=~t4%pow(2,16)
    t6=t5>>8
    t7=(t5%pow(2,8))*pow(2,8)+t6
    return t7

def get_correct_top(num,s_b_get,s_b_real):
    not_corr=0
    b_gets=[]
    b_real=[]
    for i in range(num):
        b_gets.append(s_b_get[i][0])
        b_real.append(s_b_real[i][0])
    for i in range(num):
        if b_real[i] not in b_gets:
            not_corr+=1
    return num-not_corr


def myget_value(registers,sketchkey,len_reg):
    #in my mu-Sketch ,first row's hash func is crc32,than is crc16.ibm,last is checksum
    #we realize ckcum16 by reading bmv2 hash source code
    #others using libscrc which we verify that the results of libscrc and bmv2 are equal
    v0 = registers['sketch0'][libscrc.crc32(bytes.fromhex(sketchkey))%len_reg]
    v1 = registers['sketch1'][libscrc.ibm(bytes.fromhex(sketchkey)) % len_reg]
    v2 = registers['sketch2'][cksum16(sketchkey) % len_reg]
    # return math.floor(min(v0,v1,v2)/2)
    return min(v0, v1, v2)

def getwucha(s_b_get,n):
    pjxdwc_bytop = 0
    pjjdwc_bytop = 0
    for i in range(n):
        pjjdwc_bytop += abs(s_b_get[i][1]['wucha'])
        pjxdwc_bytop += abs(s_b_get[i][1]['wucha']) / abs(s_b_get[i][1]['realsum'])
    pjxdwc_bytop /= n
    pjjdwc_bytop /= n
    return pjxdwc_bytop,pjjdwc_bytop


if __name__=="__main__":
    my_result={}
    top100=100
    filenum=111
    # sketch_len=1024
    sketch_len = 4096
    # sketch_len = 16384
    for fnum in range(filenum):
        # if fnum>=40:
        #     print(1)
        # dati = json.loads(open("./16384/result_mv/dat0__" + str(fnum + 1) + ".0.result", 'r',  errors='ignore').read())
        dati = json.loads(open("./4096/result_mu/dat0__" + str(fnum + 1) + ".0.result", 'r').read())
        # dati = json.loads(open("./16384/result_mu/dat0__" + str(fnum + 1) + ".0.result", 'r').read())
        # dati=json.loads(open("./result_cuPlus/dat0__" + str(fnum+1) + ".0.result", 'r').read())
        # dati=json.loads(open("./result_mv/dat0__" + str(fnum+1) + ".0.result", 'r').read())
        registers=dati['register']
        datas=dati['data']
        nowkeys={}
        mytop100s={}

        for i in range(3):
            for j in range(sketch_len):
                thiskey='{:012X}'.format(registers[names[i+6]][j])+'{:014X}'.format(registers[names[i+9]][j])
                if thiskey not in nowkeys:
                    if thiskey in datas.keys():
                        nowkeys[thiskey]={}
                        nowkeys[thiskey]['getsum']=  myget_value(registers, thiskey, sketch_len)
                        nowkeys[thiskey]['realsum'] = datas[thiskey]
                        nowkeys[thiskey]['wucha']=nowkeys[thiskey]['getsum']-nowkeys[thiskey]['realsum']

        s_b_get = sorted(nowkeys.items(),key = lambda i: i[1]['getsum'], reverse=True)
        s_b_real =sorted(nowkeys.items(),key = lambda i: i[1]['realsum'], reverse=True)
        # s_b_get_k2=[]
        # for x in s_b_get:
        #     if x[1]['getsum']>=40*(fnum+1)
        pjxdwc_byall = 0
        pjjdwc_byall = 0
        for allkey in datas.keys():
            realnum= datas[allkey]
            datas[allkey]={}
            datas[allkey]['realnum']=realnum
            datas[allkey]['getsum'] = myget_value(registers, allkey, sketch_len)
            datas[allkey]['wucha']=datas[allkey]['getsum']-datas[allkey]['realnum']
            pjxdwc_byall+=abs(datas[allkey]['wucha'])/datas[allkey]['realnum']
            pjjdwc_byall+=abs(datas[allkey]['wucha'])
        pjxdwc_byall/=len(datas.keys())
        pjjdwc_byall/=len(datas.keys())



        my_result[fnum]={}
        # my_result[fnum]['data']=datas
        my_result[fnum]['s_b_get']=s_b_get
        # my_result[fnum]['s_b_real']=s_b_real

        my_result[fnum]['correct_top1000']=get_correct_top(1000,s_b_get,s_b_real)/1000
        my_result[fnum]['correct_top500']=get_correct_top(500,s_b_get,s_b_real)/500
        my_result[fnum]['correct_top200']=get_correct_top(200,s_b_get,s_b_real)/200
        my_result[fnum]['correct_top100']=get_correct_top(100,s_b_get,s_b_real)/100
        my_result[fnum]['correct_top50'] = get_correct_top(50, s_b_get, s_b_real)/50
        my_result[fnum]['correct_top20'] = get_correct_top(20, s_b_get, s_b_real)/20
        my_result[fnum]['correct_top10'] = get_correct_top(10, s_b_get, s_b_real)/10
        my_result[fnum]['correct_top5'] = get_correct_top(5, s_b_get, s_b_real)/5
        my_result[fnum]['pjxdwc_byall']=pjxdwc_byall
        my_result[fnum]['pjjdwc_byall'] = pjjdwc_byall
        my_result[fnum]['pjxdwc_bytop100'],my_result[fnum]['pjjdwc_bytop100'] = getwucha(s_b_get,100)
        my_result[fnum]['pjxdwc_bytop500'], my_result[fnum]['pjjdwc_bytop500'] = getwucha(s_b_get, 500)
        my_result[fnum]['pjxdwc_bytop1000'], my_result[fnum]['pjjdwc_bytop1000'] = getwucha(s_b_get, 1000)
    # open('./result_16384_mu','w').write(json.dumps(my_result))
    open('./result_4096_mu', 'w').write(json.dumps(my_result))
    # open('./result_16384_mv', 'w').write(json.dumps(my_result))
    # open('./result_mymv', 'w').write(json.dumps(my_result))
