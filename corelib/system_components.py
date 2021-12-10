"""The actual components of the distributed system: the nodes, messages, clients, etc."""

import copy

class BaseNode:
    """
    The base node from which other nodes are built. Represents a single node in a distributed
    system.
    """

    def __init__(self, addr, all_addresses):
        self.addr = addr
        self.all_addresses = all_addresses

        self.message_buffer = []

    def __str__(self):
        return f"(node_addr: {self.addr})"
    
    def __repr__(self):
        return self.__str__()
    
    def send_message(self, m, to_addr):
        self.message_buffer.append((copy.deepcopy(m), self.addr, to_addr))

    def base_receive_message(self, m, from_addr):
        """
        The method called by the state searcher during BFS. Not to be called by any particular
        implementation of a node.
        """
        cloned_node = copy.deepcopy(self)
        cloned_node.receive_message(m, from_addr)

        messages_to_send = cloned_node.message_buffer
        cloned_node.message_buffer = []

        return cloned_node, messages_to_send
    
    def receive_message(self, m, from_addr):
        """
        The node receiving a message. To be overridden.
        """
        raise NotImplementedError("Implement this method!")

class BaseMessage:
    def __init__(self):
        pass

    def __str__(self):
        return f"BaseMessage"

    def __repr__(self):
        return self.__str__()
