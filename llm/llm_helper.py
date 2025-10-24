import os
from pathlib import Path
import uuid
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network

NOTES_DIR = "Knowbases/base1"
def create_mindmap(nodes , edges,noteID:str) -> str:
    nodes = nodes
    edges = edges
    G = nx.DiGraph() 
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # Build a NetworkX graph
    net = Network(notebook=True, height="750px", width="100%", directed=True,cdn_resources="in_line")
    net.from_nx(G)
    net.force_atlas_2based()
    filelocation = f"{NOTES_DIR}/{noteID}/assets/{uuid.uuid4().hex}.html"
    html = net.generate_html(filelocation,notebook=False,local=True)
    with open(filelocation, "w", encoding="utf-8") as f:
        f.write(html)
    return filelocation


def create_diagram( nodes, edges) -> str:
    from graphviz import Digraph
    dot = Digraph(comment="Simple Flowchart")

    for e in edges:
      dot.edge(e[0],e[1])
    for e in nodes:
      dot.node(e,e)
    dot.render('flowchart', format='png', cleanup=True)


def create_audio(text,noteID) ->str:
    from gtts import gTTS
    from shutil import rmtree
    os.makedirs("llm/temp" ,exist_ok=True)
    chunks = text.split(".")  # simple split by sentences

    i = 1
    for chunk in chunks:
        if chunk.strip():  # skip empty
            tts = gTTS(text=chunk, lang="en")
            filename = f"llm/temp/part{i}.mp3"
            tts.save(filename)
            print(f"Saved {filename}")
            i += 1

    # # You can then merge these MP3s using pydub
    from pydub import AudioSegment

    combined = AudioSegment.empty()
    for j in range(1, len(chunks)):
        path = f"llm/temp/part{j}.mp3"
        combined += AudioSegment.from_mp3(path)
    unique_id = uuid.uuid4()
    location =  f"{NOTES_DIR}/{noteID}/assets/{unique_id}.mp3"

    combined.export(location, format="mp3")
    rmtree(f"llm/temp/")
    return location


