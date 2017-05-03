from swmmio import swmmio
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style("white")

# Read the inp file using swmmio
model = swmmio.Model('/Users/pluto/Desktop/6 Pond Control/aa_orifices_v3_scs_0005min_001yr.inp')
nodes = model.nodes()
condu = model.conduits()

G = nx.Graph() # Initialize the graph
for i in nodes['coords'].keys(): # Add junctions and ponds
    G.add_node(i, pos=(nodes['coords'][i][0][0], nodes['coords'][i][0][1]))
for i in condu['InletNode'].keys(): # Add conduits joining junctions and ponds
    G.add_edge(condu['InletNode'][i], condu['OutletNode'][i])

# Plot ponds and links
nx.draw_networkx_nodes(G, nx.get_node_attributes(G, 'pos'),node_color='#43cd80')
nx.draw_networkx_edges(G, nx.get_node_attributes(G, 'pos'),edge_color='#4682B4')
plt.show()
