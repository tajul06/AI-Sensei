from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from config.settings import GOOGLE_API_KEY
from config.models import GEMINI_MODEL
from config.prompts import get_prompt_for_subject
from config.subjects import group_for_subject




def get_llm_chain(subject:str , retriever) :
    group = group_for_subject(subject)
    llm=ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GOOGLE_API_KEY,
        max_output_tokens=1024,
        
    )
    subject_prompt = get_prompt_for_subject(subject, group)
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template=subject_prompt + """

        Study Material:
        {context}
        Student's Question:
        {question}
        
        Your answer (as the tutor — don't mention "the context" or "the material" by name):
        """
    )
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    chain = (
        {"context":retriever|format_docs, "question":RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )
    return chain