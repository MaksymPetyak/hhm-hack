import openai
import streamlit as st
from streamlit_chat import message
import random
import time

openai_api_key = st.secrets.openai_api_key

st.title("Gerda App - Practice communication with children")
st.info("""Imagine you are a parent of a 6-year-old child. 
She hurt her arm while playing volleyball in PE class, and the doctor ordered an X-ray.
Your child is scared of the X-ray procedure, and you want to explain to her what is going to happen in a reassuring manner.
Gerda AI will suggest improvements to your explanation based on our best practices.
""")

st.session_state["is_processing_input"] = False if "is_processing_input" not in st.session_state else st.session_state["is_processing_input"]
st.session_state["render_count"] = 0 if "render_count" not in st.session_state else st.session_state["render_count"] + 1

if "messages" not in st.session_state:
    # TODO: JSON output
    st.session_state["messages"] = [
        {"role": "system", "content": """
You are a helpful assistant who is trying to help improve parent's communication with their child.
Given a parent's message, you will suggest a response that is more child-friendly. Give answers in 2 parts and following format:
```
FEEDBACK: Feedback and suggestion on what the parent should say. Make sure to include better examples of what the parent should say.
FOLLOW UP: Then a possible follow-up question from the child. Only ask follow-up questions as if the child is still frightened. If the response from parent was good or long, stop giving follow-up questions.
```

Here are some best practices to base your feedback on:
1. Use of analogies can be good for simple explanations.
2. Use positive language
3. Use simple language
4. The emotional state of the children is strongly determined by the emotional state of the adults, so avoid seeming stressed.
5. Children don’t want to be alone.
6. Offer the children an outlook to a reward after a challenge to increase their cooperation.
"""
        },
    ]

def add_starting_message():
    starting_messages = [
        "What happens when I’m in that tube? It looks scary.",
        "Is it going to be dark there?",
        "Is the procedure going to hurt?",
    ]
    st.session_state.messages.append(
        {"role": "assistant", "content": random.choice(starting_messages)}
    )

def display_messages():
    for idx, msg in enumerate(st.session_state.messages[1:]):
        avatar_style = "adventurer" if msg["role"] != "user" else None
        if msg["role"] == "assistant":
            if msg["content"].strip().startswith("FEEDBACK:"):
                avatar_style = "bottts"
                msg["content"] = msg["content"].replace("FEEDBACK:", "").strip()
            else:
                avatar_style = "adventurer"
                msg["content"] = msg["content"].strip(": ").strip()

        message(
            msg["content"],
            is_user=msg["role"] == "user",
            avatar_style=avatar_style,
            key=str(st.session_state.render_count) + "_" + str(idx),
        )


# Pick a starting message
if len(st.session_state.messages) == 1:
    add_starting_message()

print("Messages: ", len(st.session_state.messages))
display_messages()

if not st.session_state["is_processing_input"]:
    with st.form("chat_input", clear_on_submit=True):
        a, b = st.columns([4, 1])
        user_input = a.text_area(
            label="Your message:",
            placeholder="How would you respond to this message?",
            label_visibility="collapsed",
        )
        b.form_submit_button("Send", use_container_width=True)

    if user_input and openai_api_key:
        openai.api_key = openai_api_key
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state["is_processing_input"] = True
        user_input = None

        # FIXME: figure out why need this for stable state management
        time.sleep(0.05)

        st.experimental_rerun()
else:
    if openai_api_key and st.session_state["is_processing_input"]:
        st.text("Processing...")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=st.session_state.messages
        )
        msg = response.choices[0].message
        feedback, follow_up = msg["content"].split("FOLLOW UP:")

        st.session_state.messages.append({**msg, "content": feedback})
        st.session_state.messages.append({**msg, "content": follow_up})
        st.session_state["is_processing_input"] = False
        st.experimental_rerun()

st.button("Restart", on_click=lambda: st.session_state.clear())