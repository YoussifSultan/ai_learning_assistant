from PyQt6.QtCore import QObject, pyqtSlot, QUrl ,Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView 
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWidgets import QApplication
import sys, os
import uuid
from llm.llm import generate_article,generate_lecture ,generate_mindmap ,generate_flashcards
from llm.llm_helper import create_audio ,create_mindmap


app = QApplication(sys.argv)

view = QWebEngineView()
channel = QWebChannel()

class Backend(QObject):
    def __init__(self):
        super().__init__()

    @pyqtSlot(str,str)
    def save_content(self, pageName,content):
        """Called from JS (Ctrl+S). Always return a value."""
        with open(f"pages/{pageName}", "w", encoding="utf-8") as f:
            f.write(content)
        

    @pyqtSlot(str,str,str, result= str)
    def createpage(self,selection,content,level = "grade 11") :
        """Create a new empty page file and return its safe filename."""
        filename = f"{uuid.uuid4().hex}.html"
        path = os.path.abspath(f"pages/{filename}")
        print(selection,content, level)
        article = generate_article(selection,content, level)
        # create an empty HTML file (or use a template)
        with open(path, "w", encoding="utf-8") as l:
     
            l.write(f'{article}')
        # Return a JSON-serializable object (pywebview will convert)
        return filename
    
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
        # flashcards = generate_flashcards(article=article, NOFlashcards=NOflashcards)
        # json_str = flashcards.model_dump_json()
        # flashcard_location = f"assets/flashcards/{uuid.uuid4()}.json"
        # with open(flashcard_location, "w", encoding="utf-8") as f:
        #     f.write(json_str)  
        return  "assets/flashcards/6f5c2db4-2f7a-403c-9ce6-72a10c62c243.json"
    

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