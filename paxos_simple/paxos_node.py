"""
An implementation of the Paxos Made Simple algorithm. You can find it here:
https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
"""
from corelib.system_components import BaseMessage, BaseNode
from corelib.utils import dict_to_str

CLIENT_VALUE = "client_value"
PHASE1_PREPARE = "prepare"
PREPARE_ACK = "prepare_ack"
PHASE2_ACCEPT = "accept"
ACCEPT_ACK = "accept_ack"

class PaxosSimpleMessage(BaseMessage):
    def __init__(self, message_type, body):
        super().__init__(message_type)
        self.message_type = message_type
        self.body = body

class PaxosSimpleAcceptor(BaseNode):
    """
    """
    pass

class PaxosSimpleProposer(BaseNode):
    """
    A proposer from the paper.
    """

    def __init__(self, addr, all_addresses):
        super().__init__(addr, all_addresses)
        self.value = None
        self.proposal_num = addr
        self.acceptor_addresses = ['acceptor' in all_addresses]
        self.p1_acks = {}
        self.p2_acks = {}

        self.highest_proposal_num_seen = -1
        self.chosen = False

    def receive_message(self, m, from_addr):
        if m.message_type == CLIENT_VALUE:
            self.start_paxos(m)
        elif m.message_type == PHASE1_ACK:
            self.receive_prepare_ack(m, from_addr)
        elif m.message_type == PHASE2_ACK:
            self.receive_accept_ack(m, from_addr)
    
    def start_paxos(self, m):
        """
        Register the value that this proposer is trying to propose, and then start off Paxos by
        sending PREPAREs to the acceptors.
        """
        self.value = m.body["value"]
        prepare_message = PaxosSimpleMessage(PHASE1_PREPARE,
                            {"value": self.value, "proposal_num": self.proposal_num})

        for acc in self.acceptor_addresses:
            self.send_message(prepare_message, acc)
    
    def receive_prepare_ack(self, m, from_addr):
        """
        The response to a PREPARE is either that no proposal has been accepted so far, or that a
        proposal has been accepted, with that proposal's proposal number.
        """
        self.p1_acks[from_addr] = 1
        if "accepted_proposal" in m.body:
            if m.body["proposal_num"] > self.highest_proposal_num_seen:
                self.highest_proposal_num_seen = m.body["proposal_num"]
                self.value = m.body["accepted_proposal"]
        
        if len(self.p1_acks) > (len(self.acceptor_addresses) // 2 + 1):
            # Send 'accept' messages.
            for acc in self.acceptor_addresses:
                accept_message = PaxosSimpleMessage(
                    PHASE2_ACCEPT,
                    {"value": self.value, "proposal_num": self.proposal_num})
                self.send_message(accept_message, acc)

    def receive_accept_ack(self, m, from_addr):
        """
        The response to an ACCEPT. All we do here is know whether something has been chosen.
        """
        self.p2_acks[from_addr] = 1
        self.chosen = len(self.p2_acks) > len(self.acceptor_addresses // 2 + 1)
