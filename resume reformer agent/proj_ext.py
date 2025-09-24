import json
import fitz  # PyMuPDF
from langchain.prompts import ChatPromptTemplate
from custom_wrapper import OpenRouterChat  # Your wrapper


def extract_text_from_pdf(path):
    doc = fitz.open(path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text
def proj_extract(res):
    text=extract_text_from_pdf(res)
    template = """
You are an intelligent resume parser.

Given a resume as plain text input, extract all projects listed under the "Projects" or similar section.
For each project, return the project title and its corresponding description in a clean list format.

Look for section headings like “Projects”, “Project Experience”, “Academic Projects”, or “Key Projects”.

Example Output Format:
[
  {{
    "title": "NDT Robot for Crack Detection",
    "description": "Built an autonomous mini robot using ultrasonic, infrared, and eddy current sensors for real-time crack detection with OpenCV and ML."
  }},
  {{
    "title": "College Chatbot",
    "description": "Created an AI-powered chatbot to assist in automating admissions, events, and exam preparation using LangChain and NLP."
  }}
]

Now process the following resume text:
{res_text}
    """

    prompt = ChatPromptTemplate.from_template(template)

    llm = OpenRouterChat(
        api_key="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",
        model="mistralai/mistral-7b-instruct:free",
        temperature=0.4
    )

    chain = prompt | llm
    response = chain.invoke({"res_text": text})
    output = response.content.strip() if hasattr(response, "content") else str(response).strip()
    return output[output.index('['):output.index(']')+1]


def proj_ext_exe(res,proj):
    try:
        project_data = json.loads(proj_extract(res))
        with open(proj, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Project data saved to {proj}")
    except json.JSONDecodeError as e:
        print("❌ Failed to parse output as JSON:")
        print("Error:", e)

