# Cyber Vision AI

<p align="center">
  <img src="./IMage_ghp/award.png" alt="Award" width="300"/>
</p>

A First-Place Award-Winning Graduation Project from the Faculty of Science, Zagazig University, Computer Science Department.

<p align="center">
  <img src="./IMage_ghp/x_logo.png" alt="X Model Logo" width="200"/>
</p>

<p align="center">
  <a href="https://github.com/bx0-0/CyberVisionAI"><img src="https://img.shields.io/github/stars/bx0-0/CyberVisionAI?style=social" alt="GitHub stars"></a>
  <a href="https://github.com/bx0-0/CyberVisionAI"><img src="https://img.shields.io/github/forks/bx0-0/CyberVisionAI?style=social" alt="GitHub forks"></a>
  <a href="https://github.com/bx0-0/CyberVisionAI/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
</p>

---

## Overview

Cyber Vision AI is an advanced, open-source AI-powered assistant designed specifically for the cybersecurity community. This project, which won first place in the university's scientific conference for the Mathematics Division, was developed to overcome the limitations of conventional AI tools that often restrict security-related queries.

Our platform provides an unrestricted yet ethically-safeguarded environment for tasks such as vulnerability analysis, exploit explanation, and proof-of-concept code generation.

- **Fine-tuning Dataset:** The model was fine-tuned on a specialized dataset available at [saberbx/X-mini-datasets](https://huggingface.co/datasets/saberbx/X-mini-datasets).
- **Core Model:** The primary model used is [saberbx/XO](https://huggingface.co/saberbx/XO).

---

## Core Features

- **Deep Thinking Mode:** Delivers nuanced, analytically rich responses for complex cybersecurity problems.
- **Retrieval-Augmented Generation (RAG):** Provides highly personalized answers by searching your private vector database.
- **Deep Search & Multi-Agent Framework:** Conducts comprehensive, multi-stage searches and compiles in-depth, structured reports.
- **Voice Interaction:** Features high-accuracy speech-to-text and text-to-speech capabilities.
- **MindMap Generation:** Dynamically visualizes complex topics and plans as interactive mind maps using [Markmap-CLI](https://markmap.js.org/).
- **Live Web Search & Multi-AI Support:** Augments answers with real-time web data and insights from multiple top-tier AI models.

---

## Prerequisites

Before you begin, ensure you have the following installed and configured:

- Python 3.12+ and pip.
- **[Ollama](https://ollama.com/):** Install from [ollama.com](https://ollama.com/).
- **[Markmap-CLI](https://www.npmjs.com/package/markmap-cli):** Required for MindMap generation. Install it globally:
  ```bash
  npm install -g markmap-cli
  ```

---

## Step-by-Step Installation and Setup Guide

### Step 1: Set Up the AI Model with Ollama

- **Create the Model in Ollama:** The project expects a model named `X`.
- A ready-to-use Modelfile is available on the model's [Hugging Face page](https://huggingface.co/saberbx/XO).
- Run the following command in a new terminal to create the model. Ollama will automatically download it.
  ```bash
  ollama create X -f /path/to/your/Modelfile
  ```
  *Note: Replace the path with the actual location of your Modelfile.*
- **Verify:** Confirm the model is installed by running:
  ```bash
  ollama list
  ```
  You should see `X` in the list.

### Step 2: Set Up the Project and Environment

- **Clone the Repository:**
  ```bash
  git clone https://github.com/bx0-0/CyberVisionAI.git
  cd CyberVisionAI
  ```
- **Create and Activate a Virtual Environment:**
  ```bash
  python -m venv venv
  # On Windows
  .\venv\Scripts\activate
  ```
  *Important: Ensure the virtual environment (venv) is activated in every new terminal you use for running project commands.*
- **Install Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

### Step 3: Configure the Frontend Environment

- **Create a .env file:** Inside the `chat/streamlit_stricture` directory, create a new file named `.env`.
- **Add a Secret Key:** Open the `.env` file and add the following line. This key is used to encrypt and secure the initial communication between the Django and Streamlit servers. You can use the provided key or generate your own secure key.
  ```env
  SECRET_KEY=121f9d63c642ddd73325274068f4196aacd110b5f9ff3f882ff537046e81698b
  ```

### Step 4: Set Up the Django Database

- **Database Migrations:**
  ```bash
  # (Ensure venv is activated)
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Create a Superuser:**
  ```bash
  python manage.py createsuperuser
  ```
  Follow the prompts to set up your admin credentials.

---

## How to Run the Application

To run Cyber Vision AI, you need to start several services in separate terminals.

### Core Services (Always Required)

- **Terminal 1: Start Ollama Server**
  ```bash
  ollama serve
  ```
- **Terminal 2: Start Django Backend Server**
  ```bash
  # (Ensure venv is activated)
  python manage.py runserver 8080
  ```
  The backend will now be running at http://localhost:8080.
- **Terminal 3: Start Streamlit Frontend**
  ```bash
  # (Ensure venv is activated)
  cd chat/streamlit_stricture
  streamlit run streamlit_chat.py --server.enableXsrfProtection false
  ```
  The frontend will now be running at http://localhost:8501.

### Optional Services (for RAG Feature)

If you wish to use the Retrieval-Augmented Generation (RAG) feature, you will need to run the following two servers in two additional terminals.

- **Terminal 4: Start Redis Server**
  (We recommend installing and running it via WSL):
  ```bash
  wsl
  redis-server
  ```
- **Terminal 5: Start Celery Worker**
  From the project's root directory:
  ```bash
  # (Ensure venv is activated)
  celery -A project worker --pool=solo --loglevel=info
  ```

---

## Accessing and Logging into the Application

- **Start with the Django Interface:**
  - Open your browser and navigate to http://localhost:8080.
  - Log in or create a new account.
- **Automatic Redirect:**
  - Upon successful login, the Django interface will automatically redirect you to the Streamlit application (http://localhost:8501).
  - Your authentication token will be passed securely in the background, ensuring you are logged in and ready to use the app without any manual steps.

---

## Configuration and Customization

- [`project/settings.py`](./project/settings.py): Main Django configuration. Here you can adjust the database, Redis broker URL for Celery, and other backend settings.
- [`chat/streamlit_stricture/streamlit_chat.py`](./chat/streamlit_stricture/streamlit_chat.py): Customize the Streamlit frontend, change the default Ollama model name, or adjust other UI/AI parameters.
- [`chat/streamlit_stricture/.env`](./chat/streamlit_stricture/.env): Stores the secret key for securing the initial server-to-server communication.

---

## A Note on the Audio (TTS) Feature

- The Text-to-Speech (TTS) feature in the current code was designed for an older version of the Kokoro model.
- The application will run perfectly without the TTS feature.
- If you wish to enable it, you will need to adapt the code in `tts.py` to work with the new version of the model.

---

## License

This project is licensed under the [MIT License](https://github.com/bx0-0/CyberVisionAI/blob/main/LICENSE).
