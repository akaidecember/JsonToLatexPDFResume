# LaTeX Resume Generator

This project generates a beautifully formatted resume in PDF format using LaTeX, from a structured `JSON` input. It is designed for developers who want full control over layout, spacing, and typography while keeping the content easily editable in code.

---

## Features

- Clean, professional LaTeX PDF output
- Customizable sections (Education, Experience, Projects, Skills)
- Automatically escapes LaTeX-special characters
- Adjustable spacing and font sizes
- Easy CLI usage

---

## Dependencies

Ensure the following are installed on your system:

- **Python 3.6+**
- **LaTeX distribution** (`pdflatex` must be in your PATH)
  - macOS: [MacTeX](https://tug.org/mactex/)
  - Ubuntu: `sudo apt install texlive-full`
  - Windows: [MiKTeX](https://miktex.org/)

Python packages used:
- No external packages required (standard library only)

---

## How to Use

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/latex-resume-generator.git
cd latex-resume-generator
```

### 2. Create your resume content file

Create a `resume_content.json` file (see structure below).

### 3. Run the generator

```bash
python resume.py resume_content.json --output-dir output/
```

This will generate:
```
output/
├── resume.tex
└── resume.pdf 
```

---

## Input Format (`resume_content.json`)

Your JSON input should look like this:

```json
{
  "full_name": "John Doe",
  "location": "New York, NY",
  "phone_number": "+1-555-123-4567",
  "email": "johndoe@example.com",
  "linkedin_url": "https://www.linkedin.com/in/johndoe",
  "linkedin_short_url": "",
  "education": [
    {
      "university": "Example University",
      "location": "New York, NY",
      "degree": "Bachelor of Science, Computer Science",
      "date": "Aug 2019 -- May 2023",
      "courses": [
        "Data Structures",
        "Algorithms",
        "Machine Learning",
        "Cloud Computing",
        "Distributed Systems",
        "Databases",
        "Software Engineering"
      ]
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Tech Solutions Inc.",
      "location": "San Francisco, CA",
      "date": "Jun 2023 -- Present",
      "description": [
        "Developed scalable REST APIs using Django and PostgreSQL.",
        "Reduced page load times by 35% by optimizing backend services.",
        "Automated deployment pipelines using Jenkins and Docker."
      ]
    },
    {
      "title": "Backend Developer Intern",
      "company": "CodeLabs",
      "location": "Boston, MA",
      "date": "May 2022 -- Aug 2022",
      "description": [
        "Built microservices with Node.js and Express.",
        "Worked with Redis and RabbitMQ for messaging and caching.",
        "Wrote unit tests increasing coverage by 40%."
      ]
    }
  ],
  "projects": [
    {
      "title": "Smart Inventory Manager",
      "date": "Mar 2023",
      "tech_stack": "React, Flask, PostgreSQL",
      "link": "",
      "description": [
        "Created a real-time inventory dashboard with low-stock alerts.",
        "Implemented user authentication and role-based access.",
        "Integrated external supplier APIs for inventory sync."
      ]
    },
    {
      "title": "ChatBot Assistant",
      "date": "Oct 2022",
      "tech_stack": "Python, NLP, FastAPI",
      "link": "",
      "description": [
        "Designed a chatbot for customer support using NLTK and SpaCy.",
        "Deployed backend on Heroku with continuous integration setup.",
        "Achieved 92% accuracy in intent classification tasks."
      ]
    }
  ],
  "skills": [
    {
      "name": "Languages",
      "value": "Python, Java, JavaScript, SQL"
    },
    {
      "name": "Frameworks",
      "value": "React, Django, Node.js"
    },
    {
      "name": "Databases",
      "value": "PostgreSQL, MongoDB"
    },
    {
      "name": "DevOps",
      "value": "Docker, Jenkins, GitHub Actions"
    },
    {
      "name": "Other",
      "value": "Linux, REST APIs, Agile, Jira"
    }
  ]
}
```

---

## Output

The output is a clean, 1-page `resume.pdf` with:

- Bolded headings and job titles
- Left-aligned bullets (ragged-right)
- Small-caps section headers with underline
- Narrow margins for space efficiency

[View Sample Resume generated from above json](resume.pdf)
---
