"""Represents the state of the entire system."""

import collections

from corelib.utils import dict_to_str

class MessageFunnel:
    """
    A container to hold the messages to a particular destination from various sources.
    """

    def __init__(self, destination=None, source_to_message=None):
        self.destination = destination
        self.source_to_message = {} if source_to_message is None else source_to_message
    
    def get_message(self, from_addr):
        """
        Copies the funnel and returns a message and the copied funnel without the message.
        """
        if from_addr not in self.source_to_message:
            return (None, self)
        
        copy = MessageFunnel(self.destination, self.source_to_message.copy())
        m = copy.source_to_message.pop(from_addr)

        return (m, copy)

    def add_message(self, m, from_addr):
        """
        Copies the funnel and returns the copied funnel with the new message.
        """
        copy = MessageFunnel(self.destination, self.source_to_message.copy())
        copy.source_to_message[from_addr] = m

        return copy

    def get_from_addresses(self):
        return list(self.source_to_message.keys())

    def __repr__(self):
        return f'{{"dest": "{self.destination}", "sources": {dict_to_str(self.source_to_message)}}}'
    
    def __str__(self):
        return self.__repr__()

    def __bool__(self):
        return bool(self.source_to_message)

class MessageNetwork:
    """A map of the messages for each address."""
    def __init__(self):
        self.address_to_messages = {}

    def shallow_copy(self):
        copy = MessageNetwork()
        copy.address_to_messages = self.address_to_messages.copy()

        return copy

    def get_message(self, from_addr, to_addr):
        """
        Clone the message queue and pops a message off the cloned message queue. Return both the
        message and the cloned message queue.
        """
        if to_addr not in self.address_to_messages or not self.address_to_messages[to_addr]:
            return (None, self)

        (m, copied_funnel) = self.address_to_messages[to_addr].get_message(from_addr)
        copy = self.shallow_copy()
        copy.address_to_messages[to_addr] = copied_funnel

        return (m, copy)

    def send_messages(self, messages_to_send):
        """
        Clones the message queue and returns the new queue, with the messages appended to the
        appropriate channels.
        """
        copy = self.shallow_copy()

        for m, from_addr, to_addr in messages_to_send:
            if to_addr not in copy.address_to_messages:
                copy.address_to_messages[to_addr] = MessageFunnel(to_addr)
            copy.address_to_messages[to_addr] = copy.address_to_messages[to_addr].add_message(m, from_addr)
        
        return copy

    def __str__(self):
        """
        Convert the message queue to a string representation, to be used to hash the state later.
        Unfortunately, a simple freeze of the entire state cannot be performed because some
        variables exist only for implementation convenience and aren't actually tied to the actual
        system state.

        It is duty of the distributed algorithm implementers to make sure the node's string
        representation correctly captures the state.
        """
        return dict_to_str(self.address_to_messages)

class SystemState:
    """
    The state of the entire system - the nodes and the messages to the nodes - at some particular
    point in time.
    """

    def __init__(self, message_network=None, nodes=None, previous_state=None):
        self.message_network = message_network
        self.nodes = nodes
        self.previous_state = previous_state

    def generate_successor_state_from_send_message(self, m, from_addr, to_addr):
        """A way to send a message into the message queue from an arbitrary source."""

        message_network_copy = self.message_network.send_messages([(m, from_addr, to_addr)])

        state_copy = SystemState(message_network_copy, self.nodes, self)

        return state_copy

    def generate_successor_state_from_addresses(self, from_addr, to_addr):
        """
        Generate a successor state by allowing an address to receive a message.
        """
        m, message_network_copy = self.message_network.get_message(from_addr, to_addr)
        if m is None:
            return None
        
        node_copy, messages_to_send = self.nodes[to_addr].base_receive_message(m, from_addr)
        message_network_copy = message_network_copy.send_messages(messages_to_send)

        state_copy = SystemState(message_network_copy, self.nodes.copy(), self)
        state_copy.nodes[to_addr] = node_copy

        return state_copy

    def generate_successor_state_frontier(self):
        """
        Generates successor states to this state. There are two kinds of events that can lead to a
        next state, local events at a node or a message received by the node.
        """

        frontier = []

        for addr in self.nodes.keys():
            # TODO: Fix this long chain of calls.
            for from_addr in self.message_network.address_to_messages[addr].get_from_addresses():
                next_state = self.generate_successor_state_from_addresses(from_addr, addr)
                if next_state is None:
                    continue

                frontier.append(next_state)

        return frontier
    
    def __str__(self):
        """
        Converts to a string form for hashing.
        """
        return f'{{"nodes": {dict_to_str(self.nodes)}, "messages": {str(self.message_network)}}}'

def build_start_state_from_raw_materials(starting_messages, nodes):
    """
    Build a start state with the given nodes in whatever state, and some starting messages for
    the network.
    starting_messages: a list of (message, from_addr, to_addr) tuples
    nodes: a list of nodes
    """
    messages = MessageNetwork()
    messages = messages.send_messages(starting_messages)

    node_dict = {}
    for n in nodes:
        node_dict[n.addr] = n

    return SystemState(messages, node_dict)

def build_start_state_from_existing_state(existing_state):
    """
    Builds a state from an existing state. The resulting state will have lost its history.
    """
    # The previous state of the returned state is wiped.
    return SystemState(existing_state.message_network, existing_state.nodes, None)

def system_state_BFS(start_state, depth_limit, predicate):
    """
    Run a BFS and capture all the states that are matching the predicate, until the given depth has
    been exhausted.
    """
    states_found = []

    states_examined = {}
    state_queue = collections.deque([])

    state_queue.appendleft((0, start_state))

    while len(state_queue) != 0:
        d, curr_state = state_queue.pop()
        if str(curr_state) in states_examined or d >= depth_limit:
            continue

        if predicate(curr_state):
            states_found.append(curr_state)
        
        states_examined[str(curr_state)] = 1

        frontier = curr_state.generate_successor_state_frontier()
        for next_state in frontier:
            if str(next_state) not in states_examined:
                state_queue.appendleft((d + 1, next_state))

    return states_found, states_examined

def find_predicate_transition(start_state, end_state, predicate):
    """
    For states [start_state -> S0 -> S1 -> ... -> end_state], returns the states at which the
    predicate evaluates to True.
    """
    curr = end_state
    states_found = []
    while curr is not None and str(curr) != str(start_state):
        if predicate(curr):
            states_found.append(curr)
        curr = curr.previous_state
    
    if curr is not None:
        if predicate(curr):
            states_found.append(curr)
    else:
        print(f"Start state ({start_state}) was not an ancestor of the given end state ({end_state})")
    return states_found
