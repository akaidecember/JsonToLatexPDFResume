"""
Resume Generator from JSON to LaTeX PDF

This script takes a structured JSON file describing a resume and generates a LaTeX
document, then compiles it into a PDF using `pdflatex`.

Author: Anshul Kumar Shandilya
"""

import json, subprocess, shutil, os, argparse, sys

def sanitize_latex(s: str) -> str:
    """
    Escapes LaTeX special characters in a string to ensure correct formatting in the PDF.
    """
    return (s.replace('\\', r'\textbackslash{}')
             .replace('&', r'\&')
             .replace('%', r'\%')
             .replace('$', r'\$')
             .replace('#', r'\#')
             .replace('_', r'\_')
             .replace('{', r'\{')
             .replace('}', r'\}')
             .replace('~', r'\textasciitilde{}')
             .replace('^', r'\textasciicircum{}')
             .replace('|', r'\textbar{}'))

def generate_tex(data, oneLineEdu):
    """
    Constructs the LaTeX document as a list of lines using the given resume JSON data.
    Returns a complete LaTeX source string.
    """
    lines = []

    # ==== Preamble ====
    lines += [
        r"\documentclass[11pt]{article}",
        r"\usepackage[top=0.35in, bottom=0.4in, left=0.45in, right=0.45in]{geometry}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\usepackage{titlesec}",
        r"\usepackage{enumitem}",
        r"\setlist[itemize]{nosep,leftmargin=0.3in,label=\raisebox{0.15ex}{\scriptsize\textbullet}}",
        r"\pagestyle{empty}",
        r"\pdfgentounicode=1",
        r"\titleformat{\section}{\scshape\raggedright\footnotesize\bfseries}{}{0em}{}[\titlerule]",
        r"\titlespacing*{\section}{0pt}{1pt}{4pt}",
        r"\begin{document}",
        r""
    ]

    # ==== Header ====
    fn  = sanitize_latex(data["full_name"])
    ph  = sanitize_latex(data["phone_number"])
    em  = sanitize_latex(data["email"])
    loc = sanitize_latex(data["location"])

    li  = data.get("linkedin_url", "")
    git = data.get("github_link", "")
    lc  = data.get("leetcode_link", "")

    if li and not li.startswith("http"):
        li = "https://" + li
    if git and not git.startswith("http"):
        git = "https://" + git
    if lc and not lc.startswith("http"):
        lc = "https://" + lc

    #short_li = sanitize_latex(li.split("://")[-1]) if li else ""

    lines += [
        r"\begin{center}",
        rf"  {{\LARGE\bfseries {fn}}}\\[2pt]",
        rf"  {{\small  {ph} \,\textbar\, \href{{mailto:{em}}}{{{em}}}"
        + (rf" \,\textbar\, \href{{{li}}}{{LinkedIn}}" if li else "")
        + (rf" \,\textbar\, \href{{{git}}}{{Github}}" if git else "")
        + (rf" \,\textbar\, \href{{{lc}}}{{Leetcode}}" if lc else "")
        + rf" \,\textbar\, {loc}}}\\[4pt]",
        r"\end{center}",
        r""
    ]

    lines += [r"\vspace{-3pt}"]

    # ==== Education Section ====
    lines += [r"\vspace{-5pt}", r"\section{EDUCATION}", r"\noindent"]
    for edu in data.get("education", []):
        deg     = sanitize_latex(edu["degree"])
        dt      = sanitize_latex(edu["date"])
        un      = sanitize_latex(edu["university"])
        lo      = sanitize_latex(edu["location"])
        courses = ", ".join(sanitize_latex(c) for c in edu.get("courses", []))

        ###### Commented out one liner education 
        # if oneLineEdu:
        #     lines += [
        #         rf"\textbf{{{deg}}} \textbar\ {{{un}}} \textbar\ {{{lo}}} \hfill \textbf{{{dt}}}\\[4pt]",
        #         # rf"{un} \hfill {lo}\\[4pt]",
        #     ]
        # else:
        lines += [
            r"\normalsize",
            rf"\textbf{{{deg}}} \hfill \textbf{{{dt}}}\\[1pt]",
            rf"\textit{{{un}}} \hfill {lo}\\[6pt]",
        ]

        if courses:
            lines += [rf"\small \textbf{{Courses:}} {courses}\\[5pt]",]

    lines += [""]
    lines += [r"\vspace{-9pt}"]

    # ==== Technical Skills Section ====
    lines += [r"\vspace{-3pt}", r"\section{TECHNICAL SKILLS}", r"\noindent"]

    for skill in data.get("skills", []):
        nm  = sanitize_latex(skill["name"])
        val = sanitize_latex(skill["value"])
        lines.append(rf"\small \textbf{{{nm}}}: {val}\\[2pt]")

    lines += [""]

    # ==== Experience Section ====
    lines += [r"\vspace{-7pt}", r"\section{EXPERIENCE}", r"\noindent"]
    for exp in data.get("experience", []):
        ti = sanitize_latex(exp["title"])
        co = sanitize_latex(exp["company"])
        lo = sanitize_latex(exp["location"])
        da = sanitize_latex(exp["date"])

        lines.append(rf"\noindent \textbf{{{{{ti}}} \textbar\ {{{co}}}}} \textbar\ {lo} \hfill \textbf{{{{{da}}}}}\\[-6pt]")
        lines.append(r"\begin{itemize}")

        for desc in exp.get("description", []):
            lines.append(rf"  \item \small \raggedright {sanitize_latex(desc)}")

        lines.append(r"\end{itemize}")
        lines.append(r"\vspace{6pt}")

    # ==== Academic Projects Section ====
    if data.get("projects", []):
        lines += [r"\vspace{5pt}", r"\section{ACADEMIC PROJECTS}", r"\noindent"]

    for proj in data.get("projects", []):
        tl = sanitize_latex(proj["title"])
        dt = sanitize_latex(proj["date"])
        stk = sanitize_latex(proj["tech_stack"])
        lk = proj.get("link", "")

        if lk and not lk.startswith("http"):
            lk = "https://" + lk
        if lk:
            tl = rf"{{{tl}}} \textbar\ \href{{{lk}}}{{Link}}"

        lines.append(rf"\noindent \textbf{{{tl}}} \textbar\ \textit{{{stk}}} \hfill \textbf{{{dt}}}\\[-6pt]")
        lines.append(r"\begin{itemize}")

        for d in proj.get("description", []):
            lines.append(rf"  \item \small \raggedright {sanitize_latex(d)}")

        lines.append(r"\end{itemize}")
        lines.append(r"\vspace{4pt}")

    # ==== Certificates Section ====
    if data.get("certificates", []):
        lines += [r"\vspace{5pt}", r"\section{CERTIFICATION}", r"\noindent"]

    for certf in data.get("certificates", []):
        name = sanitize_latex(certf["name"])
        lk = certf.get("link", "")

        if lk and not lk.startswith("http"):
            lk = "https://" + lk
        if lk:
            name = rf"\href{{{lk}}}{{{name}}}"

        lines += [
            rf"{{{name}}} \hfill\\",
        ]
            
    lines += [""]

    lines.append(r"\end{document}")
    return "\n".join(lines)

def write_file(txt, path):
    """
    Writes the given text content to the specified file path using UTF-8 encoding.
    """
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)

def compile_to_pdf(tex_path, out_dir):
    """
    Compiles the LaTeX file at tex_path into a PDF in out_dir using pdflatex.
    Runs pdflatex twice to ensure proper references.
    """
    for _ in range(2):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", out_dir, tex_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def main():
    """
    Parses command-line arguments, generates the LaTeX resume from JSON input,
    writes the .tex file, and compiles it into a PDF.
    """
    p = argparse.ArgumentParser(description="Generate resume PDF from JSON")
    p.add_argument("--json_input", help="JSON resume file")
    p.add_argument("--output-dir", default=".", help="Output directory")
    p.add_argument("--oneLineEdu", default=True, help="Education section one line T/F")
    args = p.parse_args()

    data = json.load(open(args.json_input, encoding="utf-8"))
    os.makedirs(args.output_dir, exist_ok=True)

    tex = os.path.join(args.output_dir, "resume.tex")
    write_file(generate_tex(data, args.oneLineEdu), tex)

    if not shutil.which("pdflatex"):
        print("Error: pdflatex not found; install MacTeX.", file=sys.stderr)
        sys.exit(1)

    compile_to_pdf(tex, args.output_dir)
    print(f"\nresume.pdf written to {args.output_dir}/resume.pdf")

if __name__ == "__main__":
    main()
