from flask import Flask, render_template, request
import PyPDF2
import docx
import os

app = Flask(__name__)

# ---------------- ROLE SKILLS DATABASE ---------------- #

ROLE_SKILLS = {

"Data Scientist":[
"python","machine learning","deep learning","statistics",
"pandas","numpy","data analysis","tensorflow","pytorch","sql"
],

"Software Engineer":[
"java","python","c++","data structures","algorithms",
"system design","git","api","oop","debugging"
],

"Web Developer":[
"html","css","javascript","react","node","express",
"mongodb","frontend","backend","web development"
],

"Mobile App Developer":[
"android","kotlin","java","flutter","react native",
"mobile development","api","firebase"
],

"DevOps Engineer":[
"docker","kubernetes","aws","azure","ci/cd",
"jenkins","linux","terraform","cloud"
],

"Cloud Engineer":[
"aws","azure","google cloud","docker","kubernetes",
"cloud computing","linux","networking"
],

"Machine Learning Engineer":[
"python","machine learning","deep learning",
"tensorflow","pytorch","scikit learn","data pipelines"
],

"AI Engineer":[
"python","deep learning","nlp","computer vision",
"tensorflow","pytorch","machine learning"
],

"Frontend Developer":[
"html","css","javascript","react","vue","angular",
"ui","responsive design"
],

"Backend Developer":[
"python","java","node","api","database",
"sql","backend","server","microservices"
]

}

# ---------------- RESUME TEXT EXTRACTION ---------------- #

def extract_text(file):

    text=""

    if file.filename.endswith(".pdf"):

        pdf=PyPDF2.PdfReader(file)

        for page in pdf.pages:
            text+=page.extract_text()

    elif file.filename.endswith(".docx"):

        doc=docx.Document(file)

        for para in doc.paragraphs:
            text+=para.text

    return text.lower()


# ---------------- ATS SCORE ---------------- #

def calculate_ats_score(resume_text, role):

    skills=ROLE_SKILLS[role]

    matched=0

    for skill in skills:

        if skill.lower() in resume_text:
            matched+=1

    score=(matched/len(skills))*100

    return round(score,2)


# ---------------- MISSING SKILLS ---------------- #

def missing_skills(resume_text, role):

    skills=ROLE_SKILLS[role]

    missing=[]

    for skill in skills:

        if skill.lower() not in resume_text:
            missing.append(skill)

    return missing


# ---------------- SUGGESTIONS ---------------- #

def generate_suggestions(missing):

    suggestions=[]

    for skill in missing:

        suggestions.append(f"Add experience or projects related to {skill}")

    return suggestions


# ---------------- ROUTES ---------------- #

@app.route("/",methods=["GET","POST"])
def index():

    roles=list(ROLE_SKILLS.keys())

    if request.method=="POST":

        role=request.form["role"]

        file=request.files["resume"]

        resume_text=extract_text(file)

        ats=calculate_ats_score(resume_text,role)

        missing=missing_skills(resume_text,role)

        suggestions=generate_suggestions(missing)

        return render_template(
        "result.html",
        role=role,
        score=ats,
        missing=missing,
        suggestions=suggestions
        )

    return render_template("index.html",roles=roles)


if __name__=="__main__":
    app.run(debug=True)