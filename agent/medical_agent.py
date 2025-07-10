import os
from dotenv import load_dotenv
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate

load_dotenv()

def get_medical_explainer():
    prompt = PromptTemplate(
        input_variables=["symptoms"],
        template="You are a helpful medical assistant. Explain these symptoms clearly with points: {symptoms}. Also provide some home remedies for these symptoms."
    )

    llm = ChatTogether(
        together_api_key=os.getenv("TOGETHER_API_KEY"),
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        temperature=0.7
    )

    chain = prompt | llm
    return chain


def get_symptom_validator():
    prompt = PromptTemplate(
        input_variables=["symptoms"],
        template="Are the following valid medical symptoms for a patient? \n {symptoms}. Respond only in single word 'yes' or 'no'"
    )

    llm = ChatTogether(
        together_api_key=os.getenv("TOGETHER_API_KEY"),
        model="mistralai/Mixtral-8x7B-Instruct-v0.1",
        temperature=0.0  # deterministic yes/no
    )

    return prompt | llm
