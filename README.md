🌟 ResuMate Pro – Smart Resume Analyzer for Job Matching
ResuMate Pro is an intelligent web application that helps job seekers optimize their resumes to match job descriptions. With ATS (Applicant Tracking System) scoring, keyword analysis, and smart improvement suggestions, ResuMate Pro ensures your resume stands out in the hiring pipeline.

🔍 Features
🔐 User Authentication: Secure registration and login with hashed passwords using SQLite.

📄 Resume Upload: Upload your PDF resume for analysis.

🎯 Job-Based Scoring: Choose your target job title and get analyzed against relevant keywords.

🧠 ATS Score Calculation: See how well your resume matches industry standards and job expectations.

🧩 Keyword Insights:

✅ Matched Keywords

❌ Missing Keywords

🛠️ Improvement Suggestions: Tailored recommendations to improve resume quality, content, and formatting.

🎨 Beautiful UI: Built with a glassmorphic pastel design, offering a smooth, professional user experience.

🖥️ Tech Stack

Layer	Technologies Used
Frontend	HTML, CSS, JavaScript (Vanilla)
Backend	Python, Flask
Database	SQLite (with password hashing)
Resume Parsing	PyPDF2, re, nltk
Keyword Matching	Custom logic + job_keywords.json
Styling	Pastel, glassmorphic theme


📁 Folder Structure
csharp
Copy
Edit
resumate-pro/
│
├── static/                 # CSS, JS, assets
├── templates/              # HTML files
├── job_keywords.json       # Static keyword data
├── app.py                  # Main Flask application
├── database.db             # SQLite database
└── README.md               # This file
📌 Future Enhancements

✅ Export results as PDF

🔄 Dynamic keyword extraction from live job listings

📈 Admin dashboard to view user stats

🌐 Resume suggestions using GPT/NLP

✉️ Email report of analysis

🤝 Contributors
Sangeetha G.S. 

📄 License
This project is licensed under the MIT License.

🙌 Acknowledgements
Inspired by real-world ATS systems.

Resume parsing with nltk, PyPDF2.

UI inspired by Dribbble glassmorphism designs.

If you find this as useful give me 🌟
