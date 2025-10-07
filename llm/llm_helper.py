import os
import uuid

def create_mindmap(nodes , edges) -> str:
    import networkx as nx
    import matplotlib.pyplot as plt

    nodes = nodes
    edges = edges
    G = nx.DiGraph() 
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    # Build a NetworkX graph
    from pyvis.network import Network
    net = Network(notebook=True, height="750px", width="100%", directed=True,cdn_resources="in_line")
    net.from_nx(G)
    net.force_atlas_2based()
    # Save & show
    net.show("biology_mindmap.html")


def create_diagram( nodes, edges) -> str:
    from graphviz import Digraph
    dot = Digraph(comment="Simple Flowchart")

    for e in edges:
      dot.edge(e[0],e[1])
    for e in nodes:
      dot.node(e,e)
    dot.render('flowchart', format='png', cleanup=True)


def create_audio(text) ->str:
    from gtts import gTTS
    from shutil import rmtree
    os.makedirs("assets/audio/temp")
    chunks = text.split(".")  # simple split by sentences

    i = 1
    for chunk in chunks:
        if chunk.strip():  # skip empty
            tts = gTTS(text=chunk, lang="en")
            filename = f"assets/audio/temp/part{i}.mp3"
            tts.save(filename)
            print(f"Saved {filename}")
            i += 1

    # # You can then merge these MP3s using pydub
    from pydub import AudioSegment

    combined = AudioSegment.empty()
    for j in range(1, len(chunks)):
        path = f"assets/audio/temp/part{j}.mp3"
        combined += AudioSegment.from_mp3(path)
    unique_id = uuid.uuid4()
    location =  f"assets/audio/{unique_id}.mp3"

    combined.export(location, format="mp3")
    # rmtree("assets/audio/temp")
    return location


