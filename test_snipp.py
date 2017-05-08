import sys
sys.path.append("/Users/pluto/Desktop/swmmio/swmmio/")
sys.path.append("/Users/pluto/Desktop/swmmio/swmmio/utils/")
from swmmio1 import Model
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

# Read the inp file using swmmio
model = Model('/Users/pluto/Desktop/6 Pond Control/aa_orifices_v3_scs_0005min_001yr.inp')
nodes = model.nodes()
condu = model.conduits()
ori = model.orifices()

G = nx.Graph() # Initialize the graph
for i in nodes['coords'].keys(): # Add junctions and ponds
    G.add_node(i, pos=(nodes['coords'][i][0][0], nodes['coords'][i][0][1]))
for i in condu['InletNode'].keys(): # Add conduits joining junctions and ponds
    G.add_edge(condu['InletNode'][i], condu['OutletNode'][i])
for i in ori['InletNode'].keys():
    G.add_edge(ori['InletNode'][i], ori['OutletNode'][i])

# Plot ponds and links
nx.draw_networkx_nodes(G, nx.get_node_attributes(G, 'pos'),node_color='#43cd80')
nx.draw_networkx_edges(G, nx.get_node_attributes(G, 'pos'),edge_color='#4682B4')
plt.show()
