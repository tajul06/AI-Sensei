from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

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
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt_template},
        return_source_documents=True,
    )