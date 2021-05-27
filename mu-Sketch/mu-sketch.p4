#include <core.p4>
#include <v1model.p4>


const bit<16> TYPE_IPV4 = 0x800;
/* 
const bit<8> IP_PROTOCOLS_TCP = 6;
const bit<8> IP_PROTOCOLS_UDP = 17;
*/

#define SKETCH_BUCKET_LENGTH 16384
#define SKETCH_CELL_BIT_WIDTH 64
#define SKETCH_KEY_BIT_WIDTH 64
#define SKETCH_VOTE_BIT_WIDTH 64

//只考虑tcp
#define SKETCH_REGISTER(num) register<bit<SKETCH_CELL_BIT_WIDTH>>(SKETCH_BUCKET_LENGTH) sketch##num
#define SKETCH_KRY_REG(num) register<bit<SKETCH_KEY_BIT_WIDTH>>(SKETCH_BUCKET_LENGTH) sketch_1key##num;\
 register<bit<SKETCH_KEY_BIT_WIDTH>>(SKETCH_BUCKET_LENGTH) sketch_2key##num
#define SKETCH_VOTE_REG(num) register<bit<SKETCH_VOTE_BIT_WIDTH>>(SKETCH_BUCKET_LENGTH) sketch_vote##num



#define SKETCH_COUNT(num, algorithm) hash(meta.index_sketch##num, HashAlgorithm.algorithm, (bit<16>)0, {hdr.ipv4.srcAddr, \
 hdr.tcp.srcPort,hdr.ipv4.dstAddr,  hdr.tcp.dstPort, hdr.ipv4.protocol}, (bit<32>)SKETCH_BUCKET_LENGTH);\
 sketch##num.read(meta.value_sketch##num, meta.index_sketch##num); \
 sketch_1key##num.read(meta.key1_sketch##num, meta.index_sketch##num); \
 sketch_2key##num.read(meta.key2_sketch##num, meta.index_sketch##num); \
 sketch_vote##num.read(meta.vote_sketch##num, meta.index_sketch##num); \
 meta.key1_now_sketch##num[47:16] = hdr.ipv4.srcAddr; \
 meta.key1_now_sketch##num[15:0] = hdr.tcp.srcPort; \
 meta.key2_now_sketch##num[55:24] = hdr.ipv4.dstAddr; \
 meta.key2_now_sketch##num[23:8] = hdr.tcp.dstPort; \
 meta.key2_now_sketch##num[7:0] = hdr.ipv4.protocol; 

/*
#define SKETCH_VOTE_CM(num)  do{\
  if(meta.vote_sketch##num ==0){\
  sketch_1key##num.write(meta.index_sketch##num, meta.key1_now_sketch##num); \
  sketch_2key##num.write(meta.index_sketch##num, meta.key2_now_sketch##num); \
  meta.vote_sketch##num=meta.vote_sketch##num+1; \
  sketch_vote##num.write(meta.index_sketch##num, meta.vote_sketch##num); \
  }else{ \
   if(meta.key1_sketch##num == meta.key1_now_sketch##num  && meta.key2_sketch##num == meta.key2_now_sketch##num){ \
   meta.vote_sketch##num=meta.vote_sketch##num+1; \
   sketch_vote##num.write(meta.index_sketch##num, meta.vote_sketch##num); \
   }else{meta.vote_sketch##num=meta.vote_sketch##num-1; \
   sketch_vote##num.write(meta.index_sketch##num, meta.vote_sketch##num); } \
  }}while(0);
*/

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;


header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<6>    dscp;
    bit<2>    ecn;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header tcp_t{
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<1>  cwr;
    bit<1>  ece;
    bit<1>  urg;
    bit<1>  ack;
    bit<1>  psh;
    bit<1>  rst;
    bit<1>  syn;
    bit<1>  fin;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

struct metadata {
    bit<32> index_sketch0;
    bit<32> index_sketch1;
    bit<32> index_sketch2;
    //bit<32> index_sketch3;
    //bit<32> index_sketch4;

    bit<64> value_sketch0;
    bit<64> value_sketch1;
    bit<64> value_sketch2;
    //bit<64> value_sketch3;
    //bit<64> value_sketch4;

    bit<64> value_sketch_min;

    bit<64> key1_sketch0;
    bit<64> key1_sketch1;
    bit<64> key1_sketch2;
    bit<64> key2_sketch0;
    bit<64> key2_sketch1;
    bit<64> key2_sketch2;

    bit<64> key1_now_sketch0;
    bit<64> key1_now_sketch1;
    bit<64> key1_now_sketch2;
    bit<64> key2_now_sketch0;
    bit<64> key2_now_sketch1;
    bit<64> key2_now_sketch2;
    
    bit<64> vote_sketch0;
    bit<64> vote_sketch1;
    bit<64> vote_sketch2;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    tcp_t        tcp;
}

/*************************************************************************
*********************** P A R S E R  *******************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {

        transition parse_ethernet;

    }

    state parse_ethernet {

        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType){
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            6 : parse_tcp;
            default: accept;
        }
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {

        //parsed headers have to be added again into the packet.
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);

        //Only emited if valid
        packet.emit(hdr.tcp);
    }
}



/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    SKETCH_REGISTER(0);
    SKETCH_REGISTER(1);
    SKETCH_REGISTER(2);
    //SKETCH_REGISTER(3);
    //SKETCH_REGISTER(4);

    SKETCH_KRY_REG(0);
    SKETCH_KRY_REG(1);
    SKETCH_KRY_REG(2);
        
    SKETCH_VOTE_REG(0);
    SKETCH_VOTE_REG(1);
    SKETCH_VOTE_REG(2);

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action sketch_count(){
        SKETCH_COUNT(0, crc32_custom);
        SKETCH_COUNT(1, crc16_custom);
        SKETCH_COUNT(2, csum16);
        //SKETCH_COUNT(3, crc32_custom);
        //SKETCH_COUNT(4, crc32_custom);
    }
    

   action set_egress_port(bit<9> egress_port){
        standard_metadata.egress_spec = egress_port;
    }

    table forwarding {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            set_egress_port;
            drop;
            NoAction;
        }
        size = 64;
        default_action = drop;
    }

    apply {
        //apply sketch
        if (hdr.ipv4.isValid() && hdr.tcp.isValid()){
            sketch_count();
            
            //get_min_value
            meta.value_sketch_min=meta.value_sketch0;
            if (meta.value_sketch1<=meta.value_sketch_min){
                meta.value_sketch_min=meta.value_sketch1;
            }
            if (meta.value_sketch2<=meta.value_sketch_min){
                meta.value_sketch_min=meta.value_sketch2;
            }
            
            
            //SKETCH_VOTE_CM(0);
            if(meta.value_sketch0 == meta.value_sketch_min){
                meta.value_sketch0 = meta.value_sketch0 +1; 
                sketch0.write(meta.index_sketch0, meta.value_sketch0); 
                if(meta.vote_sketch0 ==0){
                    sketch_1key0.write(meta.index_sketch0, meta.key1_now_sketch0); 
                    sketch_2key0.write(meta.index_sketch0, meta.key2_now_sketch0); 
                    meta.vote_sketch0=meta.vote_sketch0+1; 
                    sketch_vote0.write(meta.index_sketch0, meta.vote_sketch0); 
                }else{ 
                    if(meta.key1_sketch0 == meta.key1_now_sketch0 && meta.key2_sketch0 == meta.key2_now_sketch0){ 
                        meta.vote_sketch0=meta.vote_sketch0+1; 
                        sketch_vote0.write(meta.index_sketch0, meta.vote_sketch0); 
                    }else{meta.vote_sketch0=meta.vote_sketch0-1; 
                        sketch_vote0.write(meta.index_sketch0, meta.vote_sketch0); } 
                }
            }
            //SKETCH_VOTE_CM(1);
            if(meta.value_sketch1 == meta.value_sketch_min){
                meta.value_sketch1 = meta.value_sketch1 +1; 
                sketch1.write(meta.index_sketch1, meta.value_sketch1); 
                if(meta.vote_sketch1 ==0){
                    sketch_1key1.write(meta.index_sketch1, meta.key1_now_sketch1); 
                    sketch_2key1.write(meta.index_sketch1, meta.key2_now_sketch1); 
                    meta.vote_sketch1=meta.vote_sketch1+1; 
                    sketch_vote1.write(meta.index_sketch1, meta.vote_sketch1); 
                }else{ 
                    if(meta.key1_sketch1 == meta.key1_now_sketch1 && meta.key2_sketch1 == meta.key2_now_sketch1){ 
                        meta.vote_sketch1=meta.vote_sketch1+1; 
                        sketch_vote1.write(meta.index_sketch1, meta.vote_sketch1); 
                    }else{meta.vote_sketch1=meta.vote_sketch1-1; 
                        sketch_vote1.write(meta.index_sketch1, meta.vote_sketch1); } 
                }
            }
            //SKETCH_VOTE_CM(2);
            if(meta.value_sketch2 == meta.value_sketch_min){
                meta.value_sketch2 = meta.value_sketch2 +1; 
                sketch2.write(meta.index_sketch2, meta.value_sketch2); 
                if(meta.vote_sketch2 ==0){
                    sketch_1key2.write(meta.index_sketch2, meta.key1_now_sketch2); 
                    sketch_2key2.write(meta.index_sketch2, meta.key2_now_sketch2); 
                    meta.vote_sketch2=meta.vote_sketch2+1; 
                    sketch_vote2.write(meta.index_sketch2, meta.vote_sketch2); 
                }else{ 
                    if(meta.key1_sketch2 == meta.key1_now_sketch2 && meta.key2_sketch2 == meta.key2_now_sketch2){ 
                        meta.vote_sketch2=meta.vote_sketch2+1; 
                        sketch_vote2.write(meta.index_sketch2, meta.vote_sketch2); 
                    }else{meta.vote_sketch2=meta.vote_sketch2-1; 
                        sketch_vote2.write(meta.index_sketch2, meta.vote_sketch2); } 
                }
            }
        }

        forwarding.apply();
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
