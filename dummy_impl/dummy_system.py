"""A sample implementation for the sake of testing."""

from corelib import system_components
from corelib.utils import dict_to_str

class DummyMessage(system_components.BaseMessage):

    def __init__(self, body):
        super().__init__('')
        self.body = body
    
    def __str__(self):
        return dict_to_str(self.body)
    
    def __repr__(self):
        return self.__str__()

class DummyNode(system_components.BaseNode):
    def __init__(self, addr, all_addresses):
        super().__init__(addr, all_addresses)

        self.value = addr
        self.am_leader = False
        self.votes = 0
        self.other_addresses = [a for a in all_addresses if a != addr]
    
    def __str__(self):
        return f'{{"addr": "{self.addr}", "val": "{self.value}", "lead": "{self.am_leader}", "vote": {self.votes}}}'

    def __repr__(self):
        return self.__str__()

    def receive_message(self, m, from_addr):
        if 'start_election' in m.body:
            if not self.am_leader:
                self.votes = 1
                for to_addr in self.other_addresses:
                    self.send_message(DummyMessage({'request_vote': self.addr}), to_addr)
        elif 'ack' in m.body:
            self.votes += 1
            if self.votes == 3:
                self.am_leader = True
        elif 'reject' in m.body:
            self.votes = -1
            self.am_leader = False
        if 'request_vote' in m.body:
            candidate = m.body['request_vote']
            if candidate > self.value:
                self.send_message(DummyMessage({'ack': 1}), from_addr)
