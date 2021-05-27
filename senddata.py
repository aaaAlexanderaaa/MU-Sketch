from scapy.all import *
import threading
import os
import struct
import fcntl
import time
import pickle
import json
from time import sleep


def getInterfaceName():
    #assume it has veth2

    return [x for x in os.listdir('/sys/cla'
                                  'ss/net') if "veth2" in x][0]
def eth_header(src, dst, proto=0x0800):
    src_bytes = "".join([x.decode('hex') for x in src.split(":")])
    dst_bytes = "".join([x.decode('hex') for x in dst.split(":")])
    return src_bytes + dst_bytes + struct.pack("!H", proto)

mytcps=0
myudps=0
data = {}
count=0
pausecount=20000
send_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW)
intf_name = getInterfaceName()
send_socket.bind((intf_name, 0))
eth_h = eth_header("01:02:20:aa:33:aa", "02:02:20:aa:33:aa", 0x800)
ske2=[]

#this func use scapy to create packet
def do_pkt(pktraw):
    myints = []
    for i in range(13):
        myints.append(int("0x" + pktraw[2 * i:2 * i + 2], 16))
    sip = ".".join(map(str,myints[0:4]))
    sport = myints[4] *256+ myints[5]
    dip = ".".join(map(str,myints[6:10]))
    dport = myints[10] *256+ myints[11]
    prot= myints[12]
    if prot==6:
        pkt=Ether(src='11:22:33:44:55:77', dst='11:22:33:44:55:66')/IP(src=sip, dst=dip)/TCP(sport=sport, dport=dport)
        global mytcps
        mytcps += 1
        return pkt
    elif prot==17:
        pkt = Ether(src='11:22:33:44:55:77', dst='11:22:33:44:55:66')/IP(src=sip, dst=dip)/UDP(sport=sport, dport=dport)
        global myudps
        myudps+=1
        return pkt
    else:
        return None

#this func use socket to create packet; using socket to send packet is faster than scapy
def do_pkt2(pktraw):
    myints = []
    for i in range(13):
        myints.append(int("0x" + pktraw[2 * i:2 * i + 2], 16))
    sip = ".".join(map(str,myints[0:4]))
    sport = myints[4] *256+ myints[5]
    dip = ".".join(map(str,myints[6:10]))
    dport = myints[10] *256+ myints[11]
    prot= myints[12]
    if prot==6:
        mx=int(pktraw[:16],16)%1024
        #global ske2
        #print sip+','+dip+','+str(sport)+','+str(dport)+','+str(mx)+','+str(len(ske2))
        #print pktraw
        #if mx not in ske2:
        #    ske2.append(mx)
        return create_packet_ip_tcp(eth_h, sip, dip, sport, dport)
    else:
        return None

def runtime_CLI_read():
    data=open("./temp_data",'r').read()
    data.strip('\n')
    dict_reg=json.loads(data)
    return dict_reg

def send_n(s, packet):
    s.send(packet)
    time.sleep(0.005)

def ip_header(src,dst,ttl,proto,id=0):

    # now start constructing the packet
    packet = ''
    # ip header fields
    ihl = 5
    version = 4
    tos = 128
    tot_len = 20 + 20   # python seems to correctly fill the total length, dont know how ??
    frag_off = 0
    if proto == "tcp":
        proto = socket.IPPROTO_TCP
    elif proto == "udp":
        proto = socket.IPPROTO_UDP
    else:
        print "proto unknown"
        return
    check = 10  # python seems to correctly fill the checksum
    saddr = socket.inet_aton ( src )  #Spoof the source ip address if you want to
    daddr = socket.inet_aton ( dst )

    ihl_version = (version << 4) + ihl

    # the ! in the pack format string means network order
    ip_header = struct.pack('!BBHHHBBH4s4s' , ihl_version, tos, tot_len, id, frag_off, ttl, proto, check, saddr, daddr)
    return ip_header

def tcp_header(src,dst,sport,dport):

    # tcp header fields
    source = sport #sourceport
    dest = dport  # destination port
    seq = 0
    ack_seq = 0
    doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
    #tcp flags
    fin = 0
    syn = 1
    rst = 0
    psh = 0
    ack = 0
    urg = 0
    window = socket.htons (5840)    #   maximum allowed window size
    check = 0
    urg_ptr = 0

    offset_res = (doff << 4) + 0
    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh <<3) + (ack << 4) + (urg << 5)

    # the ! in the pack format string means network order
    tcp_header = struct.pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, check, urg_ptr)

    # pseudo header fields
    source_address = socket.inet_aton( src )
    dest_address = socket.inet_aton(dst)
    placeholder = 0
    proto = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)

    psh = struct.pack('!4s4sBBH' , source_address , dest_address , placeholder , proto , tcp_length)
    psh = psh + tcp_header

    tcp_checksum = checksum(psh)

    # make the tcp header again and fill the correct checksum
    tcp_header = struct.pack('!HHLLBBHHH' , source, dest, seq, ack_seq, offset_res, tcp_flags,  window, tcp_checksum , urg_ptr)

    # final full packet - syn packets dont have any data
    return tcp_header

def create_packet_ip_tcp(eth_h, src_ip, dst_ip, sport, dport):
    return eth_h + ip_header(src_ip, dst_ip, 64, "tcp",1) + tcp_header(src_ip, dst_ip, sport, dport)



#datafile's num
#for filexu in range(11):
for filexu in range(1):
    file=open('./datas/'+str(filexu)+'.dat', 'rb')
    file.seek(0,0)
    while True: 
        a = file.read(13)
        #every pkt is 13 bytes ,4 byte SrcIP+ 2 byte SrcPort + 4 byte DstIP + 2 byte DstPort + 1 byte Protocal 
        if not a:
            break
        else:
            pktraw=''.join(['{:02X}'.format(ord(i)) for i in a])
            pkt2send = do_pkt2(pktraw)
            if pkt2send:
                #sendp(pkt2send, iface="veth2")
                send_n(send_socket, pkt2send)
                
                #count my flows
                if pktraw not in data.keys():
                    data[pktraw]=1
                else:
                    data[pktraw]+=1
                count += 1
        
        #every pausecount pkts, download bmv2 registers and save flow count info 
        if (count % pausecount)==0:
            sleep(2)
            #sleep just let bmv2 have enough time to deal with pkts in queue
            #subprocess use runtime_Register.py to download bmv2 registers
            subprocess.call("python ./runtime_Register.py", shell=True)
            info = runtime_CLI_read()
            result={}
            result['data']=data
            result['register']=info
            #save all collected info
            open('./result/dat'+str(filexu)+'__' + str(math.floor(count / pausecount)) + '.result','w').write(json.dumps(result,ensure_ascii=False))

sleep(2)
subprocess.call("python ./runtime_Register.py", shell=True)
info = runtime_CLI_read()
result={}
result['data']=data
result['register']=info
open('./result/dat0_result.result','w').write(json.dumps(result,ensure_ascii=False))
