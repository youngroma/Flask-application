from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config.config import Config

openai_api_key = Config.OPENAI_API_KEY
llm = ChatOpenAI(openai_api_key=openai_api_key)

def generate_response(prompt_text):
    prompt_template = PromptTemplate(input_variables=["prompt"], template="{prompt}")
    chain = LLMChain(llm=llm, prompt=prompt_template)

    response = chain.run(prompt=prompt_text)
    tokens_used = len(response.split())
    return response, tokens_used