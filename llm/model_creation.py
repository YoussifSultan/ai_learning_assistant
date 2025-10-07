import os
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import SystemMessagePromptTemplate,HumanMessagePromptTemplate

from langchain_core.prompts import ChatPromptTemplate
os.environ["DEEPSEEK_API_KEY"] = "sk-df6670570e7a40c29b1cd0f335e874b6"

reasoner_model = ChatDeepSeek(model= "deepseek-reasoner",temperature=0.3)


def create_prompt(system_prompt,user_prompt, input_variables) :
    system_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
    user_prompt =HumanMessagePromptTemplate.from_template(
        user_prompt,
        input_variables=input_variables,
    )
    prompt = ChatPromptTemplate.from_messages([system_prompt,user_prompt])

    return prompt


from pydantic import Field, BaseModel
from langchain.prompts import ChatPromptTemplate
class Mindmap(BaseModel):
  nodes : list[str] = Field(description="List of nodes")
  edges : list[list[str,str]] = Field(description="List of edges")

mindmap_model = reasoner_model.with_structured_output(Mindmap)

