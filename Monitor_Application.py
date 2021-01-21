from operator import attrgetter
from ryu.app import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub


class SimpleMonitor13(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY, ofproto.OFPP_ALL)
        datapath.send_msg(req)

        req = parser.OFPPortDescStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes     duration')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------  -----------')
        #for flow in body:
        #    print(flow)
        #    break
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            #print("Flow Stats Reply : \n", ev.msg.datapath.id, stat)
            #break
            self.logger.info('%016x %8x %17s %8x %8d %8d %8d',
                             ev.msg.datapath.id,
                             stat.match['in_port'], stat.match['eth_dst'],
                             stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count, stat.duration_sec)

   
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('datapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error  % Packet Loss')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------  -------------')
        for stat in sorted(body, key=attrgetter('port_no')):
            #print("Port Stats Reply : \n", ev.msg.datapath.id, stat)
            #break
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d %8d',
                             ev.msg.datapath.id, stat.port_no,
                             stat.rx_packets, stat.rx_bytes, stat.rx_errors,
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors, 100 - (((stat.rx_packets)/(stat.tx_packets)) * 100))

    @set_ev_cls(ofp_event.EventOFPPortDescStatsReply, MAIN_DISPATCHER)
    def port_desc_stats_reply_handler(self, ev):

        self.logger.info('Datapath       port       '
                         'MAC address     '
                         'Bit rate(kbps)')
        self.logger.info('----------  ------  '
                         '   -------------  '
                         '   ----------- ')
        ports = []
        for p in ev.msg.body:  
            ports.append('port_no=%d hw_addr=%s name=%s config=0x%08x '
                            'state=0x%08x curr=0x%08x advertised=0x%08x '
                            'supported=0x%08x peer=0x%08x curr_speed=%d '
                            'max_speed=%d' %
                            (p.port_no, p.hw_addr,
                            p.name, p.config,
                            p.state, p.curr, p.advertised,
                            p.supported, p.peer, p.curr_speed,
                            p.max_speed))
            if p.port_no <= 100:
                print('{}               {}       {}    {}'.format(ev.msg.datapath.id, p.port_no,p.hw_addr, p.curr_speed))
                
                
