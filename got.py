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

# Create pyvis network
got_net = net.Network(height='800px', width='100%', heading='', notebook=False, cdn_resources='remote')
got_net.barnes_hut()

# Add edges
for src, dst, w in zip(got_data['Source'], got_data['Target'], got_data['Weight']):
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
with open("gameofthrones.html", "r", encoding="utf-8") as f:
    html_string = f.read()

st.title("Game of Thrones Network")
components.html(html_string, height=800, scrolling=True)
