#python3
import libscrc


#传入16进制字符串
def my_csum16(flowid):
    mybytes=[]
    for i in bytes.fromhex('{:026X}'.format(int(flowid,16))):
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

#传入16进制字符串
def my_crc16(flowid):
    return libscrc.ibm(bytes.fromhex(flowid))

#传入16进制字符串
def my_crc32(flowid):
    return libscrc.crc32(bytes.fromhex(flowid))

#传入16进制字符串
def my_identity(flowid):
    return int(flowid[:16],16)


if __name__=='__main__':
    test='3927BECFBA212BE09EF8C8D506'
    sketch_len=1024
    print(my_identity(test)%sketch_len)#992
    print(my_crc16(test)%sketch_len)#701
    print(my_crc32(test)%sketch_len)#282
    print(my_csum16(test)%sketch_len)#56
