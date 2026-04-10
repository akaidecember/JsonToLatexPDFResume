"""
Resume Generator from JSON to LaTeX PDF

This script takes a structured JSON file describing a resume and generates a LaTeX
document, then compiles it into a PDF using `pdflatex`.

Author: Anshul Kumar Shandilya
"""

import json, subprocess, shutil, os, argparse, sys, re

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

def format_inline_markup(s: str) -> str:
    """
    Escapes LaTeX-sensitive text and converts markdown-style bold markers to LaTeX.
    Supports patterns like **bold text** anywhere in user-provided strings.
    """
    parts = []
    last_idx = 0

    for match in re.finditer(r"\*\*(.+?)\*\*", s):
        start, end = match.span()
        if start > last_idx:
            parts.append(sanitize_latex(s[last_idx:start]))
        parts.append(rf"\textbf{{{sanitize_latex(match.group(1))}}}")
        last_idx = end

    if last_idx < len(s):
        parts.append(sanitize_latex(s[last_idx:]))

    return "".join(parts)

def generate_tex(data, oneLineEdu, section_order, fullLinks):
    """
    Constructs the LaTeX document as a list of lines using the given resume JSON data.
    Returns a complete LaTeX source string.
    """
    lines = []

    # ==== Preamble ====
    lines += [
        r"\documentclass[11pt]{article}",
        r"\usepackage[top=0.20in, bottom=0.35in, left=0.45in, right=0.45in]{geometry}",
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
    fn  = format_inline_markup(data["full_name"])
    ph  = format_inline_markup(data["phone_number"])
    em  = sanitize_latex(data["email"])
    loc = format_inline_markup(data["location"])

    li  = data.get("linkedin_url", "")
    git = data.get("github_link", "")
    lc  = data.get("leetcode_link", "")

    if li and not li.startswith("http"):
        li = "https://" + li
    if git and not git.startswith("http"):
        git = "https://" + git
    if lc and not lc.startswith("http"):
        lc = "https://" + lc

    def format_header_link(url, label):
        if not url:
            return ""
        display_text = url if fullLinks else label
        return rf" \,\textbar\, \href{{{url}}}{{\underline{{{format_inline_markup(display_text)}}}}}"

    lines += [
        r"\begin{center}",
        rf"  {{\LARGE\bfseries {fn}}}\\[2pt]",
        rf"  {{\small  {ph} \,\textbar\, \href{{mailto:{em}}}{{{{{em}}}}}"
        + format_header_link(li, "LinkedIn")
        + format_header_link(git, "Github")
        + format_header_link(lc, "Leetcode")
        + rf" \,\textbar\, {loc}}}\\[4pt]",
        r"\end{center}",
        r""
    ]

    lines += [r"\vspace{-1pt}"]

    # ==== Summary ====
    if data.get("summary", []):
        lines += [r"\vspace{-5pt}", r"\section{SUMMARY}", r"\noindent"]
        summary_text = format_inline_markup(data.get("summary", ""))
        if summary_text:
            lines += [rf"\small {summary_text}\\[-3pt]"]

    # ==== Sections according to section_order ====
    for section in section_order:
        # EDUCATION
        if section.lower() == "education":
            lines += [r"\vspace{4pt}", r"\section{EDUCATION}", r"\noindent"]
            for edu in data.get("education", []):
                deg     = format_inline_markup(edu["degree"])
                dt      = format_inline_markup(edu["date"])
                un      = format_inline_markup(edu["university"])
                lo      = format_inline_markup(edu["location"])
                courses = ", ".join(format_inline_markup(c) for c in edu.get("courses", []))

                ##### Commented out one liner education 
                if oneLineEdu:
                    lines += [
                        rf"\textbf{{{deg}}} \textbar\ {{{un}}} \textbar\ {{{lo}}} \hfill \textbf{{{dt}}}\\[4pt]",
                        # rf"{un} \hfill {lo}\\[4pt]",
                    ]
                else:
                    lines += [
                        r"\normalsize",
                        rf"\textbf{{{deg}}} \hfill \textbf{{{dt}}}\\[1pt]",
                        rf"\textit{{{un}}} \hfill {lo}\\[1pt]",
                    ]

                if courses:
                    lines += [rf"\small \textbf{{Courses:}} {courses}\\[7pt]",]

            lines += [""]
            lines += [r"\vspace{-9pt}"]

        # SKILLS
        elif section.lower() == "skills":
            lines += [r"\vspace{-3pt}", r"\section{TECHNICAL SKILLS}", r"\noindent"]

            for skill in data.get("skills", []):
                nm  = format_inline_markup(skill["name"])
                val = format_inline_markup(skill["value"])
                lines.append(rf"\small \textbf{{{nm}}}: {val}\\[3pt]")

            lines += [""]

        # EXPERIENCE
        elif section.lower() == "experience":
            lines += [r"\vspace{-6pt}", r"\section{EXPERIENCE}", r"\noindent"]
            for exp in data.get("experience", []):
                ti = format_inline_markup(exp["title"])
                co = format_inline_markup(exp["company"])
                lo = format_inline_markup(exp["location"])
                da = format_inline_markup(exp["date"])

                lines.append(rf"\noindent \textbf{{{{{ti}}} \textbar\ {{{co}}}}} \textbar\ {lo} \hfill \textbf{{{{{da}}}}}\\[-10pt]")
                lines.append(r"\begin{itemize}")

                for desc in exp.get("description", []):
                    lines.append(rf"  \item \small \raggedright {format_inline_markup(desc)}")

                lines.append(r"\end{itemize}")
                lines.append(r"\vspace{10pt}")

        # PROJECTS
        elif section.lower() == "projects":
            if data.get("projects", []):
                lines += [r"\vspace{1pt}", r"\section{PROJECTS}", r"\noindent"]

            for proj in data.get("projects", []):
                tl = format_inline_markup(proj["title"])
                dt = format_inline_markup(proj["date"])
                stk = format_inline_markup(proj["tech_stack"])
                lk = proj.get("link", "")

                if lk and not lk.startswith("http"):
                    lk = "https://" + lk
                if lk:
                    tl = rf"{{{tl}}} \textbar\ \href{{{lk}}}{{\underline{{Link}}}}"

                lines.append(rf"\noindent \textbf{{{tl}}} \textbar\ \textit{{{stk}}} \hfill \textbf{{{dt}}}\\[-8pt]")
                lines.append(r"\begin{itemize}")

                for d in proj.get("description", []):
                    lines.append(rf"  \item \small \raggedright {format_inline_markup(d)}")

                lines.append(r"\end{itemize}")
                lines.append(r"\vspace{4pt}")

        # CERTIFICATES
        elif section.lower() in ("certificates", "certifications", "certification"):
            certs = data.get("certificates", []) or data.get("certifications", [])
            if certs:
                lines += [r"\vspace{5pt}", r"\section{CERTIFICATIONS}", r"\noindent"]

            for certf in certs:
                if isinstance(certf, str):
                    name = format_inline_markup(certf)
                    lk = ""
                else:
                    name = format_inline_markup(certf.get("name", ""))
                    lk = certf.get("link", "")

                if lk and not lk.startswith("http"):
                    lk = "https://" + lk
                if lk:
                    name = rf"\href{{{lk}}}{{\underline{{{name}}}}}"

                lines += [rf"\small {{{name}}}\\[2pt]"]
                    
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
    p.add_argument("--section-order", default="education,skills,experience,projects", help="Comma-separated list of sections in desired order")
    p.add_argument("--full-links", action="store_true", dest="fullLinks", help="Show full URLs in header links")
    args = p.parse_args()

    data = json.load(open(args.json_input, encoding="utf-8"))
    os.makedirs(args.output_dir, exist_ok=True)

    section_order = [s.strip() for s in args.section_order.split(",") if s.strip()]

    tex = os.path.join(args.output_dir, "resume.tex")
    write_file(generate_tex(data, args.oneLineEdu, section_order, args.fullLinks), tex)

    if not shutil.which("pdflatex"):
        print("Error: pdflatex not found; install MacTeX.", file=sys.stderr)
        sys.exit(1)

    compile_to_pdf(tex, args.output_dir)
    print(f"\nresume.pdf written to {args.output_dir}/resume.pdf")

if __name__ == "__main__":
    main()
