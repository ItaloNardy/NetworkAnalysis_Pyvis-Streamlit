import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

# Load CSV data
csv_path = os.path.join(os.path.dirname(__file__), "got-edges.csv")
data = pd.read_csv(csv_path)

# Build full directed graph
G = nx.DiGraph()
for src, dst, weight in zip(data['Source'], data['Target'], data['Weight']):
    G.add_edge(src, dst, weight=weight)

# Sidebar: choose graph subset
st.sidebar.title("Graph Subset Selection")
subset_option = st.sidebar.selectbox("Choose a subset of the graph:", [
    "Entire Graph",
    "Largest Strongly Connected Component",
    "Top 20 Nodes by Degree"
])

if subset_option == "Entire Graph":
    G_sub = G
elif subset_option == "Largest Strongly Connected Component":
    largest_scc = max(nx.strongly_connected_components(G), key=len)
    G_sub = G.subgraph(largest_scc).copy()
elif subset_option == "Top 20 Nodes by Degree":
    top_nodes = sorted(G.degree, key=lambda x: x[1], reverse=True)[:20]
    top_node_ids = [n for n, _ in top_nodes]
    G_sub = G.subgraph(top_node_ids).copy()

# Pyvis visualization
got_net = Network(height='800px', width='100%', directed=True, notebook=False)
got_net.barnes_hut()

for src, dst, data_edge in G_sub.edges(data=True):
    got_net.add_node(src, title=src)
    got_net.add_node(dst, title=dst)
    got_net.add_edge(src, dst, value=data_edge.get('weight', 1))

neighbor_map = got_net.get_adj_list()
for node in got_net.nodes:
    node["title"] += " Neighbors:<br>" + "<br>".join(neighbor_map[node["id"]])
    node["value"] = len(neighbor_map[node["id"]])

got_net.repulsion()
got_net.show_buttons(filter_=['physics'])
got_net.write_html("got_network.html")

# Display network
st.title("Game of Thrones Network Analysis")
st.subheader("1. Network Visualization")
components.html(open("got_network.html", "r", encoding="utf-8").read(), height=800, scrolling=True)

# 2. Structural Metrics
st.subheader("2. Structural Metrics")
density = nx.density(G)
st.markdown(f"**Network Density:** {density:.4f} — Ratio of actual edges to possible edges.")

assortativity = nx.degree_assortativity_coefficient(G)
st.markdown(f"**Assortativity:** {assortativity:.4f} — Indicates if nodes tend to connect to others with similar degree.")

clustering = nx.average_clustering(G.to_undirected())
st.markdown(f"**Global Clustering Coefficient:** {clustering:.4f} — Measures the tendency of nodes to cluster together.")

scc = list(nx.strongly_connected_components(G))
st.markdown(f"**Strongly Connected Components:** {len(scc)} — Groups where every node is reachable from any other. Applies to directed graphs.")

wcc = list(nx.weakly_connected_components(G))
st.markdown(f"**Weakly Connected Components:** {len(wcc)} — Groups where nodes are connected if direction is ignored.")

# 3. Degree Distributions
st.subheader("3. Degree Distributions")
degrees = [deg for _, deg in G.degree()]
in_degrees = [deg for _, deg in G.in_degree()]
out_degrees = [deg for _, deg in G.out_degree()]

fig, ax = plt.subplots(1, 3, figsize=(18, 5))
sns.histplot(degrees, bins=20, ax=ax[0], kde=False, color='blue')
ax[0].set_title("Total Degree Distribution")

sns.histplot(in_degrees, bins=20, ax=ax[1], kde=False, color='green')
ax[1].set_title("In-Degree Distribution")

sns.histplot(out_degrees, bins=20, ax=ax[2], kde=False, color='red')
ax[2].set_title("Out-Degree Distribution")

st.pyplot(fig)

# 4. Node Centrality Measures
st.subheader("4. Node Centrality Measures")
top_k = st.slider("Select top-k nodes to display:", min_value=5, max_value=30, value=10)

# Compute eigenvector centrality only on largest SCC
largest_scc = max(nx.strongly_connected_components(G), key=len)
G_scc = G.subgraph(largest_scc).copy()

if len(G_scc) > 2:
    try:
        eigen_centrality = nx.eigenvector_centrality_numpy(G_scc)
    except Exception:
        # fallback to power iteration
        eigen_centrality = nx.eigenvector_centrality(G_scc, max_iter=1000)
else:
    eigen_centrality = {}
    st.warning("Largest strongly connected component too small to compute eigenvector centrality.")


st.markdown("**Note:** Eigenvector centrality is computed only on the largest strongly connected component.")

centralities = {
    "Eigenvector Centrality": eigen_centrality,
    "Degree Centrality": nx.degree_centrality(G),
    "Closeness Centrality": nx.closeness_centrality(G),
    "Betweenness Centrality": nx.betweenness_centrality(G)
}

for name, values in centralities.items():
    st.markdown(f"### {name}")
    top_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)[:top_k]
    df = pd.DataFrame(top_nodes, columns=["Node", "Centrality"])
    st.dataframe(df)
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x="Centrality", y="Node", data=df, palette="viridis", ax=ax)
    ax.set_title(f"Top {top_k} Nodes by {name}")
    st.pyplot(fig)
