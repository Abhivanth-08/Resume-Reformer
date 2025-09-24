import streamlit as st
from pdf4 import extract_pdf_details
from runall2 import generate_new_detail
from test import extract_trending_skills
from suma import gen_dict
from suma2 import gen_pdf
from github_extract import fetch_projects_from_subfolders
from proj_ext import proj_ext_exe
from project_selector_agent import psa_exe
from proj_agent import proj_create


def main():
    st.title("Resume Reformer Agent")

    git_link = st.text_input("Enter GitHub Repository URL",
                              value="https://github.com/Abhivanth-08/All-Projects")

    res_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

    job_des_text = st.text_area("Paste Job Description Text Here")

    if st.button("Run Analysis"):
        if not (git_link and res_file and job_des_text.strip()):
            st.error("Please provide all inputs: GitHub URL, Resume PDF, and Job Description text.")
            return

        s = git_link.strip().split("/")
        st.write(f"Fetching projects from GitHub user: {s[-2]}, repo: {s[-1]}")

        git = fetch_projects_from_subfolders(s[-2], s[-1])
        st.success("✅ GitHub projects fetched.")

        with open("temp_resume.pdf", "wb") as f:
            f.write(res_file.getbuffer())
        res = "temp_resume.pdf"

        job_des = job_des_text.strip()

        old = "old_det.json"
        old2 = "old_det2.json"
        new = "new_det.json"
        proj = "projects.json"
        projupd = "projects_upd.json"
        resmain1 = res[:-4] + "1.pdf"

        st.write("Extracting trending skills from job description...")
        tr = extract_trending_skills(job_des)
        st.success(f"✅ Trending skills extracted: {tr}")

        st.write("Extracting PDF details from resume...")
        extract_pdf_details(res, old)
        st.success("✅ PDF details extracted.")

        st.write("Extracting projects from resume PDF...")
        proj_ext_exe(res, proj)
        st.success("✅ Projects extracted.")

        st.write("Running project selector agent...")
        psa_exe(job_des, git, proj, projupd)
        st.success("✅ Project selector agent finished.")

        st.write("Creating project-resume linkage...")
        proj_create(old, proj, projupd, old2)
        st.success("✅ Project linkage created.")

        st.write("Generating new detailed resume content...")
        d = generate_new_detail(old2, new, job_des, tr)
        st.success("✅ New details generated.")

        st.write("Generating dictionary for resume reform...")
        rep = gen_dict(old2, d)
        st.success("✅ Dictionary generated.")

        st.write("Creating updated resume PDF...")
        gen_pdf(res, rep, resmain1)
        st.success(f"✅ Updated resume PDF created: {resmain1}")

        with open(resmain1, "rb") as f:
            st.download_button(
                label="Download Updated Resume PDF",
                data=f,
                file_name=resmain1,
                mime="application/pdf"
            )

main()
