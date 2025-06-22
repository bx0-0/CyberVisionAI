import streamlit as st
import random
import time
from utils import process_file
from templates import generate_html_RAG_start_template
def setup_ui():
    
    list_of_icon = ['smart_toy:', 'precision_manufacturing:', 'robot_2:', 'robot:']
    index = random.randint(0, 3)
    st.set_page_config(page_title='X', page_icon=f':material/{list_of_icon[index]}')

    st.markdown(""" 
        <style>
        body { padding-top: 2px; }
        .stSelectbox { position: fixed; top: 9.6%; left: 0.2%; width: 150px !important; font-size: 17px; z-index: 100; }
        .stSelectbox option { font-size: 13px; }
        .stDeployButton { visibility: hidden; }
        @keyframes shine { 0% { background-position: -200%; } 100% { background-position: 200%; } }
        .animated-gradient { 
            display: inline-block; 
            font-size: 2.2em;  
            font-weight: bold; 
            color: 
            background: linear-gradient(90deg, 
            background-size: 200% 200%; 
            -webkit-background-clip: text; 
            background-clip: text; 
            color: transparent; 
            animation: shine 8s linear infinite; 
        }
        .center-content { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            overflow: hidden;  
            width: 100%;  
            white-space: nowrap;  
        }
        
        
        
                
        .stFileUploader div small{
        display: none;
        }
        
    .st-emotion-cache-1wbqy5l.e17vllj40{ display: none; }
  .custom-button {
            background-color: 
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
            width: 100%;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .custom-button:hover {
            background-color: 
            transform: scale(1.05);
        }
         .sidebar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: 
            padding: 10px;
            z-index: 1000;
        }
        .st-emotion-cache-ysg2um ereal7m6{ display: none; }
                

        </style>

    """, unsafe_allow_html=True)

    welcome_text = "🌟 Start Your Journey Here!"

    if 'welcome_message_displayed' not in st.session_state:
        st.session_state.welcome_message_displayed = False

    placeholder = st.empty()

    if not st.session_state.welcome_message_displayed:
        typed_text = ""
        for i in range(len(welcome_text) + 1):
            typed_text = welcome_text[:i]
            placeholder.markdown(f"<div class='center-content animated-gradient'>{typed_text}</div>", unsafe_allow_html=True)
            time.sleep(0.05)  

        placeholder.markdown(f"<div class='center-content animated-gradient'>{welcome_text}</div>", unsafe_allow_html=True)

        st.session_state.welcome_message_displayed = True
    else:
        st.markdown(f"<div class='center-content animated-gradient'>{welcome_text}</div>", unsafe_allow_html=True)

def display_messages(messages):
    if  messages:
        last_message = messages[-1] 
    last_message = None 
    for message in messages:
        with st.chat_message(message["role"], avatar=message.get("avatar", "")):
            st.markdown(message["content"])
        


def check_conflict(checkboxes):
    if checkboxes[0] and checkboxes[4] and sum(checkboxes) == 2:
        return False

    return sum(checkboxes) > 1

def start_new_recording():
    st.session_state.start_new_recording = True

def create_sidebar():
    st.sidebar.title('⭐Features')

    
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader('Active Modes')
    deep_thinking_mode = st.sidebar.toggle('Deep Thinking Mode')
    st.session_state.deep_thinking = deep_thinking_mode
    RAG_system = st.sidebar.toggle('RAG System')
    st.session_state.RAG = RAG_system
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader('One-Time Actions')

    
    if 'upload_files' not in st.session_state:
        st.session_state.upload_files = False
    if 'use_internet_text' not in st.session_state:
        st.session_state.use_internet_text = False
    if 'warning_displayed' not in st.session_state:
        st.session_state.warning_displayed = False
    if 'use_Vision' not in st.session_state:
        st.session_state.use_Vision = False
    if 'use_external_ais' not in st.session_state:
        st.session_state.use_external_ais = False
    if 'create_mind_map' not in st.session_state:
        st.session_state.create_mind_map = False
    if 'record_audio' not in st.session_state:
        st.session_state.record_audio = False
    if 'start_new_recording' not in st.session_state:
        st.session_state.start_new_recording = False
        
    
    upload_files = st.sidebar.checkbox('Enable file upload', value=False, help='X allows you to upload files for processing or extracting information directly from the provided documents.')
    use_external_ais = st.sidebar.checkbox('Enable external AI verification', value=False, help='X can query external AIs (e.g., GPT-4o-mini, Claude-3-Haiku, LLaMA-3.1-70B, Mixtral-8x7B) to verify and validate answers by cross-referencing multiple models for more reliable responses.')

    
    use_internet_text = st.sidebar.checkbox(
        'Enable internet access for text',
        value=False,
        help='Allow X to search the internet for text-based content. Note: This option is limited to text search, not for code.'
    )

    create_mindmap = st.sidebar.checkbox(
        'Create Mind Map',
        value=False,
        help='X can create mindmaps for you just tell him the name of the mindmap you want to create and he will create it for you.'
    )
    use_Vision = st.sidebar.checkbox('Enable Vision mode', value=False)
    record_audio = st.sidebar.checkbox('Record Audio', value=False, help='You can  record audio for your conversation with X.')
    


    st.session_state.convert_last_message_to_audio = st.sidebar.button(
        "🔊 Convert Last Message to Audio",
        help='Convert the last message from the assistant to an audio file.',
        key="convert_audio_button"
    )

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader('Settings')


    st.session_state.save = st.sidebar.button(
        "Save Conversion",
        icon=":material/mood:",
        help='You can\'t send any message here again if you save, so you must start a new chat',
        use_container_width=True
    )
    
    if 'speaker' not in st.session_state:
        st.session_state.speaker = 0
    speaker = st.sidebar.pills('Select Speaker', ['default','Bella', 'Sarah', 'Adam', 'Michael', 'Emma', 'Isabella', 'George', 'Lewis', 'Nicole', 'Sky'],default='default', key="speaker_radio")
    st.session_state.speaker = ['default','Bella', 'Sarah', 'Adam', 'Michael', 'Emma', 'Isabella', 'George', 'Lewis', 'Nicole', 'Sky'].index(speaker)

    st.session_state.RAG_result_number = st.sidebar.slider(
        'Select RAG Result Number',
        5,
        10,
        value = 5 ,
        key="RAG_result_number_slider",
        help='Each number auction increases the accuracy of the answer, but the model slows down during the answer',
        disabled=True if st.session_state.deep_thinking else False,
    )
    if st.session_state.deep_thinking:
        st.session_state.RAG_result_number = 5

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    active_checks = [upload_files, use_internet_text, use_Vision, use_external_ais, create_mindmap, record_audio, st.session_state.save,st.session_state.RAG]

    
    if check_conflict(active_checks):
        
        st.session_state.upload_files = False
        st.session_state.use_internet_text = False
        st.session_state.use_Vision = False
        st.session_state.use_external_ais = False
        st.session_state.warning_displayed = True
        st.session_state.create_mindmap = False
        st.session_state.record_audio = False
        st.session_state.RAG = False
        st.warning("Only one 'One-Time Actions' option can be enabled at a time")
    else:
        
        st.session_state.upload_files = upload_files
        st.session_state.use_internet_text = use_internet_text
        st.session_state.use_Vision = use_Vision
        st.session_state.use_external_ais = use_external_ais
        st.session_state.create_mindmap = create_mindmap
        st.session_state.record_audio = record_audio
        st.session_state.RAG = RAG_system
        st.session_state.warning_displayed = False

    
    if st.session_state.upload_files and not st.session_state.save_success_conversation:
        uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'txt', 'docx', 'doc'], key="file_uploader")
        file_content = None
        if uploaded_file is not None:
            with st.spinner('summarize your file...'):
                file_content = process_file(uploaded_file)

            if 'Error: File size' in file_content:
                st.error(file_content)
            else:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                return st.session_state.upload_files,False, file_content, uploaded_file.name
            
    elif st.session_state.record_audio and not st.session_state.save_success_conversation:
        print('inside ui')
        audio_file = st.audio_input("Record your audio...", key="audio_recorder",on_change=start_new_recording)
        if audio_file and st.session_state.start_new_recording:
            audio_content = audio_file.read()
            return False, True, audio_content, "audio_recorder"
        else:
            return False,False, None, None
        
    elif st.session_state.use_Vision and not st.session_state.save_success_conversation:
        upload_image = st.file_uploader("Upload an image", type=['png', 'jpg', 'jpeg'], key="image_uploader")  

    elif st.session_state.RAG:
        with st.expander("💡 Learn About RAG..?"):
            st.markdown(generate_html_RAG_start_template())

    return False, False, None, None

def get_user_input():
    
    if st.session_state.save_success_conversation:
        user_input = st.chat_input("Say something...", disabled=True)
        st.info('You can\'t send any message here again if you save, so you must start a new chat', icon=":material/info:")
        return None
    elif st.session_state.warning_displayed:
        user_input = st.chat_input("Say something...", disabled=True)
        st.info('You can\'t send any message only one function can  be selected', icon=":material/info:")
        return None
    else:
        user_input = st.chat_input("Say something...")

    
    return user_input

if __name__ == "__main__":
    setup_ui()
