import re
import os

INPUT_FILE = r"C:\Users\Shreesh\Documents\UIDAI-Migration_Prediction_System\HACKATHON_REPORT.md"
OUTPUT_FILE = r"C:\Users\Shreesh\Documents\UIDAI-Migration_Prediction_System\outputs\Final_Hackathon_Report.tex"
PROJECT_ROOT = r"C:\Users\Shreesh\Documents\UIDAI-Migration_Prediction_System"

def sanitize_unicode(text):
    # Global replacement of problematic unicode
    replacements = {
        '₹': 'Rs. ',
        '≤': r'$\le$', '≥': r'$\ge$', '≠': r'$\neq$',
        '–': '-', '—': '-',
        '“': "``", '”': "''", '’': "'", '‘': "`",
        # Box drawing - critical to fix verbatim errors
        '├': '+', '─': '-', '└': '+', '│': '|', '┌': '+', '┐': '+', '┘': '+',
        '…': '...',
        'ε': r'$\epsilon$', 'σ': r'$\sigma$'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def escape_latex_text(text):
    # Escapes reserved chars in normal text
    chars = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', 
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\^{}', '\\': r'\textbackslash{}',
        '|': r'\textbar{}'
    }
    # We must escape logic that introduces backslashes first? 
    # Actually, simpler: just iterate and replace.
    res = ""
    for c in text:
        if c in chars:
            res += chars[c]
        else:
            res += c
    return res

def process_inline_formatting(text):
    # 1. Protect Inline Code: `code`
    # Replace with placeholders
    code_map = {}
    
    def code_repl(match):
        uid = f"CODE_{len(code_map)}_"
        # Content inside inline code needs to be escaped for latex special chars too,
        # otherwise `_` in code becomes subscript or error if not in math mode,
        # BUT \texttt{} handles most things. However, special chars like %, #, & still break \texttt.
        # So we MUST escape them.
        content = match.group(1)
        content_escaped = escape_latex_text(content)
        code_map[uid] = r'\texttt{' + content_escaped + '}'
        return uid
        
    text = re.sub(r'`([^`]+)`', code_repl, text)
    
    # 2. Escape valid text now (so we don't escape formatting commands we are about to add)
    text = escape_latex_text(text)
    
    # Restore identifiers for inline code (they don't need further escaping or formatting)
    for uid, latex_code in code_map.items():
        text = text.replace(escape_latex_text(uid), latex_code) # Note: uid might have chars escaped? uid is safe ASCII "CODE_0_"
        
    # 3. Apply formatting regex on the ESCAPED text
    # Bold: **content** -> \textbf{content} (Note: * was NOT escaped)
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    
    # Italic: _content_  (mapped to \\_content\\_) or *content* (mapped to \\*content\\*)
    # Use word boundaries for underscore to avoid variables: \b\\_ matches escaped underscore at boundary?
    # Actually, after escaping, '_' becomes '\_'.
    # \_text\_ -> \textit{text}
    text = re.sub(r'(^|[\s])\\_(.+?)\\_(?=[\s]|[.,;!?]|$)', r'\1\\textit{\2}', text)
    
    # 4. Allow breaking at slashes (fixes table overflow)
    text = text.replace('/', r'/\allowbreak ')

    return text

def convert_md_to_latex(md_content):
    # 1. Global Sanitize
    md_content = sanitize_unicode(md_content)
    
    lines = md_content.split('\n')
    latex_lines = []
    
    # Preamble (Optimized for Overleaf)
    latex_lines.append(r'''\documentclass[11pt, a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{graphicx}
\usepackage[margin=2.5cm]{geometry}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{float}
\usepackage{listings}
\usepackage{microtype}
\usepackage{setspace}

% Standardize line spacing
\onehalfspacing

% Define ragged-right X column to prevent ugly full justification in narrow columns
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}

% Unicode Fallbacks (Robustness)
\DeclareUnicodeCharacter{03B5}{\ensuremath{\epsilon}}
\DeclareUnicodeCharacter{03C3}{\ensuremath{\sigma}}

% Prevent vertical justification issues
\raggedbottom

% Color Definitions
\definecolor{DarkOrange}{RGB}{204, 85, 0} % Formal "Neon" Orange
\definecolor{CodeBg}{RGB}{245, 245, 245}

% listings Config
\lstset{
  basicstyle=\ttfamily\small,
  backgroundcolor=\color{CodeBg},
  frame=single,
  rulecolor=\color{gray},
  breaklines=true,
  postbreak=\mbox{\textcolor{red}{$\hookrightarrow$}\space},
  aboveskip=1.5em,
  belowskip=1.5em,
  showstringspaces=false,
  columns=fullflexible,
  literate={×}{{$\times$}}1 {ε}{{\ensuremath{\epsilon}}}1 {σ}{{\ensuremath{\sigma}}}1 {₹}{{Rs. }}1 {≤}{{$\le$}}1 {≥}{{$\ge$}}1 {≠}{{$\neq$}}1
}

% Header/Footer
\setlength{\headheight}{15pt}

\hypersetup{
    colorlinks=true,
    linkcolor=DarkOrange, 
    urlcolor=blue,
    pdftitle={UIDAI Migration Analysis Report},
    pdfauthor={Team AlgoQX}
}
\pagestyle{fancy}
\fancyhf{}
\lhead{UIDAI Analysis}
\rhead{\thepage}

\title{\textbf{\Large The Proactive-Reactive Divide: \\[0.5em] \large Behavioral Analysis of Aadhaar Update Patterns Across Indian Districts}}
\author{Team AlgoQX}
\date{\today}

\begin{document}
\UseRawInputEncoding
\maketitle
\thispagestyle{empty}
\clearpage

% Acknowledgements with ToC entry
\phantomsection
\addcontentsline{toc}{section}{Acknowledgments}
{{ACKNOWLEDGEMENTS}}

\tableofcontents
\clearpage

\phantomsection
\addcontentsline{toc}{section}{List of Figures}
\listoffigures
\clearpage

\phantomsection
\addcontentsline{toc}{section}{List of Tables}
\listoftables
\clearpage
''')

    in_code_block = False
    in_table = False
    table_buffer = []

    # Acknowledgement Extraction State
    ack_buffer = []
    in_ack = False
    ack_content = ""

    for line in lines:
        stripped = line.strip()
        
        # 0. Acknowledgements Extraction
        if re.search(r'^##.*ACKNOWLEDGMENTS', stripped, re.IGNORECASE):
            in_ack = True
            continue 
            
        if in_ack:
            if stripped.startswith('#') or stripped == '---':
                in_ack = False
                ack_content = "\n".join([process_inline_formatting(l) for l in ack_buffer])
            else:
                ack_buffer.append(line)
                continue

        # 4. Code Blocks (Listings with Border)
        if stripped.startswith('```'):
            if in_code_block:
                latex_lines.append(r'\end{lstlisting}')
                in_code_block = False
            else:
                latex_lines.append(r'\begin{lstlisting}')
                in_code_block = True
            continue
            
        if in_code_block:
            latex_lines.append(line)
            continue
            
        # 5. Tables
        if stripped.startswith('|'):
            if not in_table:
                in_table = True
                table_buffer = []
            
            if '---' in stripped:
                continue 
            
            raw_cells = [c.strip() for c in stripped.strip('|').split('|')]
            table_buffer.append(raw_cells)
            continue
            
        # End Table
        if in_table and not stripped.startswith('|'):
            if table_buffer:
                num_cols = len(table_buffer[0])
                # Add spacing before table
                latex_lines.append(r'\vspace{0.8em}')
                latex_lines.append(r'{\small')
                latex_lines.append(r'\begin{tabularx}{\textwidth}{|' + ('Y|' * num_cols) + '}')
                latex_lines.append(r'\hline')
                
                header_row = table_buffer[0]
                header_tex = [r'\textbf{' + process_inline_formatting(c) + '}' for c in header_row]
                latex_lines.append(" & ".join(header_tex) + r' \\ \hline')
                
                for row in table_buffer[1:]:
                    if len(row) < num_cols:
                        row = row + [''] * (num_cols - len(row))
                    elif len(row) > num_cols:
                         row = row[:num_cols]
                         
                    row_tex = [process_inline_formatting(c) for c in row]
                    latex_lines.append(" & ".join(row_tex) + r' \\ \hline')
                    
                latex_lines.append(r'\end{tabularx}')
                latex_lines.append(r'}')
                latex_lines.append(r'\vspace{1em}')
            in_table = False
            table_buffer = []

        # 6. Headers
        header_match = re.search(r'^(#+)\s+(\d+\.\s*)?(.*)', stripped)
        if header_match:
            level = len(header_match.group(1))
            title = header_match.group(3)
            title_tex = process_inline_formatting(title)
            
            is_special = any(x in title.upper() for x in ['REFERENCES', 'ACKNOWLEDGMENTS', 'APPENDIX'])
            
            # Since we extract Acknowledgements manually, we might still hit the header if logic above fails or for others
            # But if 'in_ack' logic works, the lines are skipped. 
            # The 'ACKNOWLEDGMENTS' in this list handles the case where it wasn't caught or needs specific handling if not skipped.
            # But we skip it. So effectively only References and Appendix use this.
            
            cmd = "section"
            if level == 2: cmd = "subsection"
            elif level == 3: cmd = "subsubsection"
            elif level == 4: cmd = "paragraph"
            
            if is_special:
                 latex_lines.append(r'\clearpage')
                 latex_lines.append("\\" + cmd + '*{' + title_tex + '}')
                 latex_lines.append(r'\addcontentsline{toc}{' + cmd + '}{' + title_tex + '}')
            else:
                 if cmd == "section":
                     latex_lines.append(r'\clearpage')
                 latex_lines.append("\\" + cmd + '{' + title_tex + '}')
                 
        # 7. Images
        elif stripped.startswith('![') and '](' in line:
            match = re.search(r'!\[(.*?)\]\((.*?)\)', line)
            if match:
                alt = process_inline_formatting(match.group(1))
                path = match.group(2)
                match_path = path.replace('\\', '/')
                latex_lines.append(r'\begin{figure}[H]\centering')
                latex_lines.append(r'\includegraphics[width=0.85\textwidth, keepaspectratio]{' + match_path + '}')
                latex_lines.append(r'\caption{' + alt + '}')
                latex_lines.append(r'\end{figure}')
                
        # 8. Lists
        elif stripped.startswith('- '):
            content = process_inline_formatting(stripped[2:])
            latex_lines.append(r'\begin{itemize}')
            latex_lines.append(r'\item ' + content)
            latex_lines.append(r'\end{itemize}')
            
        # 9. Normal Text
        elif stripped == '---':
            latex_lines.append(r'\noindent\rule{\textwidth}{0.5pt}')
        elif stripped:
            latex_lines.append(process_inline_formatting(stripped) + '\n')
        else:
             # Just a blank line for natural paragraph break (handled by setspace/latex)
            latex_lines.append('')

    latex_lines.append(r'\end{document}')
    
    # Process buffer if EOF
    if in_ack:
        ack_content = "\n".join([process_inline_formatting(l) for l in ack_buffer])
    
    final = "\n".join(latex_lines)
    
    # Inject Acknowledgements
    if ack_content:
        # Format explicitly
        ack_latex = r'\section*{Acknowledgments}' + '\n' + ack_content + r'\clearpage'
        final = final.replace('{{ACKNOWLEDGEMENTS}}', ack_latex)
    else:
        final = final.replace('{{ACKNOWLEDGEMENTS}}', '')

    final = final.replace(r"\end{itemize}" + "\n" + r"\begin{itemize}", "")
    
    return final

def main():
    print("Reading Markdown...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        md = f.read()
    
    print("Converting to LaTeX...")
    tex = convert_md_to_latex(md)
    
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(tex)
    
    print("Done.")

if __name__ == "__main__":
    main()
