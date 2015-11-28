from pox.core import core
import pox
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
import pox.lib.packet.ethernet as ethernet
import pox.lib.packet.ipv4 as ip
from pox.lib.util import dpid_to_str, str_to_dpid

log = core.getLogger()

class ARP_RULE ():
    def __init__ (self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp (self, event):
        log.info("installing ARP rule")
        fm = of.ofp_flow_mod()
        fm.priority = 0x7000
        fm.match.dl_type = ethernet.ARP_TYPE
        fm.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
        event.connection.send(fm)

        log.info("installing ICMP rule")
        fm = of.ofp_flow_mod() 
        fm.priority = 0x7000 
        fm.match.dl_type = ethernet.IP_TYPE 
        fm.match.nw_proto = ip.ICMP_PROTOCOL
        fm.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
        event.connection.send(fm)
        print(event.dpid)
        print(dpid_to_str(event.dpid))
        print(str_to_dpid(dpid_to_str(event.dpid)))

def launch():
    core.registerNew(ARP_RULE)

