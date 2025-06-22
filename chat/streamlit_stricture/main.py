import streamlit as st
from auth import validate_token, generate_temporary_token_and_timestamp
from streamlit_chat import get_assistant_response, stream_text
from ui import setup_ui, display_messages, get_user_input, create_sidebar
from utils import internet_access, use_external_ais
from utils import (
    extract_mind_map_content,
    send_mindMap_to_dj,
    snow_animation,
    save_conversation,
    clear_text_after_convert_to_audio,
    extract_text_from_audio,
    get_RAG_content_from_DJ,
)
import tts



def main_ui():
    setup_ui()

    if "validated" not in st.session_state:
        st.session_state.validated = False

    if "api_key" not in st.session_state:
        st.session_state.api_key = None

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "save_success_conversation" not in st.session_state:
        st.session_state.save_success_conversation = False
    
    if "convert_last_message_to_audio" not in st.session_state:
        st.session_state.convert_last_message_to_audio = False

    if 'warning_displayed' not in  st.session_state:
        st.session_state.warning_displayed = False

    

    token = st.query_params.get("token", [None])
    if not token[0]:
        st.error("Token missing. Redirecting to login...")
        st.write(
            '<meta http-equiv="refresh" content="0; url=http://localhost:8000/accounts/login/">',
            unsafe_allow_html=True,
        )
        st.stop()

    token, timestamp, signature = generate_temporary_token_and_timestamp(token)

    if token and timestamp and not st.session_state.validated:
        result = validate_token(token, timestamp, signature)
        if result and result.get("success"):
            st.session_state.validated = True
            st.session_state.api_key = result.get("api")
            user_name = result.get("name")
            st.success(f"✨Welcome :{user_name} ")

    if st.session_state.validated:
        display_messages(st.session_state.messages)

        prompt = get_user_input()
        is_file_uploaded, is_record ,file_content, file_name = create_sidebar()

        if prompt and not st.session_state.save_success_conversation:
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            st.session_state.messages.append(
                {"role": "user", "content": prompt, "avatar": "👤"}
            )

            if (
                is_file_uploaded
                and not is_record
                and prompt
                and not st.session_state.create_mind_map
                and file_content
                and file_name
                and not st.session_state.RAG
            ):
                assistant_stream = get_assistant_response(
                    prompt, file=file_content, file_name=file_name, is_file=True
                )
            elif st.session_state.RAG:
                RAG_content = get_RAG_content_from_DJ(prompt)
                assistant_stream = get_assistant_response(question=prompt,context=RAG_content)
                
            elif prompt and st.session_state.use_internet_text:
                with st.spinner("searching..."):
                    search, current_datetime, links = internet_access(prompt)
                    with st.expander("Web Resources"):
                        st.write(links)
                    search = (
                        f"{search}, the current date and time  is: {current_datetime}"
                    )
                assistant_stream = get_assistant_response(
                    question=prompt, search=search
                )
            elif prompt and st.session_state.use_external_ais:
                with st.spinner("asking ais..."):
                    external_ais_response = use_external_ais(prompt)
                    with st.expander("Ai's Response."):
                        st.write(external_ais_response)
                assistant_stream = get_assistant_response(
                    prompt,
                    use_external_ais=True,
                    external_ais_response=external_ais_response,
                )
            elif (
                prompt
                and st.session_state.create_mindmap
                and is_file_uploaded
                and file_content
                and file_name
            ):
                assistant_stream = get_assistant_response(
                    prompt,
                    file=file_content,
                    file_name=file_name,
                    is_file=True,
                    search="",
                    use_external_ais=False,
                    external_ais_response="",
                )
                content = extract_mind_map_content(assistant_stream)
                send_mindMap_to_dj(content)
           
                

            else:
                assistant_stream = get_assistant_response(prompt)
            with st.chat_message(
                "assistant", avatar="C:\\Users\\User\\Downloads\\X.jpeg.png"
            ):
                content = stream_text(assistant_stream)
                print("content" + content)

                if st.session_state.create_mindmap:
                    content = extract_mind_map_content(content)
                    send_mindMap_to_dj(content)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": content,
                    "avatar": "C:\\Users\\User\\Downloads\\X.jpeg.png",
                }
            )

        elif (
                not prompt
                and not st.session_state.convert_last_message_to_audio
                and not is_file_uploaded
                and is_record
                and st.session_state.record_audio
                and not st.session_state.RAG
            ):
                
                if file_content and st.session_state.start_new_recording:
                    st.audio(file_content)
                    with st.spinner("processing the audio file..."):
                        text = extract_text_from_audio(file_content)
                    st.session_state.start_new_recording = False
                    if text:
                        with st.chat_message("user", avatar="👤"):
                            st.markdown(text)
                        st.session_state.messages.append(
                            {"role": "user", "content": text, "avatar": "👤"}
                        )
                        assistant_stream = get_assistant_response(text)
                        with st.chat_message(
                            "assistant", avatar="C:\\Users\\User\\Downloads\\X.jpeg.png"
                        ):
                            content = stream_text(assistant_stream)
                            print("content" + content)
                            
                            if st.session_state.create_mindmap:
                                content = extract_mind_map_content(content)
                                send_mindMap_to_dj(content)
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": content,
                                "avatar": "C:\\Users\\User\\Downloads\\X.jpeg.png",
                            }
                        )
                        
                    else:
                        st.error("The audio  file is empty...")

                else:
                    st.error("No audio content available to play.")
        if st.session_state.save and not st.session_state.convert_last_message_to_audio and not st.session_state.RAG:
            if not st.session_state.save_success_conversation:
                if st.session_state.messages:
                    snow_animation()
                    save_conversation()
                else:
                    st.info("You must type something to save", icon=":material/info:")
            else:
                st.success("Chat already saved , you can start new chat")
        

                    
        if st.session_state.convert_last_message_to_audio and st.session_state.messages and not st.session_state.save_success_conversation:
            last_message = clear_text_after_convert_to_audio(st.session_state.messages[-1]["content"])
            # Send the audio file to the user
            if last_message:
                with st.spinner("Converting the last message to an audio file..."):
                    print(last_message)
                    file = tts.text_to_speech(last_message,st.session_state.speaker)
                    st.markdown("""
                    <h6 style='color: blue;'>👾🔊:</h6>
                    """, unsafe_allow_html=True)
                    st.audio(file)
                    print(st.session_state.convert_last_message_to_audio)
                    st.session_state.convert_last_message_to_audio = False
            else:
                st.session_state.convert_last_message_to_audio = False
                st.info("You must start conversion to  convert  it  to audio..", icon=":material/info:")


if __name__ == "__main__":
    main_ui()