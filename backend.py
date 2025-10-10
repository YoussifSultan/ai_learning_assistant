from PyQt6.QtCore import QObject, pyqtSlot, QUrl ,Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView 
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QApplication
import sys, os
import uuid
from pathlib import Path
from llm.llm import generate_article,generate_lecture ,generate_mindmap ,generate_flashcards
from llm.llm_helper import create_audio ,create_mindmap
from filemanager import create_note , link_notes ,save_meta
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
    def save_content(self, pageLocation:str,content):
        """Called from JS (Ctrl+S). Always return a value."""
        pageLocation= pageLocation.replace("../","")
        with open(pageLocation, "w", encoding="utf-8") as f:
            f.write(content)
        # save_meta()
        

    @pyqtSlot(str,str,str, str,result= str)
    def createpage(self,selection,content,level = "grade 11",parent_id="root/root") :
        """Create a new empty page file and return its safe filename."""
        note_id =uuid.uuid4().hex
        path = Path(parent_id)
        print(list(path.parts))
        parent_id = list(path.parts)[-2]
        filename = f"{note_id}.html"
        path = os.path.abspath(NOTES_DIR)
        # article = generate_article(selection,content, level)
        create_note(str(note_id),selection,str(parent_id))
        link_notes(parent_id,note_id)
        path = os.path.join(path,note_id,filename)
        with open(path, "w", encoding="utf-8") as l:
            l.write('dsfknasdj sdfjndsj fsdjfnsdjn')
        return f"../{NOTES_DIR}/{note_id}/{filename}"
    
    @pyqtSlot(str,result=str)
    def create_lecture(self,article):
        lecture = generate_lecture(article, "grade 11")
        lecture_filelocation = create_audio(lecture)
        return lecture_filelocation
    
    @pyqtSlot(str,result=str)
    def create_mindmap(self,article):
        nodes,edges =generate_mindmap(article)
        mindmap_filelocation = create_mindmap(nodes=nodes,edges=edges)
        return mindmap_filelocation
    
    @pyqtSlot(str,int,result=str)
    def create_flashcards(self,article,NOflashcards):
        flashcards = generate_flashcards(article=article, NOFlashcards=NOflashcards)
        json_str = flashcards.model_dump_json()
        flashcard_location = f"assets/flashcards/{uuid.uuid4().hex}.json"
        with open(flashcard_location, "w", encoding="utf-8") as f:
            f.write(json_str)  
        return  flashcard_location
    

    @pyqtSlot(str, result=str)
    def print(self, problem):
        print(problem)



backend = Backend()
channel.registerObject("backend", backend)
view.page().setWebChannel(channel)

file_path = os.path.abspath("web/index.html")
view.load(QUrl.fromLocalFile(file_path))
view.showMaximized()   

view.show()

sys.exit(app.exec())