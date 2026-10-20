import os
import re
import streamlit as st
st.markdown("""

st.markdown("""
<style>
/* Fix text visibility in the chat input on mobile */
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    background-color: #20212b !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #c5c7d3 !important;
    -webkit-text-fill-color: #c5c7d3 !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] {
    background-color: #20212b !important;
}

[data-testid="stChatInput"] button {
    color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)

from pypdf import PdfReader

st.set_page_config(page_title="AstraAIT | Study Assistant", page_icon="🧠", layout="wide")

# ---------- Theme ----------
st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: #0b0d15; color: #f4f5fb; }
[data-testid="stSidebar"] { background: #20212b; border-right: 1px solid #343544; }
.block-container { max-width: 1050px; padding-top: 1.7rem; }
.hero { padding: 0.4rem 0 1.2rem; }
.hero h1 { font-size: 2.15rem; margin-bottom: .2rem; color: #f6f6ff; }
.hero p { color: #aeb2c5; margin-top: 0; }
.chat-card { background: #171923; border: 1px solid #2b2e3c; border-radius: 14px; padding: 1rem 1.1rem; margin: .6rem 0; }
.stButton > button { border-radius: 9px; }
div[data-testid="stChatInput"] { border-color: #3a3d50; }
.small-muted { color: #aeb2c5; font-size: .85rem; }
</style>
""", unsafe_allow_html=True)

# ---------- AIT starter knowledge base ----------
KB = [
    (["what is ai", "define ai", "artificial intelligence"], 
     "Artificial Intelligence (AI) is a branch of computer science that builds systems able to perform tasks that normally require human intelligence, such as reasoning, learning, planning, perception, and understanding language."),
    (["intelligent agent", "agent"], 
     "An **intelligent agent** perceives its environment through sensors and acts on it through actuators to achieve a goal. Examples include a robot, a navigation app, or a game-playing program."),
    (["rational agent", "rationality"], 
     "A **rational agent** chooses the action expected to maximize its performance measure, given its percepts, knowledge, and available actions. Rational does not mean omniscient; it means making the best expected choice with available information."),
    (["environment", "task environment", "peas"], 
     "A task environment can be described with **PEAS**: **P**erformance measure, **E**nvironment, **A**ctuators, and **S**ensors. Example for a vacuum robot: cleanliness, rooms/dirt, wheels/suction, and dirt/location sensors."),
    (["uninformed search", "blind search"], 
     "Uninformed search uses no extra estimate of how close a state is to the goal. Common methods are Breadth-First Search (BFS), Depth-First Search (DFS), Uniform-Cost Search (UCS), Depth-Limited Search, and Iterative Deepening DFS."),
    (["bfs", "breadth first"], 
     "**Breadth-First Search (BFS)** explores nodes level by level, usually using a FIFO queue. It is complete for finite branching factors and finds the shallowest solution; it is optimal when every step has the same cost."),
    (["dfs", "depth first"], 
     "**Depth-First Search (DFS)** explores one branch deeply before backtracking, usually using a stack or recursion. It uses relatively little memory, but may not find the shortest path and can get stuck in deep/infinite paths without safeguards."),
    (["a star", "a*", "astar"], 
     "**A\\* search** evaluates a node using **f(n) = g(n) + h(n)**, where g(n) is the cost so far and h(n) estimates the remaining cost. With an admissible heuristic (and suitable graph-search conditions), A\\* can find an optimal solution."),
    (["heuristic"], 
     "A **heuristic** is an estimate used to guide search toward a goal. For example, straight-line distance can estimate travel distance. An admissible heuristic never overestimates the true minimum remaining cost."),
    (["constraint satisfaction", "csp"], 
     "A **Constraint Satisfaction Problem (CSP)** consists of variables, domains of possible values, and constraints restricting which combinations are allowed. Examples include map coloring, Sudoku, and timetable scheduling. Common methods include backtracking, forward checking, and constraint propagation."),
    (["knowledge representation", "propositional logic"], 
     "Knowledge representation stores facts and relationships so a system can reason with them. Propositional logic uses statements that are true or false and connectives such as AND (∧), OR (∨), NOT (¬), and implication (→)."),
    (["if then", "production rule", "rules"], 
     "A production rule has the form **IF condition THEN conclusion/action**. Example: IF the road is wet THEN the road may be slippery. Rule-based systems apply rules to known facts using inference strategies such as forward chaining or backward chaining."),
    (["forward chaining"], 
     "**Forward chaining** is data-driven reasoning: start with known facts, fire rules whose conditions match, and add their conclusions until a goal is found or no more rules apply."),
    (["backward chaining"], 
     "**Backward chaining** is goal-driven reasoning: start with a goal, find rules that could prove it, then check whether their premises can be established from facts or other rules."),
    (["minimax"], 
     "**Minimax** is a decision method for two-player, zero-sum games. MAX chooses the move with the highest value, while MIN chooses the move with the lowest value. It explores a game tree assuming both players play optimally."),
    (["alpha beta", "alpha-beta", "pruning"], 
     "**Alpha-beta pruning** speeds up minimax by skipping branches that cannot affect the final decision. Alpha is MAX's best guaranteed value; beta is MIN's best guaranteed value. Pruning is possible when alpha ≥ beta."),
    (["machine learning", "ml"], 
     "Machine Learning (ML) is a part of AI where systems learn patterns from data. Main categories are supervised learning (labelled examples), unsupervised learning (finding structure without labels), and reinforcement learning (learning through rewards and penalties)."),
    (["neural network", "deep learning"], 
     "A **neural network** is a model made of connected computational units (neurons) arranged in layers. Deep learning uses neural networks with multiple layers to learn complex patterns from data."),
    (["natural language processing", "nlp"], 
     "Natural Language Processing (NLP) enables computers to work with human language. Tasks include text classification, translation, sentiment analysis, question answering, and speech recognition."),
    (["expert system"], 
     "An **expert system** imitates a specialist's decision-making in a narrow domain. Its main parts typically include a knowledge base, inference engine, user interface, and explanation facility."),
    (["difference between bfs and dfs", "bfs vs dfs"], 
     "**BFS vs DFS:** BFS explores level by level with a queue and can find the shortest path when all edges have equal cost, but often uses more memory. DFS explores deeply with a stack/recursion and usually uses less memory, but does not guarantee the shortest path."),
]

def answer_question(question, notes=""):
    q = question.lower().strip()
    # Prefer longer/more specific matches
    for keywords, answer in sorted(KB, key=lambda item: max(len(k) for k in item[0]), reverse=True):
        if any(k in q for k in keywords):
            return answer
    if notes.strip():
        terms = [t for t in re.findall(r"[a-zA-Z]{4,}", q) if t not in {"explain", "what", "define", "about", "this", "that", "with", "give", "example"}]
        if terms and any(t.lower() in notes.lower() for t in terms):
            return ("I found related content in your uploaded notes. Here is a useful way to study it:\n\n"
                    + notes[:1800]
                    + "\n\nAsk me a more specific question about this section for a focused explanation.")
    return ("I’m AstraAIT, your AIT study assistant. I can explain AI concepts, give definitions, compare algorithms, and provide exam-style answers. "
            "I don’t have a live language-model API connected in this starter version, so I may not know every topic yet.\n\n"
            "Try asking: **What is an intelligent agent?**, **Explain BFS vs DFS**, **What is A\\* search?**, or **Explain forward chaining with an example**.")

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🧠 AstraAIT")
    st.caption("Your Artificial Intelligence Techniques study partner")
    subject = st.selectbox("Choose a subject", ["Artificial Intelligence Techniques", "Search Algorithms", "Knowledge Representation", "Machine Learning", "Exam Revision"])
    st.divider()
    st.markdown("### 🎙️ Voice question")
    st.caption("Voice input can be added in a future version. For now, type your question in the chat box.")
    st.info("Tip: Ask one concept at a time for clearer explanations.")
    st.divider()
    st.markdown("### 📄 Study PDF")
    uploaded_file = st.file_uploader("Upload your notes (PDF)", type=["pdf"])
    notes_text = ""
    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            notes_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            st.success(f"Loaded {len(reader.pages)} page(s)")
        except Exception as exc:
            st.error(f"Could not read this PDF: {exc}")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("AstraAIT • Python + Streamlit")

# ---------- Main content ----------
st.markdown("""
<div class="hero">
  <h1>🧠 AstraAIT</h1>
  <p>AI-powered study companion for Artificial Intelligence Techniques</p>
</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.markdown('<div class="chat-card"><b>👋 Hello! I’m AstraAIT.</b><br><br>Ask me about AI concepts, search algorithms, logic, agents, or machine learning. I can also use text extracted from a PDF you upload.</div>', unsafe_allow_html=True)
    st.markdown("#### Try a question")
    cols = st.columns(2)
    examples = ["What is Artificial Intelligence?", "Explain BFS vs DFS", "What is an intelligent agent?", "Explain A* search"]
    for i, example in enumerate(examples):
        if cols[i % 2].button(example, use_container_width=True):
            st.session_state.pending_question = example
            st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🧑‍🎓" if message["role"] == "user" else "🧠"):
        st.markdown(message["content"])

prompt = st.chat_input("Ask your AIT question...")
if "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = answer_question(prompt, notes_text)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
