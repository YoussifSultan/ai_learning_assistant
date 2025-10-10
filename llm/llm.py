from llm.model_creation import reasoner_model, create_prompt, mindmap_model , flashcard_model
from pydantic import Field, BaseModel

def generate_article(word,context,education_level) ->str:
    generate_article_prompt = create_prompt(system_prompt="You are an AI Teacher which provides an in-detailed explanation of the scietific topic" ,
                  input_variables=["word" , "context" , "education_level"],
                  user_prompt="""
You are a scientific tutor.
    Provide a clear, precise, and detailed scientific explanation of the concept **"{word}"**.

    Context: "{context}"
    Target education level: "{education_level}"

    Guidelines:
    - Adapt the depth, terminology, and complexity of the explanation to match the specified education level
      (e.g., elementary school, high school, undergraduate, master’s, or PhD).
    - Ensure scientific accuracy and detail while keeping it understandable for that level.
    - Provide relevant examples, analogies, or mathematical details when appropriate.
    - If the word has multiple meanings, choose the one that best fits the context.
    -  **Inline Math**: Use `<math>` with `display="inline"` for inline expressions.
    - **Block Math**: Use `<math>` with `display="block"` for standalone equations.
    -**Use MathML tags**: such as `<mi>`, `<mn>`, `<mo>`, `<msup>`, `<msub>`, `<mfrac>`, `<msqrt>`, `<mroot>`, `<mfenced>`, `<mrow>` ,etc.
    - USE tables, codes, headings ,lists , links,  horizontal rule ,footnotes , paragraphs , etc.
    - Output: a part of html which would be put in <div>...</div> tag file 

""")
   
    generate_article_chain = (
     {
        "word" : lambda x:x["word"],
        "context" : lambda x: x["context"],
        "education_level" : lambda x:x["education_level"],
    }
    | generate_article_prompt
    | reasoner_model
    )
    article =  generate_article_chain.invoke({"word":word , "context":context , "education_level":education_level})
    return article.content

# Return file path of an HTML file
def generate_mindmap(article) ->tuple:
    mindmap_prompt= create_prompt(system_prompt="You are an AI assistant that creates mindmaps from scientific articles",
                  user_prompt="""
        Input:
        ---
        {article}
        ---

        Task:
        - Extract all entities/concepts as **nodes**.
        - Extract relationships as **edges**.
        """
        , input_variables=["article"])
    mindmap_chain =(
    {"article" : lambda x:x["article"]}
    | mindmap_prompt
    | mindmap_model
    | {
      "nodes" : lambda x:x.nodes,
      "edges" : lambda x:x.edges,
       })
    mindmap_data =mindmap_chain.invoke({"article":article})
    return mindmap_data["nodes"] , mindmap_data["edges"]

def generate_lecture(article, education_level):
    lecture_prompt = create_prompt(system_prompt="""You are an expert educator and lecturer.  
Your goal is to read a scientific article and explain it to students as if delivering a live lecture.  

Guidelines:
- Speak in a **lecture style**, like an instructor addressing a class.  
- Adapt complexity and vocabulary to the student’s education level:  
  • Beginner → simple language, analogies, step-by-step.  
  • Intermediate → moderate technical terms, clear structure, examples.  
  • Advanced → precise scientific language, detailed concepts, real-world applications.  
- Make the explanation **engaging and flowing**, not a dry summary.  
- Make sure to include commas and pauses to mimic natural speech.        
- Use transitions such as *“Now let’s move on to…”* or *“Think of it this way…”* to mimic natural speech.  
- If the article has equations or data, explain them clearly in plain words.  
- Output should be a **continuous transcript**, as if spoken, in plain text. """
 ,  user_prompt="""
Article:
{article}

Student Education Level: {education_level}"""
, input_variables=["article","education_level"])
    lecture_chain =(
    {
        "article" : lambda x:x["article"],
        "education_level" : lambda x:x["education_level"],
     }
    | lecture_prompt
    | reasoner_model)
    lecture = lecture_chain.invoke({
    "article" :article,
    "education_level" : education_level,
}).content
    return lecture

def generate_flashcards(article , NOFlashcards):
    flashcard_prompt = create_prompt(system_prompt="""
    You are an expert AI tutor that generates flashcards from scientific articles.

- Create a list of flashcards that helps a student understand this article.
each flashcard should be in the following format:
{{
  "front": "Front of the flashcard (the question or prompt)",
  "back": "Back of the flashcard (the correct answer or explanation)",
  "hint": "A small clue to help recall",
  "type": "One of: Definition | Concept | Example | Multiple-choice | Fill-in-the-blank | True/False | Application",
  "difficulty": "Integer from 1 (easy) to 5 (very hard)"
}}
    Guidelines:
- Use clear and precise scientific language.
- Vary the **type** of flashcards
- Adapt difficulty based on the complexity of the concept (basic terms = 1–2, abstract theories = 4–5).
- Make sure flashcards are concise but accurate.
- Avoid repeating the same style of question.
""",
user_prompt="""
---
{article}

---
Number of flashcards : {numberOfFlashcards}

""" ,input_variables=["article","numberOfFlashcards"])
    flashcards_chain =(
    {"article" : lambda x:x["article"],
     "numberOfFlashcards" : lambda x:x["numberOfFlashcards"]}
    | flashcard_prompt
    | flashcard_model

)
    return flashcards_chain.invoke({"article" : article , "numberOfFlashcards" : NOFlashcards})
    
