from PyQt6.QtCore import QObject, pyqtSlot, QUrl ,Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView 
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QApplication
import sys, os
import uuid
from pathlib import Path
from llm.llm import generate_article,generate_lecture ,generate_mindmap ,generate_flashcards
from llm.llm_helper import create_audio ,create_mindmap
from filemanager import create_note , link_notes ,save_meta, metadata, load_meta ,Assetlocation
from datetime import datetime
from pathlib import Path

# import debugpy
app = QApplication(sys.argv)
# debugpy.debug_this_thread() 
view = QWebEngineView()
channel = QWebChannel()
DB_PATH = "database/notes.db"
NOTES_DIR = "Knowbases/base1"
class Backend(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(str,str)
    def save_content(self, pageName:str,content):
        """Called from JS (Ctrl+S). Always return a value."""
        pageLocation = Path(NOTES_DIR) / pageName / f"{pageName}.html"
        with open(pageLocation, "w", encoding="utf-8") as f:
            f.write(content)
        new_meta =load_meta(note_id=pageName)
        save_meta(new_meta.id,meta=new_meta)
        

    @pyqtSlot(str,str,str, str,result= str)
    def createpage(self,selection,content,parent_id,level = "grade 11") :
        """Create a new empty page file and return its safe filename."""
        note_id =uuid.uuid4().hex
        filename = f"{note_id}.html"
        path = os.path.abspath(NOTES_DIR)
        # article = generate_article(selection,content, level)
        create_note(str(note_id),selection,str(parent_id))
        link_notes(parent_id,note_id)
        pageLocation = Path(NOTES_DIR) / note_id / filename
        with open(pageLocation, "w", encoding="utf-8") as l:
            l.write('dsfknasdj sdfjndsj fsdjfnsdjn')
        return note_id
    
    @pyqtSlot(str,str,result=str)
    def create_lecture(self,article,noteID):
        lecture = generate_lecture(article, "grade 11")
        lecture_filelocation = create_audio(lecture,noteID )
        new_meta =load_meta(note_id=noteID)
        new_meta.assets_location.lecture_location =lecture_filelocation
        save_meta(noteID,meta=new_meta)
        return lecture_filelocation
    
    @pyqtSlot(str,str,result=str)
    def create_mindmap(self,article,noteID):
        nodes,edges =generate_mindmap(article)
        mindmap_filelocation = create_mindmap(nodes=nodes,edges=edges,noteID=noteID)
        new_meta =load_meta(note_id=noteID)
        new_meta.assets_location.mindmap_location =mindmap_filelocation
        save_meta(noteID,meta=new_meta)
        return mindmap_filelocation
    
    @pyqtSlot(str,int,str,result=str)
    def create_flashcards(self,article,NOflashcards,noteID):
        flashcards = generate_flashcards(article=article, NOFlashcards=NOflashcards)
        json_str = flashcards.model_dump_json()
        flashcard_location = f"{NOTES_DIR}/{noteID}/assets/{uuid.uuid4().hex}.json"
        new_meta =load_meta(note_id=noteID)
        new_meta.assets_location.flashcards_location =flashcard_location
        save_meta(noteID,meta=new_meta)
        with open(flashcard_location, "w", encoding="utf-8") as f:
            f.write(json_str)  
        return  flashcard_location
    

    @pyqtSlot(str, result=str)
    def print(self, problem):
        print(problem)



backend = Backend()
channel.registerObject("backend", backend)
view.page().setWebChannel(channel)

file_path = os.path.abspath("web/index1.html")
view.load(QUrl.fromLocalFile(file_path))
view.showMaximized()   

view.show()

sys.exit(app.exec())