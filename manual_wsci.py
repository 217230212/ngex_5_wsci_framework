from pathlib import Path
from ollama import chat


question = """
I changed my university password this morning.
Now my Windows laptop won't connect to campus Wi-Fi,
but my phone still works.
"""

selected_files = [
    "knowledge/wifi_setup.txt",
    "knowledge/password_changes.txt",
    "knowledge/service_status.txt",
]


context = ""

for file_path in selected_files:
    context += Path(file_path).read_text()
    context += "\n\n"


response = chat(
    model="qwen2.5",
    messages=[
        {
            "role": "system",
            "content": "You are a university IT support assistant. Use the provided knowledge base to answer the student's question."
        },
        {
            "role": "user",
            "content": f"Knowledge base:\n\n{context}\n\nStudent's question:\n{question}"
        }
    ]
)


print(
    "Context characters:",
    len(context)
)
print(response.message.content)
