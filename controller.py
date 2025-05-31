#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep
import json
import networkx as nx
import numpy as np
import grpc

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2 # type: ignore
import p4runtime_lib.helper # type: ignore
from p4runtime_lib.switch import ShutdownAllSwitchConnections # type: ignore

PORT_1 = 1
PORT_2 = 2
PORT_3 = 3
PORT_4 = 4
PORT_5 = 5
PORT_6 = 6

interface_relations = {}
node_to_index={}
hosts={}
switches={}
graph = nx.Graph()

def writeUpdateRules(p4info_helper,switch,dst_ip_addr,k1,k2):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.update_cost_tag",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.cost_tag_update",
        action_params={
            "upper_limit": k1,
            "lower_limit": k2
        })
    switch.WriteTableEntry(table_entry)
    # print("Installed update rule on %s" % switch.name)

def writeAddRules(p4info_helper,switch, dst_ip_addr):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.update_cost_tag",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.cost_tag_add",
        action_params={
        })
    switch.WriteTableEntry(table_entry)
    # print("Installed add rule on %s" % switch.name)

def writeDeleteRules(p4info_helper,switch, dst_ip_addr):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.update_cost_tag",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.cost_tag_delete",
        action_params={
        })
    switch.WriteTableEntry(table_entry)
    # print("Installed delete rule on %s" % switch.name)

def writeIPv4Rules(p4info_helper,switch,dst_ip_addr,dst_mac,egress_port):
    if egress_port=='1':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_1
            })
    elif egress_port=='2':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_2
            })
    elif egress_port=='3':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_3
            })
    elif egress_port=='4':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_4
            })
    elif egress_port=='5':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_5
            })
    else:
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.ipv4_lpm",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.ipv4_forward",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_6
            })
    switch.WriteTableEntry(table_entry)

    # print("Installed ipv4 rule on %s" % switch.name)

def readTableRules(p4info_helper, sw):
    
    print('\n----- Reading tables rules for %s -----' % sw.name)
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry
            # TODO For extra credit, you can use the p4info_helper to translate
            #      the IDs in the entry to names
            table_name = p4info_helper.get_tables_name(entry.table_id)
            print('%s: ' % table_name, end=' ')
            for m in entry.match:
                print(p4info_helper.get_match_field_name(table_name, m.field_id), end=' ')
                print('%r' % (p4info_helper.get_match_field_value(m),), end=' ')
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print('->', action_name, end=' ')
            for p in action.params:
                print(p4info_helper.get_action_param_name(action_name, p.param_id), end=' ')
                print('%r' % p.value, end=' ')
            print()

def printCounter(p4info_helper, sw, counter_name, index):
    
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print("%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            ))

def printGrpcError(e):
    print("gRPC Error:", e.details(), end=' ')
    status_code = e.code()
    print("(%s)" % status_code.name, end=' ')
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))

def dijkstra(graph,source,target):
    source_node=node_to_index[source]
    target_node=node_to_index[target]
    shortest_path = nx.shortest_path(graph, source=source_node, target=target_node)
    shortest_path_length = nx.shortest_path_length(graph, source=source_node, target=target_node)
    return shortest_path,shortest_path_length

def k_shortest_paths(graph, source, target, K):
    source=node_to_index[source]
    target=node_to_index[target]
    shortest_path = nx.shortest_path(graph, source=source, target=target, weight='weight')
    paths = [shortest_path]
    candidates = []
    for k in range(1, K):
        for i in range(len(paths[-1]) - 1):
            spur_node = paths[-1][i]
            root_path = paths[-1][:i + 1]
            
            edges_removed = []
            for path in paths:
                if len(path) > i and root_path == path[:i + 1]:
                    edge = (path[i], path[i + 1])
                    if graph.has_edge(*edge):
                        graph.remove_edge(*edge)
                        edges_removed.append(edge)
                spur_path = nx.shortest_path(graph, source=spur_node, target=target, weight='weight')
            if spur_path and spur_path[-1] == target:
                total_path = root_path[:-1] + spur_path
                total_weight = nx.path_weight(graph, total_path, weight='weight')
                
                heapq.heappush(candidates, (total_weight, total_path))
            
            for edge in edges_removed:
                graph.add_edge(*edge)
        
        if not candidates:
            break
        
        path = heapq.heappop(candidates)[1]
        paths.append(path)
    
    return paths

def reroute(graph,source,target,default_path):
    source_node=node_to_index[source]
    target_node=node_to_index[target]
    i=0
    p=[]
    p1,l=dijkstra(graph,source,target)
    p.append(p1)
    while len(p[-1])<len(default_path):
        i=i+1
        try:
            p2=k_shortest_paths(graph,source,target,i)
        except Exception as e:
            break
        else:
            p=p2
    return p

def get_key(my_dict,val):
    for key, value in my_dict.items():
         if val == value:
             return key
 
    return "There is no such Key"

def writeDefaultRules(p4info_helper,path,switches):
    src_node=get_key(node_to_index,path[0])
    dst_node=get_key(node_to_index,path[-1])
    for i in range(1,len(path)-1):
        egress_port=get_key(interface_relations[path[i]],path[i+1])
        writeIPv4Rules(p4info_helper,switches[path[i]-19],hosts[dst_node]['ip'][:-3],hosts[dst_node]['mac'],egress_port)

def writeCostRules(p4info_helper,path,switches,k1,k2):
    src_node=get_key(node_to_index,path[0])
    dst_node=get_key(node_to_index,path[-1])
    writeAddRules(p4info_helper,switches[path[1]-19],hosts[dst_node]['ip'][:-3])
    writeDeleteRules(p4info_helper,switches[path[-2]-19],hosts[dst_node]['ip'][:-3])
    if len(path)>4:
        for i in range(2,len(path)-2):
            writeUpdateRules(p4info_helper,switches[path[i]-19],hosts[dst_node]['ip'][:-3],k1,k2)

def writeRerouteRules(p4info_helper,switch,dst_ip_addr,dst_mac,egress_port,k):
    if egress_port=='1':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.reroute_path",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.reroute",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_1
            })
    elif egress_port=='2':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.reroute_path",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.reroute",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_2
            })
    elif egress_port=='3':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.reroute_path",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.reroute",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_3
            })
    elif egress_port=='4':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.reroute_path",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.reroute",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_4
            })
    elif egress_port=='5':
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.reroute_path",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.reroute",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_5
            })
    else:
        table_entry = p4info_helper.buildTableEntry(
            table_name="MyIngress.reroute_path",
            match_fields={
                "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
            },
            action_name="MyIngress.reroute",
            action_params={
                "dstAddr":dst_mac,
                "port":PORT_6
            })
    switch.WriteTableEntry(table_entry)
    # print("Installed reroute rule on %s" % switch.name)

def writeReroutePathRules(p4info_helper,path,switches,k,k1,k2):
    src_node=get_key(node_to_index,path[0])
    dst_node=get_key(node_to_index,path[-1])
    egress_port=get_key(interface_relations[path[0]],path[1])
    writeRerouteRules(p4info_helper,switches[path[0]-19],hosts[dst_node]['ip'][:-3],hosts[dst_node]['mac'],egress_port,k)
    path1=path[1:]
    src_node=get_key(node_to_index,path1[0])
    dst_node=get_key(node_to_index,path1[-1])
    try:
        if len(path1)>1:
            for i in range(0,len(path1)-1):
                egress_port=get_key(interface_relations[path1[i]],path1[i+1])
                writeIPv4Rules(p4info_helper,switches[path1[i]-19],hosts[dst_node]['ip'][:-3],hosts[dst_node]['mac'],egress_port)
    except Exception as e:
        return
    try:
        if len(path1)>2:
            for i in range(0,len(path1)-2):
                writeUpdateRules(p4info_helper,switches[path1[i]-19],hosts[dst_node]['ip'][:-3],k1,k2)
        writeDeleteRules(p4info_helper,switches[path1[-2]-19],hosts[dst_node]['ip'][:-3])
        
    except Exception as e:
        return

def find_deviation_point(path1, path2):
    deviation_point=None
    for x in range(0,len(path1)):
        if path1[x]!=path2[x]:
            deviation_point=x
            break
    if deviation_point is None:
        print("no deviation_point")
        return None
    return path1[x-1:]

def main(p4info_file_path, bmv2_file_path,k1,k2,k3):
    global graph, hosts, switches, node_to_index, interface_relations
    # Initialize the topology
    graph, hosts, switches, node_to_index, interface_relations=init_topology(graph, hosts, switches, node_to_index, interface_relations)
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
    switches=[]
    try:
        for i in range(0,18):
            x=i+1
            switches.append(p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s'+str(x),
            address='127.0.0.1:500'+str(x+50),
            device_id=i,
            proto_dump_file='logs/s'+str(x)+'-p4runtime-requests.txt'))
            switches[i].MasterArbitrationUpdate()
            switches[i].SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                        bmv2_json_file_path=bmv2_file_path)
            # print("Installed P4 Program using SetForwardingPipelineConfig on s"+str(x))
        default_paths0=[0,19,20,21,25,6]
        default_paths1=[7,25,26,27,8]
        default_paths2=[9,27,26,35,34,33,16]
        default_paths3=[17,34,35,29,28,10]
        default_paths4=[11,29,30,12]
        # default_paths5=[12,30,31,14]
        default_paths6=[18,35,31,13]
        default_paths7=[1,36,21,25,26,35,29,30,31,14]
        # default_paths=[default_paths0,default_paths1,default_paths2,default_paths3,default_paths4,default_paths5,default_paths6,default_paths7]
        default_paths=[default_paths0,default_paths1,default_paths2,default_paths3,default_paths4,default_paths6,default_paths7]
        for i in range(0,7):
            writeDefaultRules(p4info_helper,default_paths[i],switches)
            writeCostRules(p4info_helper,default_paths[i],switches,k1,k2)
        path=reroute(graph,'h2','h15',default_paths7)
        if path:
            for x in path:
                writeReroutePathRules(p4info_helper,find_deviation_point(x,default_paths7),switches,k3,k1,k2)
        
        # for i in range(0,18):
        #     readTableRules(p4info_helper, switches[i])
    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

def init_topology(graph, hosts, switches, node_to_index, interface_relations):
    topology_file = 'topology.json'
    with open(topology_file, 'r') as file:
        topology_data = json.load(file)
    hosts = topology_data.get('hosts', {})
    switches = topology_data.get('switches', {})
    nodes = list(hosts.keys()) + list(switches.keys())
    node_to_index = {node: index for index, node in enumerate(nodes)}
    num_nodes = len(nodes)
    adjacency_matrix = np.zeros((num_nodes, num_nodes))
    links = topology_data.get('links', [])
    for link in links:
        node1 = link[0].split('-')[0]
        node2 = link[1].split('-')[0]
        node1, interface1 = link[0].split('-') if '-' in link[0] else (link[0], 'default')
        node2, interface2 = link[1].split('-') if '-' in link[1] else (link[1], 'default')
        if interface1 != 'default': interface1 = interface1[1]
        if interface2 != 'default': interface2 = interface2[1]
        if node1 in nodes and node2 in nodes:
            index1 = node_to_index[node1]
            index2 = node_to_index[node2]
            if index1 not in interface_relations:
                interface_relations[index1] = {}
            if index2 not in interface_relations:
                interface_relations[index2] = {}
            interface_relations[index1][interface1] = index2
            interface_relations[index2][interface2] = index1
            adjacency_matrix[index1][index2] = 1
            adjacency_matrix[index2][index1] = 1
    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix[i])):
            if adjacency_matrix[i][j] == 1:
                graph.add_edge(i, j)
    return graph, hosts, switches, node_to_index, interface_relations

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.p4.p4info.txtpb')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/advanced_tunnel.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)



    main(args.p4info, args.bmv2_json,3000,5000,7000)
