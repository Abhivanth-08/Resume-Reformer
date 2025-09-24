from pdf4 import extract_pdf_details
from runall2 import generate_new_detail
from test import extract_trending_skills
from suma import gen_dict
from suma2 import gen_pdf
from github_extract import fetch_projects_from_subfolders
from proj_ext import proj_ext_exe
from project_selector_agent import psa_exe
from proj_agent import proj_create


git_link="https://github.com/Abhivanth-08/All-Projects"
s=git_link.split("/")
git=fetch_projects_from_subfolders(s[-2],s[-1])

res="R Abhivanth Resume.pdf"

old="old_det.json"
old2="old_det2.json"
new="new_det.json"
proj="projects.json"
projupd="projects_upd.json"
resmain1 =res[:-4]+"1.pdf"
job_des = open("job_des.txt","r").read()
tr=extract_trending_skills(job_des)

extract_pdf_details(res,old)
proj_ext_exe(res,proj)
psa_exe(job_des,git,proj,projupd)

proj_create(old,proj,projupd,old2)
d=generate_new_detail(old2,new,job_des,tr)
rep=gen_dict(old2,d)
gen_pdf(res,rep,resmain1)


