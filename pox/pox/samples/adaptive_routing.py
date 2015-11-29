from pox.core import core
import pox
from pox.lib.util import dpid_to_str, str_to_dpid
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.addresses import IPAddr, EthAddr
import pox.lib.packet.ethernet as ethernet
import pox.lib.packet.ipv4 as ip
import threading, time

log = core.getLogger()

node_a = IPAddr("192.168.10.1")
node_b = IPAddr("192.168.10.2")
node_c = IPAddr("192.168.10.3")
node_d = IPAddr("192.168.10.4")

ip_list = [
    IPAddr("192.168.10.1"),
    IPAddr("192.168.10.2"),
    IPAddr("192.168.10.3"),
    IPAddr("192.168.10.4")
]

ip_to_mac_dict = {
    IPAddr("192.168.10.1"): EthAddr("00:00:00:00:00:00"),
    IPAddr("192.168.10.2"): EthAddr("00:00:00:00:00:00"),
    IPAddr("192.168.10.3"): EthAddr("00:00:00:00:00:00"),
    IPAddr("192.168.10.4"): EthAddr("00:00:00:00:00:00")
}

ip_to_dpid_dict = {
    IPAddr("192.168.10.1"): 0,
    IPAddr("192.168.10.2"): 0,
    IPAddr("192.168.10.3"): 0,
    IPAddr("192.168.10.4"): 0
}

cost_matrix = {
    IPAddr("192.168.10.1"): [1000, 1000, 1000, 1000],
    IPAddr("192.168.10.2"): [1000, 1000, 1000, 1000],
    IPAddr("192.168.10.3"): [1000, 1000, 1000, 1000],
    IPAddr("192.168.10.4"): [1000, 1000, 1000, 1000]
}

snapshot_mac_hop_rule = {
    IPAddr("192.168.10.1"): [0, 0, 0, 0],
    IPAddr("192.168.10.2"): [0, 0, 0, 0],
    IPAddr("192.168.10.3"): [0, 0, 0, 0],
    IPAddr("192.168.10.4"): [0, 0, 0, 0]
}

optimal_path = [node_a, node_d]
snapshot_optimal_path = [node_a, node_d]

def launch():
    core.registerNew(GROUP9)


def normal_functioning_rule(connection):
    log.info("NORMAL RULE install begin")
    fm = of.ofp_flow_mod()
    fm.priority = 0x0
    fm.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
    connection.send(fm)
    log.info("NORMAL RULE install end")


def lqi_to_controller_rule(connection):
    log.info("LQItoC install begin")
    fm = of.ofp_flow_mod()
    fm.priority = 0x7000
    fm.match.in_port = of.OFPP_LOCAL
    fm.match.dl_type = ethernet.IP_TYPE
    fm.match.nw_proto = ip.UDP_PROTOCOL
    fm.match.tp_dst = 50000
    fm.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
    connection.send(fm)
    log.info("LQItoC install end")


def lqi_broadcast(connection):
    log.info("lqi_broadcast install begin")
    fm = of.ofp_flow_mod()
    fm.priority = 0x7000
    #fm.match.in_port = of.OFPP_LOCAL
    fm.match.dl_type = ethernet.IP_TYPE
    fm.match.nw_proto = ip.UDP_PROTOCOL
    fm.match.tp_dst = 40000
    fm.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
    connection.send(fm)
    log.info("lqi_broadcast install end")


def lqi_response(connection):
    log.info("lqi_broadcast install begin")
    fm = of.ofp_flow_mod()
    fm.priority = 0x7000
    #fm.match.in_port = of.OFPP_LOCAL
    fm.match.dl_type = ethernet.IP_TYPE
    fm.match.nw_proto = ip.UDP_PROTOCOL
    fm.match.tp_dst = 40002
    fm.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
    connection.send(fm)
    log.info("lqi_broadcast install end")


def parse_lqi(udp_packet):
    print("UDP Packet: ", udp_packet.payload)
    values = udp_packet.payload.split(';')
    src_ip = IPAddr("0.0.0.0")
    for value in values:
        if value.split(',')[2] == "1000":
            src_ip = IPAddr(value.split(',')[0])
            break
    print("Source IP:", src_ip)
    lqi_parsed = {}
    for idx, value in enumerate(values):
        information = value.split(',')
        lqi_parsed[IPAddr(information[0])] = [EthAddr(information[1]), information[2]]
        if EthAddr(information[1]).toStr() != "00:00:00:00:00:00":
            ip_to_mac_dict[IPAddr(information[0])] = EthAddr(information[1])
        if src_ip == IPAddr("0.0.0.0"):
            log.error("parse_lqi: source IP is 0.0.0.0")
            return
        if int(information[2]) == 0:
            cost_matrix[src_ip][idx] = 999
        else:
            cost_matrix[src_ip][idx] = int(information[2])
    # print("LQI Parsed: ", lqi_parsed)
    # print("Cost Matrix: ", cost_matrix)
    optimal_path_finder()


def optimal_path_finder():
    log.info("optimal_path_finder: begin")
    print("Cost Matrix: ", cost_matrix)
    min_from_a = cost_matrix[node_a].index(min(cost_matrix[node_a][0:4]))
    min_from_b = cost_matrix[node_b].index(min(cost_matrix[node_b][2:4]))
    print("Cost Matrix for A: ", cost_matrix[node_a])
    print("Min from A: ", min(cost_matrix[node_a][1:4]), " Min from B: ", min(cost_matrix[node_b][2:4]))
    print("Min from A: ", min_from_a, " Min from B: ", min_from_b)
    del optimal_path[:]
    optimal_path.append(node_a)
    if ip_list[min_from_a] == node_b:
        optimal_path.append(node_b)
        if ip_list[min_from_b] == node_c:
            optimal_path.append(node_c)
    elif ip_list[min_from_a] == node_c:
        optimal_path.append(node_c)
    optimal_path.append(node_d)
    print('Optimal Path: ', optimal_path)
    log.info("optimal_path_finder: end")
    # network_updater()


def reset_flows():
    log.info("reset_flows begin")
    connection_a = core.openflow.getConnection(ip_to_dpid_dict[node_a])
    connection_b = core.openflow.getConnection(ip_to_dpid_dict[node_b])
    connection_c = core.openflow.getConnection(ip_to_dpid_dict[node_c])
    connection_d = core.openflow.getConnection(ip_to_dpid_dict[node_d])
    if connection_a is not None:
        connection_a.send(of.ofp_flow_mod(command=of.OFPFC_DELETE))
        startup_rules(connection_a)
    else:
        log.error("CONNECTION A is NULL")
    if connection_b is not None:
        connection_b.send(of.ofp_flow_mod(command=of.OFPFC_DELETE))
        startup_rules(connection_b)
    else:
        log.error("CONNECTION B is NULL")
    if connection_c is not None:
        connection_c.send(of.ofp_flow_mod(command=of.OFPFC_DELETE))
        startup_rules(connection_c)
    else:
        log.error("CONNECTION C is NULL")
    if connection_d is not None:
        connection_d.send(of.ofp_flow_mod(command=of.OFPFC_DELETE))
        startup_rules(connection_d)
    else:
        log.error("CONNECTION D is NULL")
    log.info("reset_flows end")


def startup_rules(connection):
    log.info("startup_rules begin")
    normal_functioning_rule(connection)
    lqi_to_controller_rule(connection)
    #lqi_broadcast(connection)
    #lqi_response(connection)
    log.info("startup_rules end")


def network_updater():
    threading.Timer(20.0, network_updater).start()
    log.info("network_updater: begin************************************************************")
    '''
    if optimal_path == snapshot_optimal_path:
        log.info("network_updater: no modification in optimal path")
        return
    '''
    # reset_flows()
    if optimal_path == [node_a, node_d]:
        mac_hopping_rule(ip_list[0], ip_list[3], ip_list[3], True)
        mac_hopping_rule(ip_list[3], ip_list[0], ip_list[0], True)
    elif optimal_path == [node_a, node_b, node_d]:
        mac_hopping_rule(ip_list[0], ip_list[3], ip_list[1], True)
        mac_hopping_rule(ip_list[1], ip_list[3], ip_list[3])
        mac_hopping_rule(ip_list[3], ip_list[0], ip_list[1], True)
        mac_hopping_rule(ip_list[1], ip_list[0], ip_list[0])
    elif optimal_path == [node_a, node_c, node_d]:
        mac_hopping_rule(ip_list[0], ip_list[3], ip_list[2], True)
        mac_hopping_rule(ip_list[2], ip_list[3], ip_list[3])
        mac_hopping_rule(ip_list[3], ip_list[0], ip_list[2], True)
        mac_hopping_rule(ip_list[2], ip_list[0], ip_list[0])
    elif optimal_path == [node_a, node_b, node_c, node_d]:
        mac_hopping_rule(ip_list[0], ip_list[3], ip_list[1], True)
        mac_hopping_rule(ip_list[1], ip_list[3], ip_list[2])
        mac_hopping_rule(ip_list[2], ip_list[3], ip_list[3])
        mac_hopping_rule(ip_list[3], ip_list[0], ip_list[2], True)
        mac_hopping_rule(ip_list[2], ip_list[0], ip_list[1])
        mac_hopping_rule(ip_list[1], ip_list[0], ip_list[0])
    del snapshot_optimal_path[:]
    snapshot_optimal_path.extend(optimal_path)
    log.info("network_updater: end************************************************************")


def mac_hopping_rule(src_ip, dst_ip, next_hop_ip, is_edge=False):
    log.info("mac_hopping_rule begin")
    if ip_to_dpid_dict[src_ip] == 0:
        log.info("DPID is 0")
        return
    if ip_to_mac_dict[dst_ip] == EthAddr("00:00:00:00:00:00"):
        log.info("Mac for DST " + dst_ip.toStr() + " is NOT known")
        return
    if ip_to_mac_dict[next_hop_ip] == EthAddr("00:00:00:00:00:00"):
        log.info("Mac for Next Hop : " + next_hop_ip.toStr() + " is NOT known")
        return

    fm = of.ofp_flow_mod()
    fm.priority = 0x6FFF
    # if is_edge:
    #    fm.match.in_port = of.OFPP_LOCAL
    fm.match.dl_type = ethernet.IP_TYPE
    if not is_edge:
        fm.match.dl_dst = ip_to_mac_dict[src_ip]
    fm.match.nw_dst = dst_ip
    fm.match.nw_proto = ip.UDP_PROTOCOL
    fm.match.tp_dst = 45000
    fm.actions.append(of.ofp_action_dl_addr.set_dst(ip_to_mac_dict[next_hop_ip]))
    fm.actions.append(of.ofp_action_dl_addr.set_src(ip_to_mac_dict[src_ip]))
    if is_edge:
        fm.actions.append(of.ofp_action_output(port=1))
    else:
        fm.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))

    print "Next Hop Node number is: " + next_hop_ip.toStr().split('.')[-1]
    '''if fm == snapshot_mac_hop_rule[src_ip][int(next_hop_ip.toStr().split('.')[-1]) - 1]:
        print("NO changes in the rule from " + src_ip.toStr() + " to " + next_hop_ip.toStr())
        return
    '''
    connection = core.openflow.getConnection(ip_to_dpid_dict[src_ip])
    if connection is None:
        print "Connection is NULL"
    else:
        print "Connection PRESENT"
    connection.send(fm)
    snapshot_mac_hop_rule[src_ip][int(next_hop_ip.toStr().split('.')[-1]) - 1] = fm
    log.info("MAC_hop end")
    print ip_to_mac_dict
    log.info("mac_hopping_rule end")


class GROUP9:
    def __init__(self):
        core.openflow.addListeners(self)
        network_updater()

    def _handle_ConnectionUp(self, event):
        startup_rules(event.connection)

    def _handle_PacketIn(self, event):
        log.info("PacketIn begin")
        packet = event.parsed
        print("PacketIn: Packet received: ", packet.src)

        eth_packet = packet.find('ethernet')
        if eth_packet is None:
            log.info("PacketIn: ethernet packet is None")
            return

        ip_packet = packet.find("ipv4")
        if ip_packet is None:
            log.info("PacketIn: not an IP packet")
            return

        udp_packet = packet.find("udp")
        if udp_packet is None:
            log.info("PacketIn: not a UDP packet")
            return

        if udp_packet.dstport != 50000:
            log.info("not an LQI message")
            return
        # print "Payload: " + udp_packet.payload

        src_ip = ip_packet.srcip
        ip_to_dpid_dict[src_ip] = event.dpid
        parse_lqi(udp_packet)
        print("ORIG SRC IP: ",  src_ip)
        log.info("PacketIn end")

