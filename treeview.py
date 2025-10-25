import json
import os
import pprint
from filemanager import load_meta, metadata,Assetlocation 
import filemanager
def build_tree(notes_dict):
        tree = {}
        for note_id, note in notes_dict.items():
            note["children"] =[]
        
        # Build the hierarchy
        for note_id, note in notes_dict.items():
            parent_id = note["parent_id"]
            if parent_id != note_id and parent_id in notes_dict:
                parent = notes_dict[parent_id]
                
                parent["children"].append(note)
            else:
                # Root node
                tree[note_id] = note
        return tree
def generate_treeviewJson():
    notes_dict = {}

    for note_dir in os.listdir(filemanager.NOTES_DIR):
        metadata_path = os.path.join(filemanager.NOTES_DIR, note_dir, "meta.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                note = json.load(f)
                notes_dict[note["id"]] = note
    tree = build_tree(notes_dict)
    return json.dumps(tree, indent=2)


