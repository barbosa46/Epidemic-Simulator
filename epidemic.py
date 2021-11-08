import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import copy
from matplotlib.animation import FuncAnimation


###########CHANGE THIS#######################################################################
animation_interval = 5000 # time (ms) between each frame                                    #
time_steps = 10                                                                             #
avg_degree = 4                                                                              #
                                                                                            #
number_persons = 10                                                                         #
quarantine_probability = 0.2                                                                #
transmission_probability = 0.8                                                              # 
rewire_prob = 0.2 # probability of a node connected to an infected node rewiring each edge  #
recovery = 5 # time to recover from infection (in time_steps)                               #
quantine_duration = recovery                                                                #
immunity = 2 # immunity duration after recovery (in time_steps)                             #
time_to_first_quarentine = 4 # quarantines only will be possible after this time step       #
#############################################################################################

copy_quarantine=quarantine_probability
infected_time = []
infected_list = []
imune_time = []
imune_list = []
quarantined_list = []
quarantined_time = []
color_map = ['grey' for _ in range(number_persons)]

G=nx.generators.random_graphs.watts_strogatz_graph(number_persons,avg_degree,0.5) # Small world network


def rewire(G, n):
    neighbors = copy.deepcopy(G.neighbors(n))
    for neighbor in neighbors:
        if random.random() < rewire_prob:
            new_neighbor=(random.choice([i for i in G.nodes() if i not in G.neighbors(n) and i not in quarantined_list and i != n]))
            G.remove_edge(n, neighbor) 
            G.add_edge(n, new_neighbor)


def update_infected(t):
    quarantine_probability=0
    if t>time_to_first_quarentine:
        quarantine_probability=copy_quarantine #quarantine doesn't make sense in the early stage

    # update immunity status for each agent that ended the quarantine
    for i in copy.deepcopy(quarantined_time):
        if quantine_duration < t - i[1]:
            for _ in range(avg_degree):
                new_neighbor = random.choice([n for n in G.nodes() if n not in G.neighbors(i[0]) and n not in quarantined_list])
                G.add_edge(i[0],new_neighbor)

            quarantined_list.remove(i[0])
            quarantined_time.remove(i)

            imune_list.append(i[0])
            imune_time.append([i[0],t])

            color_map[i[0]]='green'

    # update immunity status for each imune agent
    for i in copy.deepcopy(imune_time):
        if immunity < t - i[1]:
            imune_time.remove(i)
            imune_list.remove(i[0])

            color_map[i[0]] = 'grey'

    # update infection and quarantine status for each infected agent
    infected_copy = copy.deepcopy(infected_time)
    for i in infected_copy:
        if recovery < t - i[1]:
            infected_time.remove(i)
            infected_list.remove(i[0])
            
            imune_list.append(i[0])
            imune_time.append([i[0],t])

            color_map[i[0]] = 'green'

        elif random.random() < quarantine_probability:

            quarantined_time.append([i[0],t])
            quarantined_list.append(i[0])
            infected_list.remove(i[0])
            infected_time.remove(i)
            G.remove_edges_from(list(G.edges(i[0])))
            color_map[i[0]]='yellow'

    # spread the infection across the neighbors of infected agents
    infected_list_copy = copy.deepcopy(infected_list)
    for i in infected_list_copy:
        for n in G.neighbors(i):
            if random.random()< transmission_probability:
                if n not in infected_list and n not in imune_list:
                    color_map[n]='red'
                    infected_time.append([n,t])
                    infected_list.append(n)
''' Rewire each edge of each neighbor of each infected agent '''
def update_network():
    rewired_nodes=[]
    for i in range(len(infected_list)):
        neighbors = G.neighbors(infected_list[i])
        for n in neighbors:
            if n not in rewired_nodes:
                rewired_nodes.append(n)
    for n in rewired_nodes:
        rewire(G, n)
    
def animate(frame):
    if frame%2==0:
        fig.clear()
        update_network()
        nx.draw_circular(G,node_color=color_map, with_labels=True)
    else:
        fig.clear()
        update_infected(frame)
        nx.draw_circular(G,node_color=color_map,with_labels=True)

''' You can run this function to compute all the steps without animating '''
def run():
    time = range(1,time_steps)
    time_to_peak=0
    quarantine_probability=0

    first_infected= random.randint(0,number_persons-1)
    infected_list.append(first_infected)
    infected_time.append([first_infected,0])
    color_map[first_infected]='orange'
    update_infected(0)
    for t in time:
        if t==10:
            quarantine_probability=copy_quarantine #quarantine doesn't make sense in the early stage

        update_network()
        update_infected(t)

    print('READY')

##########ANIMATION##########
fig=plt.figure()
first_infected= random.randint(0,number_persons-1)
infected_list.append(first_infected)
infected_time.append([first_infected,0])
color_map[first_infected]='orange'

anim = FuncAnimation(fig,animate,interval=animation_interval)
plt.show()
#############################
