import json
import time
import re
from langchain.prompts import ChatPromptTemplate
from custom_wrapper import OpenRouterChat
from runall import rewrite_to_length
from json_corrector import fix_and_save_json_string


def find_largest_common_substring(source: str, target: str):
    source = source.lower()
    target = target.lower()
    m = len(source)
    n = len(target)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    length = 0
    end_pos = 0

    for i in range(m):
        for j in range(n):
            if source[i] == target[j]:
                dp[i + 1][j + 1] = dp[i][j] + 1
                if dp[i + 1][j + 1] > length:
                    length = dp[i + 1][j + 1]
                    end_pos = j + 1

    if length == 0:
        return -1, -1, ""

    start = end_pos - length
    return start, end_pos, target[start:end_pos]

def extract_all_texts(json_data):
    texts = []

    # Step into each page
    for page in json_data.get("pages", []):
        # Step into each block
        for block in page.get("blocks", []):
            # Step into each line (which is a list of text items)
            for line in block.get("lines", []):
                for item in line:
                    if "text" in item:
                        texts.append(item["text"])

    return texts

def generate_new_detail(old, new, jd_text, trending_skills):
    # === Load original resume JSON ===
    with open(old, "r", encoding="utf-8") as f:
        resume_json = json.load(f)

    ml=extract_all_texts(resume_json)
    for i in range(len(ml)):
        if len(ml[i])<60:
            ml[i]=''

    # === Build reusable prompt template ===
    template ="""You are a deterministic Resume Reformer Agent.

INPUTS:
- Resume: a list of text entries (strings).
- Trending Skills: key skills relevant to the target job.
- Job Description: the job role and responsibilities.

TASK:
For each text entry in the Resume, rewrite it to better fit the Trending Skills and Job Description.

RULES:
- Only rewrite existing text entries one-to-one (no additions or deletions).
- Maintain original semantic meaning but use terminology that aligns with Trending Skills and Job Description.
- Do not invent new facts or unrelated content.
- Do not alter formatting or structure outside the rewritten text.
- Your rewriting must be deterministic (same input → same output).
- Provide output strictly as a list of pairs: [old_text, rewritten_text].
- Include only those pairs where rewriting was applied or improvement made.
- Output must look like this exactly:
- old Text must be the exact element present in the given list not even a single change made
- MAke sure to include all the words in the trending skills
- plssss old text are the element in given list dont combine it ever please please please
- Make sure new and old texts have same no of characters

example:
if list contains:
    'Innovative tech enthusiast skilled in advanced programming, ML, IoT, and app development, with hands-on'
u should not consider it as :
'Innovative tech enthusiast skilled in advanced programming, ML, IoT, and app development, with hands-on project experience.'
-dont give description for a project title

[
"old text here",
"rewritten text here"
],
[
"old text here",
"rewritten text here"
]

INPUTS:

Trending Skills:
{trending_skills}

Job Description:
{job_description}

Resume:
{resume}

"""



    prompt = ChatPromptTemplate.from_template(template)

    # === Initialize model ===
    llm = OpenRouterChat(
        api_key="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",
        model="mistralai/mistral-7b-instruct:free",
        temperature=0.3,
    )

    chain = prompt | llm

    print("🔧 Processing entire resume...")

    response = chain.invoke({
        "trending_skills": trending_skills,
        "job_description": jd_text,
        "resume": ml
    })

    raw_output = response.content.strip() if hasattr(response, "content") else str(response).strip()
    print(raw_output)
    raw_output = "["+raw_output[raw_output.index('"'):-2]
    print(raw_output)
    k=raw_output.split("],")
    print(k)
    d = {}
    print(len(k))
    for i in range(len(k)):
        st = k[i][k[i].index('"') + 1:-1].split('",')
        a = st[0].strip()
        b = st[1].replace('"', '').strip()
        bb = rewrite_to_length(b, len(a))
        d[a] = bb
    tst = str(resume_json)
    print(d)
    fp=open("n2.json","w")
    json.dump(d,fp,indent=2)
    fp.close()
    for i in d:
        tst=tst.replace(i,d[i])
    fix_and_save_json_string(tst,new)
    return d










