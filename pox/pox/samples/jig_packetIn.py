from pox.core import core
import pox
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
import pox.lib.packet.ethernet as ethernet
import pox.lib.packet.ipv4 as ip

log = core.getLogger()

class GROUP9 ():
    def __init__ (self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp (self, event):
        log.info("installing ARP rule")
        fm = of.ofp_flow_mod()
        fm.priority = 0x7000
        fm.match.in_port = of.OFPP_LOCAL
        fm.match.nw_proto = ip.UDP_PROTOCOL
        fn.match.tp_src =   50000
        fm.actions.append(of.ofp_action_output(port=of.OFPP_CONTROLLER))
        event.connection.send(fm)
        

    def _handle_PacketIn(self, event):
        log.info("received a packet")

def launch():
    core.registerNew(GROUP9)

