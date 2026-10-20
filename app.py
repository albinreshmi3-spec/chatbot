
import re
import streamlit as st
from pypdf import PdfReader

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="AstraAIT | Study Assistant",
    page_icon="🧠",
    layout="wide"
)

# ---------- Theme and Mobile Input Fix ----------
st.markdown("""
<style>
:root {
    color-scheme: dark;
}

.stApp {
    background: #0b0d15;
    color: #f4f5fb;
}

[data-testid="stSidebar"] {
    background: #20212b;
    border-right: 1px solid #343544;
}

.block-container {
    max-width: 1050px;
    padding-top: 1.7rem;
    padding-bottom: 5rem;
}

.hero {
    padding: 0.4rem 0 1.2rem;
}

.hero h1 {
    font-size: 2.15rem;
    margin-bottom: .2rem;
    color: #f6f6ff;
}

.hero p {
    color: #aeb2c5;
    margin-top: 0;
}

.chat-card {
    background: #171923;
    border: 1px solid #2b2e3c;
    border-radius: 14px;
    padding: 1rem 1.1rem;
    margin: .6rem 0;
}

.stButton > button {
    border-radius: 9px;
}

/* Mobile and desktop chat input */
[data-testid="stChatInput"] {
    background-color: #20212b !important;
    border: 1px solid #555970 !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    background-color: #20212b !important;
    font-size: 16px !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #c5c7d3 !important;
    -webkit-text-fill-color: #c5c7d3 !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button {
    color: #ffffff !important;
}

/* Other input fields */
.stTextInput input,
.stTextArea textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    background-color: #20212b !important;
    caret-color: #ffffff !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #c5c7d3 !important;
    -webkit-text-fill-color: #c5c7d3 !important;
    opacity: 1 !important;
}

@media (max-width: 600px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
    }

    .hero h1 {
        font-size: 1.7rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ---------- AIT Knowledge Base ----------
KB = [
    (
        ["difference between bfs and dfs", "bfs vs dfs"],
        "**BFS vs DFS:** BFS explores level by level using a queue "
        "and finds the shallowest solution when step costs are equal. "
        "DFS explores deeply using a stack or recursion and usually "
        "uses less memory, but does not guarantee the shortest path."
    ),
    (
        ["what is ai", "define ai", "artificial intelligence"],
        "Artificial Intelligence (AI) is a branch of computer science "
        "that builds systems able to perform tasks that normally require "
        "human intelligence, such as reasoning, learning, planning, "
        "perception, and understanding language."
    ),
    (
        ["intelligent agent"],
        "An **intelligent agent** perceives its environment through "
        "sensors and acts through actuators to achieve a goal. Examples "
        "include robots, navigation apps, and game-playing programs."
    ),
    (
        ["rational agent", "rationality"],
        "A **rational agent** chooses the action expected to maximize "
        "its performance measure, given its percepts, knowledge, and "
        "available actions."
    ),
    (
        ["task environment", "peas"],
        "A task environment can be described with **PEAS**: Performance "
        "measure, Environment, Actuators, and Sensors. For a vacuum robot, "
        "these include cleanliness, rooms and dirt, wheels and suction, "
        "and dirt/location sensors."
    ),
    (
        ["uninformed search", "blind search"],
        "Uninformed search uses no extra estimate of how close a state "
        "is to the goal. Common methods include BFS, DFS, Uniform-Cost "
        "Search, Depth-Limited Search, and Iterative Deepening DFS."
    ),
    (
        ["breadth first search", "breadth-first search", "bfs"],
        "**Breadth-First Search (BFS)** explores nodes level by level, "
        "usually using a FIFO queue. It finds the shallowest solution "
        "and is optimal when all step costs are equal."
    ),
    (
        ["depth first search", "depth-first search", "dfs"],
        "**Depth-First Search (DFS)** explores one branch deeply before "
        "backtracking, using a stack or recursion. It usually uses less "
        "memory but does not guarantee the shortest path."
    ),
    (
        ["a star", "a*", "astar"],
        "**A* Search** evaluates nodes using **f(n) = g(n) + h(n)**, "
        "where g(n) is the cost so far and h(n) estimates the remaining "
        "cost. With suitable conditions, A* can find an optimal solution."
    ),
    (
        ["heuristic"],
        "A **heuristic** estimates how close a state is to the goal. "
        "An admissible heuristic never overestimates the true minimum "
        "remaining cost."
    ),
    (
        ["constraint satisfaction", "csp"],
        "A **Constraint Satisfaction Problem (CSP)** consists of "
        "variables, domains of possible values, and constraints. "
        "Examples include map coloring, Sudoku, and timetable scheduling."
    ),
    (
        ["knowledge representation", "propositional logic"],
        "Knowledge representation stores facts and relationships so "
        "a system can reason with them. Propositional logic uses true/false "
        "statements and connectives such as AND, OR, NOT, and implication."
    ),
    (
        ["forward chaining"],
        "**Forward chaining** is data-driven reasoning. It starts with "
        "known facts and applies matching rules to derive new conclusions."
    ),
    (
        ["backward chaining"],
        "**Backward chaining** is goal-driven reasoning. It starts with "
        "a goal and checks which rules or facts can prove it."
    ),
    (
        ["if then", "production rule"],
        "A production rule has the form **IF condition THEN conclusion "
        "or action**. Example: IF the road is wet THEN it may be slippery."
    ),
    (
        ["alpha beta", "alpha-beta", "pruning"],
        "**Alpha-beta pruning** speeds up minimax by skipping branches "
        "that cannot affect the final decision. Pruning occurs when "
        "alpha is greater than or equal to beta."
    ),
    (
        ["minimax"],
        "**Minimax** is a decision method for two-player, zero-sum games. "
        "MAX chooses the highest value and MIN chooses the lowest value."
    ),
    (
        ["machine learning", "ml"],
        "Machine Learning (ML) is a part of AI where systems learn "
        "patterns from data. Its main types are supervised learning, "
        "unsupervised learning, and reinforcement learning."
    ),
    (
        ["neural network", "deep learning"],
        "A **neural network** contains connected computational units "
        "called neurons arranged in layers. Deep learning uses networks "
        "with multiple layers to learn complex patterns."
    ),
    (
        ["natural language processing", "nlp"],
        "Natural Language Processing (NLP) enables computers to work "
        "with human language. Applications include translation, "
        "sentiment analysis, and question answering."
    ),
    (
        ["expert system"],
        "An **expert system** imitates a specialist's decision-making "
        "in a narrow domain. It typically contains a knowledge base, "
        "an inference engine, and a user interface."
    ),
]


# ---------- Answer Function ----------
def answer_question(question, notes=""):
    q = question.lower().strip()

    # Match the most specific keywords first.
    for keywords, answer in sorted(
        KB,
        key=lambda item: max(len(k) for k in item[0]),
        reverse=True
    ):
        if any(keyword in q for keyword in keywords):
            return answer

    # Search uploaded notes if no built-in answer matches.
    if notes.strip():
        terms = [
            term for term in re.findall(r"[a-zA-Z]{4,}", q)
            if term not in {
                "explain", "what", "define", "about",
                "this", "that", "with", "give", "example"
            }
        ]

        if terms and any(term in notes.lower() for term in terms):
            return (
                "I found related content in your uploaded notes:\n\n"
                + notes[:1800]
                + "\n\nAsk a more specific question for a focused answer."
            )

    return (
        "I'm AstraAIT, your AIT study assistant. I can explain AI "
        "concepts, search algorithms, logic, and machine learning.\n\n"
        "This starter version uses built-in answers and PDF text lookup; "
        "it is not connected to a live AI language model yet.\n\n"
        "**Try asking:** What is AI? Explain BFS vs DFS. "
        "What is an intelligent agent? Explain A* search."
    )


# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🧠 AstraAIT")
    st.caption("Your Artificial Intelligence Techniques study partner")

    st.selectbox(
        "Choose a subject",
        [
            "Artificial Intelligence Techniques",
            "Search Algorithms",
            "Knowledge Representation",
            "Machine Learning",
            "Exam Revision"
        ]
    )

    st.divider()
    st.markdown("### 🎙️ Voice question")
    st.caption("Voice input is not implemented yet. Type your question below.")

    st.info("Tip: Ask one concept at a time for clearer explanations.")

    st.divider()
    st.markdown("### 📄 Study PDF")

    uploaded_file = st.file_uploader(
        "Upload your notes (PDF)",
        type=["pdf"]
    )

    notes_text = ""

    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            notes_text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )
            st.success(f"Loaded {len(reader.pages)} page(s)")
        except Exception as exc:
            st.error(f"Could not read this PDF: {exc}")

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.caption("AstraAIT • Python + Streamlit")


# ---------- Main Header ----------
st.markdown("""
<div class="hero">
    <h1>🧠 AstraAIT</h1>
    <p>AI study companion for Artificial Intelligence Techniques</p>
</div>
""", unsafe_allow_html=True)


# ---------- Welcome Screen ----------
if not st.session_state.messages:
    st.markdown("""
    <div class="chat-card">
        <b>👋 Hello! I'm AstraAIT.</b><br><br>
        Ask me about AI concepts, search algorithms, logic, agents,
        or machine learning. You can also upload PDF notes.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Try a question")

    examples = [
        "What is Artificial Intelligence?",
        "Explain BFS vs DFS",
        "What is an intelligent agent?",
        "Explain A* search"
    ]

    cols = st.columns(2)

    for i, example in enumerate(examples):
        if cols[i % 2].button(
            example,
            use_container_width=True,
            key=f"example_{i}"
        ):
            st.session_state.pending_question = example
            st.rerun()


# ---------- Display Chat History ----------
for message in st.session_state.messages:
    avatar = "🧑‍🎓" if message["role"] == "user" else "🧠"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


# ---------- Chat Input ----------
prompt = st.chat_input("Ask your AIT question...")

if st.session_state.pending_question is not None:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    response = answer_question(prompt, notes_text)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    st.rerun()
