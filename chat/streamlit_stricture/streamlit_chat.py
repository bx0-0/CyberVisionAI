import time
import streamlit as st
import ollama

def get_assistant_response(question,file='',file_name='',is_file=False,search="",use_external_ais=False,external_ais_response="", model='x',context=None):
    sys="Dont answer the question directly and instead Before answering, analyze the task thoroughly using <thinking>. Outline each step in a structured approach, and verify each step's accuracy and application. Present your answer only after this careful process. Use Markdown formatting (headers, lists, code blocks) where appropriate to ensure clarity."
    q = f"'{question.strip()}'"

    if is_file and not st.session_state.create_mindmap and file_name != "" and file != "":
        q=f"""
            The user has uploaded a file. Your task is to read the content of the file and answer the user's question based on the file's content. Below are the details:
            - **File Name:** {file_name}
            - **User's Question:** {q}
            **File Content:**
                {file}
            Please analyze the file content carefully and provide a clear and concise answer to the user's question.

            """
    elif search != "" and st.session_state.use_internet_text:
        q = (
            "Your primary task is to search the internet and use the provided search results to answer the user's question accurately. "
            "Here are the details:\n"
            f"- **User's Question**: '{q}'\n"
            f"- **Search Results**: {search}\n\n"
            "### Your Role:\n"
            "1. Analyze the search results provided and use them to construct an accurate and concise answer to the question.\n"
            "2. If the search results are incomplete or unclear, rely on your general knowledge to provide a helpful response.\n"
            "3. Mention relevant links from the search results in your answer, where applicable, to support your response.\n"
            "4. Avoid copying text directly from the search results; instead, rephrase and integrate the information naturally.\n\n"
            "### Expected Output:\n"
            "A clear, well-structured response to the user's question, supported by insights from the search results or your own understanding."
        )


    elif use_external_ais and external_ais_response != "":
        q = (
        f"The user has asked a question: '{q}'. "
        "You have access to multiple external AI systems, including 'gpt-4o-mini', 'claude-3-haiku', 'llama-3.1-70b'."
        "Each of these AIs has provided their own insights or answers to the question. "
        "Your task is to review and learn from their responses, then provide the most reliable, accurate, and well-rounded answer based on this collective knowledge. "
        f"here are the external AI responses:{external_ais_response}"
         )
    elif st.session_state.create_mindmap and not is_file:
        q = (
            f"{q}."
            "Give an answer to the user's question quickly without much analysis"
            "your role is create small , simple mindmap for the user request"
            f"Remember to structure your content (mind map) using `###` for headers, `-` for list items, and `[ ]` for checkboxes where appropriate. "
            "dont forget to use <output> tag to output the mind map"
            )
    elif st.session_state.create_mindmap and is_file:
        q = (
            f"this is the user question:{q}."
            f"The user has uploaded a file file name: {file_name}"
            "your role is create small , simple mindmap for the file content"
            f"File content: {file}"
            f"Remember to structure your content (mind map) using `###` for headers, `-` for list items, and `[ ]` for checkboxes where appropriate. "
            "dont forget to use <output> tag to output the mind map"
            )

    messages = [{'role': 'user', 'content': q}]
    print(messages)
    
    if not st.session_state.RAG and (st.session_state.deep_thinking or is_file or search != ""  or st.session_state.create_mindmap or st.session_state.use_external_ais):
        messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
    elif st.session_state.deep_thinking and st.session_state.RAG:
        q = (
            f"The user has asked a question: '{q}'.\n\n"
            "Your task is to provide an accurate and well-rounded answer based on the information you have. "
            "Here are the rules you must follow:\n\n"
            "1. **Answer Naturally:** Provide your response as if you already know the information, without explicitly mentioning that you received context, data or information from the user.\n"
            "2. **Be Clear and Concise:** Your answer should be straightforward and easy to understand. Avoid unnecessary details or technical jargon unless it's relevant to the question.\n"
            "3. **Acknowledge Missing Information:** If you do not have enough information to answer the question accurately, inform the user politely. For example, say: 'I don't have enough information to answer this question. Could you provide more details?'\n"
            "Here is the information you have for this question:\n"
            f"{context}\n\n"
            )        
        messages = [{'role': 'user', 'content': f"system message: {sys}, user task is {q}"}]
        
    elif st.session_state.RAG and context and not st.session_state.deep_thinking:
        sys = f"""Answer the question by  using only the following context:"{context.strip()}.If there is no answer, tell the user that he is answering and provides you with more information in the question so that you can answer more accurately."""
        messages = [
        {'role': 'system', 'content': sys},
        {'role':"system",'content':"Remember to use the context to answer the question only and dont answer the question directly."},
        {'role': 'user', 'content': "dont repeat any  answer and dont forget to  use the context. user question:"+question},

        ]
        
    with st.spinner("analyzing"):
        print(messages)
        stream = ollama.chat(model=model, messages=messages, stream=True)
        time.sleep(2)
        print(stream)
    
        return stream
    

def stream_text(stream, delay=0.00000001):
    placeholder = st.empty()         # Main text placeholder
    thinking_placeholder = st.empty() # Persistent placeholder for Thinking
    output_placeholder = st.empty()   # Persistent placeholder for Answer
    text_accumulated = ""
    c = ''
    is_thinking_appeared = not (st.session_state.deep_thinking or st.session_state.create_mindmap or st.session_state.use_internet_text or st.session_state.use_external_ais or st.session_state.upload_files)
    print(is_thinking_appeared)

    for chunk in stream:
        if 'message' in chunk and 'content' in chunk['message']:
            text = chunk['message']['content']
            c += text

            # Display "Thinking..." HTML label only once
            if "<thinking>" in c and not is_thinking_appeared:
                thinking_placeholder.markdown(
                    "<strong style='color: #888;'>1-🧠 Thinking...</strong>",
                    unsafe_allow_html=True
                )
                placeholder = st.empty()      

                c = ''  # Reset after rendering HTML
                text = text.replace("<thinking>", " ")
                is_thinking_appeared = True

            # Display "Answer" HTML label only once
            elif "<output>" in c :
                output_placeholder.markdown("<strong style='color: #888;'>2-🧠 Answer...</strong>",unsafe_allow_html=True)
                text += '\n\n---------------------------------------------------------------------------------------------\n\n'
                c = ''  # Reset after rendering HTML


            if is_thinking_appeared:
                for char in text:
                    text_accumulated += char
                    placeholder.markdown(text_accumulated)  # Plain text rendering
    print(text_accumulated)

    return text_accumulated
