import streamlit as st
import PyPDF2
from io import BytesIO
import requests
import json


# AI Integration Function
def get_ai_response(question, pdf_text):
    """Get response from local Llama 3 model via Ollama API"""
    try:
        # Prepare the prompt with document context
        prompt = f"""Based on this document content, answer the question accurately:

Document Content:
{pdf_text[:3000]}

Question: {question}

Please provide a clear, helpful answer based on the document content."""

        # Call local Ollama API
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama3',
                'prompt': prompt,
                'stream': False
            },
            timeout=500
        )

        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            return "Sorry, I couldn't process your question. Please try again."


    except requests.exceptions.ConnectionError:

        return "⚠️ Please start Ollama by running 'ollama serve' in Command Prompt first."

    except requests.exceptions.Timeout:  # ADD THIS LINE

        return "⚠️ The AI is taking longer than expected. Try a shorter question or restart Ollama."  # ADD THIS LINE

    except Exception as e:

        return f"Error: {str(e)}"


# Page config
st.set_page_config(page_title="LastMinute Padhai", page_icon="📚", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Sidebar styling with gradient and glass effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
        backdrop-filter: blur(15px);
        border-right: 2px solid rgba(255, 255, 255, 0.2);
    }

    /* Sidebar content styling */
    [data-testid="stSidebar"] .css-1d391kg {
        background: transparent;
    }

    /* Sidebar text styling */
    [data-testid="stSidebar"] h3 {
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        font-weight: 600;
    }

    /* File uploader styling */
    [data-testid="stSidebar"] .stFileUploader {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* File uploader text */
    [data-testid="stSidebar"] .stFileUploader label {
        color: white !important;
        font-weight: 500;
    }

    /* Browse files button */
    [data-testid="stSidebar"] button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 8px 16px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    [data-testid="stSidebar"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Chat messages styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }

    /* Title styling */
    h1 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        text-align: center;
        font-weight: 700;
    }

    /* Cards styling */
    .info-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        margin: 15px 0;
        border-top: 3px solid #667eea;
        transition: transform 0.3s ease;
    }

    .info-card:hover {
        transform: translateY(-5px);
    }

    /* Success message styling */
    .stSuccess {
        background: linear-gradient(90deg, #00C851, #007E33);
        color: white;
        border-radius: 15px;
        border: none;
    }

    /* Drag and drop area styling */
    [data-testid="stSidebar"] .st-emotion-cache-1erivf3 {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.4);
        border-radius: 15px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Header with custom styling
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h1>📚 LastMinute Padhai</h1>
    <p style='color: white; font-size: 18px; margin-top: -10px;'>
        <em>Your AI Study Assistant for Last-Minute Exam Prep</em>
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar for file upload
with st.sidebar:
    st.markdown("### 📄 Upload Study Material")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload your notes, textbooks, or study materials"
    )

# Main area
if uploaded_file is not None:
    # Display file info with custom styling
    st.markdown(f"""
    <div class='info-card'>
        <h3 style='color: #2E7D32; margin: 0;'>✅ File Uploaded Successfully!</h3>
        <p style='margin: 5px 0;'><strong>File:</strong> {uploaded_file.name}</p>
        <p style='margin: 5px 0;'><strong>Size:</strong> {uploaded_file.size / 1024:.1f} KB</p>
    </div>
    """, unsafe_allow_html=True)

    # Extract text from PDF
    pdf_reader = PyPDF2.PdfReader(BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Show text preview
    with st.expander("📖 Document Preview"):
        st.text_area("Extracted Text", text[:1000] + "...", height=200)

    # Chat interface
    st.markdown("### 💬 Ask Questions About Your Document")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask anything about your study material..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response using the integrated function
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                response = get_ai_response(prompt, text)
                st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

else:
    # Welcome message with cards
    st.markdown("""
    <div class='info-card' style='text-align: center;'>
        <h3 style='color: #1976D2;'>👆 Upload a PDF to start your study session!</h3>
        <p>Get instant answers from your study materials using AI</p>
    </div>
    """, unsafe_allow_html=True)

    # Feature cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class='info-card'>
            <h4 style='color: #E65100;'>📚 Upload PDFs</h4>
            <p>Upload textbooks, notes, research papers</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='info-card'>
            <h4 style='color: #7B1FA2;'>🤖 AI Chat</h4>
            <p>Ask questions and get instant answers</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='info-card'>
            <h4 style='color: #388E3C;'>🔒 Privacy First</h4>
            <p>All processing happens locally</p>
        </div>
        """, unsafe_allow_html=True)
