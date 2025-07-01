# got.py

from pyvis import network as net
import pandas as pd
import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
import os

# Load the CSV
csv_path = os.path.join(os.path.dirname(__file__), "got-edges.csv")
got_data = pd.read_csv(csv_path)

# Build a directed graph (DiGraph)
G = nx.DiGraph()
for src, dst, w in zip(got_data['Source'], got_data['Target'], got_data['Weight']):
    G.add_edge(src, dst, weight=w)

# Create pyvis network
got_net = net.Network(height='800px', width='100%', heading='', notebook=False, cdn_resources='remote', directed=True)
got_net.barnes_hut()

# Add nodes and edges
for src, dst, w in G.edges(data='weight'):
    got_net.add_node(src, src, title=src)
    got_net.add_node(dst, dst, title=dst)
    got_net.add_edge(src, dst, value=w)

# Add neighbor info
neighbor_map = got_net.get_adj_list()
for node in got_net.nodes:
    node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
    node["value"] = len(neighbor_map[node["id"]])

# Optional controls
got_net.repulsion()
got_net.show_buttons(filter_=['physics'])

# Export to HTML
got_net.write_html("gameofthrones.html")

# Display in Streamlit
st.title("Game of Thrones Network")
components.html(open("gameofthrones.html", "r", encoding="utf-8").read(), height=800, scrolling=True)

# -------------------------
# Metrics and explanations
# -------------------------
st.header("Network Metrics and Their Meanings")

# Density
density = nx.density(G)
st.subheader("Network Sparsity / Density")
st.write(f"**Density:** {density:.4f}")
st.markdown("Density is the ratio of actual edges to the total possible edges. It tells how 'full' the network is.")

# Assortativity
assortativity = nx.degree_assortativity_coefficient(G)
st.subheader("Network Assortativity")
st.write(f"**Assortativity Coefficient:** {assortativity:.4f}")
st.markdown("Assortativity measures how nodes tend to connect to others with similar degree. Positive values indicate similar-degree nodes connect more often.")

# Global clustering coefficient
try:
    clustering = nx.average_clustering(G.to_undirected())
    st.subheader("Global Clustering Coefficient")
    st.write(f"**Average Clustering Coefficient:** {clustering:.4f}")
    st.markdown("This measures the tendency of a node's neighbors to be connected with each other — forming 'triangles' or tight-knit groups.")
except:
    st.warning("Could not compute clustering coefficient.")

# Strongly connected components
strongly_connected = list(nx.strongly_connected_components(G))
st.subheader("Strongly Connected Components")
st.write(f"**Number of Strongly Connected Components:** {len(strongly_connected)}")
st.markdown("In a directed graph, a strongly connected component is a set of nodes where each node is reachable from any other node in the same set.")

# Weakly connected components
weakly_connected = list(nx.weakly_connected_components(G))
st.subheader("Weakly Connected Components")
st.write(f"**Number of Weakly Connected Components:** {len(weakly_connected)}")
st.markdown("A weakly connected component is a set of nodes that would be connected if all edge directions were ignored.")
