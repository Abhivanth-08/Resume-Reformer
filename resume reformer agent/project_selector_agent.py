from langchain.prompts import ChatPromptTemplate
from custom_wrapper import OpenRouterChat
import json

#git=['Autonomous Drainage Cleaning Robot', 'College Chatbot', 'Exhibit Defect Detection System', 'Loyalty Prediction', 'Mini Versatile Robot', 'NDT','E Commerce website','Animated Website']
def ext_len(proj):
    f=open(proj,"r")
    d=json.load(f)
    return len(d)
def select_relevant_projects(job_description, github_projects,proj):
    max_projects=ext_len(proj)
    template = """
    You are a Project Relevance Selector Agent.

    Your task is to **analyze a list of GitHub projects** and **select only the most relevant ones** based on the given job description.

    🔒 RULES:
    - Select exactly {max_projects} most relevant projects.
    - Choose projects that **closely align with the skills or responsibilities** mentioned in the job description.
    - always give relevant description of the project for atleast 10 words, u generate by your own if you dont know.
    - DO NOT fabricate or invent any projects not listed in the GitHub project input.
    - DO NOT modify or enhance the project descriptions based on the job description.
    - The description must be taken **exactly** from the original GitHub project list.
    - The output should be a single JSON array with multiple dictionaries (one per selected project).
    - I need exact count of projects
    🧾 OUTPUT FORMAT:
    [
      
    {{
        "title": "Versatile Mini Robot",
        "description": "Designed a multifunctional robot with features like object recognition, color detection, QR/text scanning, translation, and virtual assistance. Technologies: Python, OpenCV, Raspberry Pi, Sensors."
    }},
    {{
        "title": "NDT Robot for Crack/Defect Detection",
        "description": "Built an autonomous mini robot using ultrasonic, infrared, and eddy current sensors for real-time crack detection with OpenCV and ML. Technologies: Python, OpenCV, Sensors, ML, Raspberry Pi."
    }},
    ]
    Exactly the output should be like above , no other extra words - reminder
    💼 Job Description:
    {job_description}

    🗂️ GitHub Projects:
    {github_projects}
    """

    prompt = ChatPromptTemplate.from_template(template)
    llm = OpenRouterChat(
        api_key="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",
        model="mistralai/mistral-7b-instruct:free",
        temperature=0.2,
    )

    chain = prompt | llm
    result = chain.invoke({
        "job_description": job_description,
        "github_projects": "\n".join(github_projects),
        "max_projects": max_projects
    })

    raw = result.content
    return raw

def psa_exe(job_des,git,proj,projupd):
    k=select_relevant_projects(job_des,git,proj)
    try:
        project_data = json.loads(k)
        with open(projupd, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4, ensure_ascii=False)

        print("✅ Project data saved to projects.json")

    except json.JSONDecodeError as e:
        print("❌ Failed to parse output as JSON:")
        print("Error:", e)

