from pathlib import Path
from ollama import chat
import json


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""


service_status = {
    "wifi": "operational"
}

state = {
    "problem": question,
    "wi_fi status": "operational",
    "wi-fi_check": True
}

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )

with open("state.json", "r") as file:
    state = json.load(file)

print(state)



def select_context(question):
    q = question.lower()
    files = []


    if any(word in q for word in ["wi-fi", "wifi", "wireless", "eduroam", "connect", "connection", "network"]):
        files.append("knowledge/wifi_setup.txt")
        files.append("knowledge/service_status.txt")

  
    if any(word in q for word in ["password", "pass", "credential", "changed password", "new password", "old password"]):
        files.append("knowledge/password_changes.txt")

    if any(word in q for word in ["vpn", "remote", "off-campus", "outside campus"]):
        files.append("knowledge/vpn.txt")

    if any(word in q for word in ["email", "e-mail", "mail", "outlook", "webmail"]):
        files.append("knowledge/email_setup.txt")


    if any(word in q for word in ["print", "printer", "printing", "print queue"]):
        files.append("knowledge/printing.txt")

    if any(word in q for word in ["projector", "project", "hdmi", "display", "screen", "classroom"]):
        files.append("knowledge/classroom_projectors.txt")


    seen = set()
    unique_files = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)

    return unique_files


selected_files = select_context(question)


context = ""

for file_path in selected_files:
    context += Path(file_path).read_text()
    context += "\n\n"



def compress_context(context, question):
    response = chat(
        model="qwen2.5",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a context compression assistant. "
                    "Your task is to compress the given knowledge base context "
                    "so that only information directly relevant to the user's question is kept. "
                    "Preserve all key facts, steps, and instructions that could help answer the question. "
                    "Do not add any new information. "
                    "Output only the compressed text, nothing else."
                )
            },
            {
                "role": "user",
                "content": f"User question:\n{question}\n\nContext to compress:\n{context}"
            }
        ]
    )
    return response.message.content


compressed_context = compress_context(context, question)


print(len(compressed_context))


state_summary = (
    "Service state:\n"
    f"  Wi-Fi status: {state['wi_fi status']}\n"
    f"  Wi-Fi checked: {state['wi-fi_check']}\n"
)

response = chat(
    model="qwen2.5",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a university IT support assistant. "
                "Use the provided compressed knowledge base and service state to answer the student's question. "
                "Provide clear, step-by-step instructions. "
                "Structure your answer with clear headings."
            )
        },
        {
            "role": "user",
            "content": (
                f"Compressed knowledge base:\n\n{compressed_context}\n\n"
                f"{state_summary}\n"
                f"Student's question:\n{question}"
            )
        }
    ]
)


print(response.message.content)



state["answer"] = response.message.content
state["selected_files"] = selected_files
state["context_length"] = len(context)
state["compressed_context_length"] = len(compressed_context)

with open("state.json", "w") as file:
    json.dump(
        state,
        file,
        indent=2
    )
