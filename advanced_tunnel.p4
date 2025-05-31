/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_COSTTAG = 200;
const bit<32> MAX_TUNNEL_ID = 1 << 16;


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
    bit<8>    diffserv;
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

header cost_tag{
    bit<8> oringin_proto;
    bit<3> priority;
    bit<48> enter_timestamp;
    bit<48> leave_timestamp;
    bit<19> depth;
    bit<10> plength;
}


struct metadata {
    /* empty */
}

struct headers {
    ethernet_t              ethernet;
    ipv4_t                  ipv4;
    cost_tag                cost_tag;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
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
            TYPE_IPV4:parse_ipv4;
            default:accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            TYPE_COSTTAG:parse_cost_tag;
            default:accept;
        }
    }

    state parse_cost_tag{
        packet.extract(hdr.cost_tag);
        standard_metadata.priority=hdr.cost_tag.priority;
        transition accept;
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

    counter(MAX_TUNNEL_ID, CounterType.packets_and_bytes) Counter;
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    action reroute(macAddr_t dstAddr, egressSpec_t port){
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
    }

    table reroute_path{
        key={
            hdr.ipv4.dstAddr:lpm;
        }
        actions={
            reroute;
            NoAction;
        }
        default_action=NoAction;
    }

    action cost_tag_add(){
        hdr.cost_tag.setValid();
        hdr.cost_tag.oringin_proto=hdr.ipv4.protocol;
        hdr.ipv4.protocol=TYPE_COSTTAG;
        hdr.cost_tag.enter_timestamp=standard_metadata.ingress_global_timestamp;
        hdr.cost_tag.priority= 0 ;
        hdr.cost_tag.plength=1;
        hdr.cost_tag.depth=standard_metadata.enq_qdepth;
    }

    action cost_tag_update(bit<48> upper_limit,bit<48> lower_limit){
        bit<48> t;
        t=standard_metadata.ingress_global_timestamp-hdr.cost_tag.enter_timestamp;
        if(t>upper_limit){
            hdr.cost_tag.priority=2;
            standard_metadata.priority=2;
        }else if(t<lower_limit){
            hdr.cost_tag.priority=0;
            standard_metadata.priority=0;
        }
    }

    action cost_tag_delete(){
        hdr.cost_tag.leave_timestamp=standard_metadata.ingress_global_timestamp;
        clone_preserving_field_list(CloneType.I2E,100,0);
        hdr.ipv4.protocol=hdr.cost_tag.oringin_proto;
        hdr.cost_tag.setInvalid();
    }

    table update_cost_tag{
        key={
            hdr.ipv4.dstAddr:lpm;
        }
        actions={
            cost_tag_add;
            cost_tag_update;
            cost_tag_delete;
            drop;
        }
        default_action=drop;
    }


    apply {
        Counter.count((bit<32>) 100);
        if(hdr.ipv4.isValid()){
            ipv4_lpm.apply();
        }
        if(hdr.cost_tag.isValid()){
            update_cost_tag.apply();
            reroute_path.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {
        if(hdr.cost_tag.depth<standard_metadata.enq_qdepth){
            hdr.cost_tag.depth=standard_metadata.enq_qdepth;
        }  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { 
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
     }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.cost_tag);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;