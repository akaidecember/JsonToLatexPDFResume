import json, subprocess, shutil, os, argparse, sys

def sanitize_latex(s: str) -> str:
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

def generate_tex(data):
    lines = []

    # Preamble
    lines += [
        r"\documentclass[11pt]{article}",
        r"\usepackage[top=0.25in, bottom=0.4in, left=0.4in, right=0.4in]{geometry}",
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

    # Header
    fn  = sanitize_latex(data["full_name"])
    ph  = sanitize_latex(data["phone_number"])
    em  = sanitize_latex(data["email"])
    loc = sanitize_latex(data["location"])
    li  = data.get("linkedin_url", "")
    short_li = sanitize_latex(li.split("://")[-1]) if li else ""

    lines += [
        r"\begin{center}",
        rf"  {{\LARGE\bfseries {fn}}}\\[2pt]",
        rf"  {{\small  {ph} \,\textbar\, \href{{mailto:{em}}}{{{em}}}"
        + (rf" \,\textbar\, \href{{{li}}}{{{short_li}}}" if li else "")
        + rf" \,\textbar\, {loc}}}\\[4pt]",
        r"\end{center}",
        r""
    ]

    # Education
    lines += [r"\vspace{-5pt}", r"\section{EDUCATION}", r"\noindent"]
    for edu in data.get("education", []):
        deg = sanitize_latex(edu["degree"])
        dt  = sanitize_latex(edu["date"])
        un  = sanitize_latex(edu["university"])
        lo  = sanitize_latex(edu["location"])
        courses = ", ".join(sanitize_latex(c) for c in edu.get("courses", []))
        lines += [
            rf"\textbf{{{deg}}} \hfill {dt}\\",
            rf"{un} \hfill {lo}\\[4pt]",
            rf"\small \textbf{{Courses:}} {courses}\\[4pt]",
        ]
    lines += [""]

    # Technical Skills
    lines += [r"\vspace{-5pt}", r"\section{TECHNICAL SKILLS}", r"\noindent"]
    for skill in data.get("skills", []):
        nm  = sanitize_latex(skill["name"])
        val = sanitize_latex(skill["value"])
        lines.append(rf"\small \textbf{{{nm}}}: {val}\\")
    lines += [""]

    # Experience
    lines += [r"\vspace{-5pt}", r"\section{EXPERIENCE}", r"\noindent"]
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

    # Projects
    lines += [r"\vspace{5pt}", r"\section{PROJECTS}", r"\noindent"]
    for proj in data.get("projects", []):
        tl = sanitize_latex(proj["title"])
        dt = sanitize_latex(proj["date"])
        lk = proj.get("link","")
        if lk:
            tl += rf" \href{{{lk}}}{{\scriptsize\faExternalLink}}"
        lines.append(rf"\noindent \textbf{{{tl}}} \hfill \textbf{{{dt}}}\\[-12pt]")
        lines.append(r"\begin{itemize}")
        for d in proj.get("description", []):
            lines.append(rf"  \item \small \raggedright {sanitize_latex(d)}")
        lines.append(r"\end{itemize}")
        lines.append(r"\vspace{4pt}")

    lines.append(r"\end{document}")
    return "\n".join(lines)


def write_file(txt, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)

def compile_to_pdf(tex_path, out_dir):
    for _ in range(2):
        subprocess.run(
            ["pdflatex","-interaction=nonstopmode","-output-directory",out_dir,tex_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

def main():
    p = argparse.ArgumentParser(description="Generate resume PDF from JSON")
    p.add_argument("json_input", help="JSON resume file")
    p.add_argument("--output-dir", default=".", help="Output directory")
    args = p.parse_args()

    data = json.load(open(args.json_input, encoding="utf-8"))
    os.makedirs(args.output_dir, exist_ok=True)
    tex = os.path.join(args.output_dir, "resume.tex")
    write_file(generate_tex(data), tex)

    if not shutil.which("pdflatex"):
        print("Error: pdflatex not found; install MacTeX.", file=sys.stderr)
        sys.exit(1)

    compile_to_pdf(tex, args.output_dir)
    print(f"\nresume.pdf written to {args.output_dir}/resume.pdf")

if __name__ == "__main__":
    main()
