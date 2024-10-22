import streamlit as st
from openai import OpenAI
import openai
import json

# Function to read content from a file in the source code
def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")
        return None

# Function to get the initial prompt for classifying the error
def get_classify_error_prompt():
    return read_file('prompts/classify_error_prompt.txt')

# Function to get the initial prompt for classifying the error
def get_prepare_ticket_for_error_prompt():
    return read_file('prompts/create_ticket_prompt.txt')

# Function to get the error details
def get_data_error_details():
    return read_file('error_samples/demo_error_1.txt')

# Function to make a query to LLM
def ask_llm(messages): 
    return client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )

# Function to fetch LLM response message content
def get_llm_message_response_content(response):
    return response.choices[0].message.content

# LLM action Function to handle additional context retrieval
def retrieve_additional_context_action(initial_messages, initial_response):
    ### TODO 1: Viacheslav: just stub, this should gather context datafactory version, configuration, all source code class names and pathes
    ### arguments of the application(path to the config file, config file itself should also be loaded) + main class path
    ### ask_llm + handle_llm_response(llm_response)
    additional_question = st.text_input("Please provide more context or clarify your question:", key=initial_messages[0])
    if additional_question:
        updated_prompt = f"{initial_messages[0]}\n\n---\n\n{additional_question}"
        updated_messages = [{"role": "user", "content": updated_prompt}]
        # debug: st.write(f"udpdated prompt{updated_messages}")
        updated_response = ask_llm([{"role": "user", "content": updated_prompt}])
        updated_result = get_llm_message_response_content(updated_response)
        st.write(updated_result)
        handle_llm_response(updated_messages, updated_result)

def rise_incident_action(initial_messages, initial_prompt):
### TODO 2: Uladzimir: Action to create jira ticket(LLM should provide us a text that needs to be used in jira ticket, title, text, priority, story points etc.)
    prompt = get_prepare_ticket_for_error_prompt()
    error_contents = get_data_error_details()

    if error_contents and prompt:
        messages = [
            {"role": "user", "content": f"{error_contents} \n\n---\n\n {prompt}"}
        ]
        response = ask_llm(messages)

        result = get_llm_message_response_content(response)
        st.write(result)

### TODO 3: Viacheslav: fix json parsing for git diff issues in LLM response
### TODO 4: Uladzimir: action for the user interaction when LLM provided git diff, we should request user review and approval or rejection
### TODO 5: Stanislau: find configuration parser code

# Function to handle the response from the language model
def handle_llm_response(initial_messages, llm_response):
    try:
        parsed_result = json.loads(llm_response)
        issue_level = parsed_result.get("issueLevel")
        st.write(f"Issue level detected is {issue_level}")
        suggested_action = parsed_result.get("suggestedAction")

        # Define supported action handlers
        action_handlers = {
            "request_additional_context": lambda: retrieve_additional_context_action(initial_messages, llm_response),
            "rise_an_incident": lambda: rise_incident_action(initial_messages, llm_response),
            # Add more actions here
        }

        # Execute the appropriate action based on the suggested action
        handler = action_handlers.get(suggested_action, lambda: st.error(f"The action {suggested_action} is not yet registered."))
        handler()
    except json.JSONDecodeError:
        st.error(f"Failed to parse the response as JSON: {llm_response}")

### Main application

st.title("📄 Data Pipeline Assistant")

# Request the OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client
    #client = OpenAI(api_key=openai_api_key)
    client = openai.AzureOpenAI(api_key=openai_api_key, api_version="2024-08-01-preview", azure_endpoint=st.secrets.aoai.endpoint_full)
    prompt = get_classify_error_prompt()
    error_contents = get_data_error_details()

    if error_contents and prompt:
        messages = [
            {"role": "user", "content": f"{prompt} \n\n---\n\n {error_contents}"}
        ]
        response = ask_llm(messages)

        result = get_llm_message_response_content(response)
        st.write(result)
        handle_llm_response(messages, result)


### Examples for future use:
   # Let the user upload a file via `st.file_uploader`.
    # uploaded_file = st.file_uploader(
    #     "Upload a document (.txt or .md)", type=("txt", "md")
    # )

    # # Ask the user for a question via `st.text_area`.
    # question = st.text_area(
    #     "Now ask a question about the document!",
    #     placeholder="Can you give me a short summary?",
    #     disabled=not uploaded_file,
    # )