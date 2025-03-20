import streamlit as st
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.tools import DuckDuckGoSearchResults #searching tools
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import  HumanMessage
load_dotenv()

# Add detailed API key verification
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4-turbo")

class JobSearch:
    def __init__(self, prompt):
        # Initialize the chat model, prompt template, and search tool for job search assistance
        self.model = llm
        self.prompt = prompt
        self.tools = [DuckDuckGoSearchResults()]  # Search tool to find job listings or related information
        # Create an agent executor with tool access, enabling verbose output and error handling
        self.agent = create_tool_calling_agent(self.model, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True, handle_parsing_errors=True)

    def find_jobs(self, user_input):
        response = self.agent_executor.invoke({"input": user_input, "job_chat_history": st.session_state.job_chat_history})
        st.session_state.job_chat_history.extend([HumanMessage(content=user_input), response["output"]])
        changed_response = str(response.get('output')).replace("```markdown", "").strip()
        return changed_response

def job_search(query):
    """Provide a job search response based on user query requirements."""
    # prompt = ChatPromptTemplate.from_template('''Your task is to refactor and make .md file for the this content which includes
    # the jobs available in the market. Refactor such that user can refer easily. Content: {result}''')
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", '''You task is to search jobs available based on the users query.
                                              Ensure that the final job search result is in the md format'''),
        MessagesPlaceholder("job_chat_history"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    jobSearch = JobSearch(prompt)
    #state["query"] = input('Please make sure to mention Job location you want,Job roles\n')
    response = jobSearch.find_jobs(query)
    return response
    return {"response": response}
    


st.title("Job Search Assistant")


if "job_messages" not in st.session_state:
    st.session_state.job_messages = []
    
if "job_chat_history" not in st.session_state:
    st.session_state.job_chat_history = []


for job_messages in st.session_state.job_messages:
    with st.chat_message(job_messages["role"]):
        st.markdown(job_messages["content"])
        


if user_query := st.chat_input("Enter question for Generative AI career assistant"):
    st.session_state.job_messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    response = job_search(user_query)
    st.session_state.job_messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)  
