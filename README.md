# understando
A small sandbox for you to be able to quickly implement a distributed algorithm and play around with
it. The idea is that you can see how your algorithm fares against multiple event orderings.  

This is heavily inspired by a [series of distributed labs assignments](https://github.com/emichael/dslabs)
I had to do a few years ago. I really liked the model-checking tests those labs had and I wanted to
create an interactive version.

## How to use it
Here is a sample of how to interact with the Paxos Made Simple algorithm and explore its states.
```
~ $ git clone https://github.com/kauboy26/understando.git
~ $ cd understando
~/understando $ python3
>>> 
```
Once the interpreter is running, we can import `understando`'s components. You can go ahead and copy
paste the following to the interpreter:
```
from paxos_simple.paxos_node import PaxosSimpleAcceptor, PaxosSimpleProposer, PaxosSimpleMessage
from paxos_simple.paxos_node import CLIENT_VALUE
from corelib import search

import json

# Create some acceptor nodes
acc_nodes = [PaxosSimpleAcceptor(f'acceptor{i}', []) for i in range(3)]
# Create some proposer nodes
prop_nodes = [PaxosSimpleProposer(f'proposer{i}', [acc.addr for acc in acc_nodes], i) for i in range(2)]

# Start off by having a message to each node.
starting_messages = [(PaxosSimpleMessage(CLIENT_VALUE, {"value": p.addr}), 'client1', p.addr) for p in prop_nodes]
start_state = search.build_start_state_from_raw_materials(starting_messages, acc_nodes + prop_nodes)
```
This builds the start state from where we start the search. We can define some predicates for the
states we care about, as well as define which states we should skip. In this example, we want to
find states in which a `proposer`'s value has been chosen, and we don't want to skip looking at any
states.
```
def value_chosen(state):
    for addr, node in state.nodes.items():
        if isinstance(node, PaxosSimpleProposer) and node.chosen:
            return True
    return False

def should_skip(state):
    return False
```
We can start the search:
```
states_found, states_examined = search.system_state_BFS(start_state, 15, value_chosen, should_skip)
```
This may take a few seconds. We can alter the depth to make it run faster, but that would limit the
number of explored states. Finally, we can examine which states were found.
```
curr = states_found[0]
```
We can print out one of the states we found and examine its ancestors:
```
i = 0
while curr is not None:
    print('state:', i)
    i += 1

    search.print_unlinked_state(curr)
    curr = curr.previous_state
```
We can also restart the search from any other state we found interesting:
```
interesting = states_found[12]
# states_found, states_examined = search.system_state_BFS(interesting, 15, new_predicate, should_skip)
```
