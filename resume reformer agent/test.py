from langchain.prompts import ChatPromptTemplate
from custom_wrapper import OpenRouterChat  # Your custom wrapper

def extract_trending_skills(job_description: str) -> list[str]:
    template = """
You are an expert recruiter and skills analyst.

TASK:
From the following job description, extract a concise list of trending skills (technical and soft skills) required for the role.

OUTPUT:
- Return the skills ONLY as a Python list of strings.
- Do NOT include any explanations or extra text.
- Skills should be comma separated inside the list, e.g. ["skill1", "skill2", "skill3"].
- Extract only relevant and trending skills that appear in the job description.

Job Description:
{job_desc}
"""

    prompt = ChatPromptTemplate.from_template(template)

    llm = OpenRouterChat(
        api_key="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",
        model="mistralai/mistral-7b-instruct:free",
        temperature=0.3
    )

    chain = prompt | llm

    response = chain.invoke({"job_desc": job_description})

    output = response.content.strip() if hasattr(response, "content") else str(response).strip()

    # Evaluate the string output safely to get Python list
    try:
        trending_skills = eval(output)
        if not isinstance(trending_skills, list):
            trending_skills = []
    except Exception:
        trending_skills = []

    return trending_skills
