"""Represents the state of the entire system."""

import collections

class MessageQueue:
    """A map of the messages for each address."""
    def __init__(self):
        self.address_to_messages = {}

    def shallow_copy(self):
        copy = MessageQueue()
        copy.address_to_messages = self.address_to_messages.copy()

        return copy

    def get_message(self, addr=None):
        """
        Clone the message queue and pops a message off the cloned message queue. Return both the
        message and the cloned message queue.
        """
        if addr is None:
            raise ValueError("'None' address passed.")
        
        if addr not in self.address_to_messages or not self.address_to_messages[addr]:
            # print(f"Doing nothing; no messages to address {addr}.")
            return (None, self)

        copy = self.shallow_copy()
        copy.address_to_messages[addr] = copy.address_to_messages[addr].copy()
        m = copy.address_to_messages[addr].pop()

        return (m, copy)

    def send_messages(self, messages_to_send):
        """
        Clones the message queue and returns the new queue, with the messages appended to the
        appropriate channels.
        """
        copy = self.shallow_copy()

        addrs_channels_cloned = {}

        for m, from_addr, to_addr in messages_to_send:
            if to_addr in addrs_channels_cloned:
                copy.address_to_messages[to_addr].append((m, from_addr))
                continue
            
            addrs_channels_cloned[to_addr] = 1
            if to_addr not in copy.address_to_messages:
                copy.address_to_messages[to_addr] = []
            else:
                copy.address_to_messages[to_addr] = self.address_to_messages[to_addr].copy()
            copy.address_to_messages[to_addr].append((m, from_addr))
        
        return copy

    def __str__(self):
        """
        Convert the message queue to a string representation, to be used to hash the state later.
        """
        pieces = []
        for k in sorted(self.address_to_messages.keys()):
            if not self.address_to_messages[k]:
                continue
            pieces.extend(['(address:', str(k), '; m:', str(self.address_to_messages[k]), ')'])

        return ' '.join(pieces)


class SystemState:
    """
    The state of the entire system - the nodes and the messages to the nodes - at some particular
    point in time.
    """

    def __init__(self, messages=None, nodes=None, previous_state=None):
        self.messages = messages
        self.nodes = nodes
        self.previous_state = previous_state

        pass

    def generate_successor_state_from_message(self, m, from_addr, to_addr):
        """A way to send a message into the message queue from an arbitrary source."""

        message_queue_copy = self.messages.send_messages([(m, from_addr, to_addr)])

        state_copy = SystemState(message_queue_copy, self.nodes, self)

        return state_copy

    def generate_successor_state_from_address(self, addr):
        """
        Generate a successor state by allowing an address to receive a message.
        """
        # 'm_a' is a (message, from_addr) tuple.
        m_a, message_queue_copy = self.messages.get_message(addr)
        if m_a is None:
            return None
        
        node_copy, messages_to_send = self.nodes[addr].base_receive_message(m_a[0], m_a[1])
        message_queue_copy = message_queue_copy.send_messages(messages_to_send)

        state_copy = SystemState(message_queue_copy, self.nodes.copy(), self)
        state_copy.nodes[addr] = node_copy

        return state_copy

    def generate_successor_state_frontier(self):
        """
        Generates successor states to this state. There are two kinds of events that can lead to a
        next state, local events at a node or a message received by the node.
        """

        frontier = []

        for addr in self.nodes.keys():
            next_state = self.generate_successor_state_from_address(addr)
            if next_state is None:
                continue

            frontier.append(next_state)

        return frontier
    
    def __str__(self):
        """
        Converts to a string form for hashing.
        """
        pieces = ['n:']
        for addr in sorted(self.nodes.keys()):
            pieces.extend([addr, ':', str(self.nodes[addr])])
        
        pieces.append('mq:')
        pieces.append(str(self.messages))

        return ' '.join(pieces)

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
        # print(f"d: {d}, curr: ({str(curr_state)})")
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

class SearchAlgorithm:
    """
    The recommended way to initialize an algorithm and start it.
    """

    def __init__(self, nodes, starting_messages):
        """Set up the starting state for the search."""

        messages = MessageQueue()
        messages = messages.send_messages(starting_messages)

        node_dict = {}
        for n in nodes:
            node_dict[n.addr] = n

        self.init_state = SystemState(messages, node_dict)

    def start_search(self, depth_limit, predicate):
        return system_state_BFS(self.init_state, depth_limit, predicate)
