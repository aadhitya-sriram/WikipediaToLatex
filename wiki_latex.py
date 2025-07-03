import requests
import pypandoc
import re
import os

class WikipediaToLatexConverter:

    def __init__(self):
        self.latex_symbol_pattern = r'(?<!\\\()\\(neq|eq|leq|geq|in|notin|subset|supset|to|approx|sim|times|cdot|pm|mp|div|cap|cup|land|lor|Rightarrow|Leftarrow|iff|implies|dots|ldots|cdots|vdots|ddots)(?![^\\]*(\\\)|\]))'
        self.latex_fixes = {
            r'\\tightlist': '',
            r'\\R': r'R',
            r'\\emph\{y\}': r'y',
        }
        self.unicode_math_symbols = {
            '−': '-',            # minus
            '×': r'\\times',
            '÷': r'\\div',
            '±': r'\\pm',
            '∓': r'\\mp',
            '≠': r'\\neq',
            '≤': r'\\leq',
            '≥': r'\\geq',
            '≈': r'\\approx',
            '≡': r'\\equiv',
            '∑': r'\\sum',
            '∏': r'\\prod',
            '∫': r'\\int',
            '∞': r'\\infty',
            '∂': r'\\partial',
            '∇': r'\\nabla',
            '∃': r'\\exists',
            '∀': r'\\forall',
            '∈': r'\\in',
            '∉': r'\\notin',
            '∅': r'\\emptyset',
            '∧': r'\\wedge',
            '∨': r'\\vee',
            '⊂': r'\\subset',
            '⊃': r'\\supset',
            '⊆': r'\\subseteq',
            '⊇': r'\\supseteq',
            '→': r'\\to',
            '←': r'\\leftarrow',
            '⇔': r'\\Leftrightarrow',
            '⇒': r'\\Rightarrow',
            'θ': r'\\theta',
            'λ': r'\\lambda',
            'μ': r'\\mu',
            'π': r'\\pi',
            'φ': r'\\phi',
            '∠': r'\\angle',
            # '°': r'^\\circ',
        }

    def get_raw_wikitext(self, title):
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "rvprop": "content",
            "titles": title,
            "formatversion": 2
        }
        response = requests.get(url, params=params)
        page = response.json()['query']['pages'][0]
        return page['revisions'][0]['content'] if 'revisions' in page else ""

    def convert_wikitext_to_latex(self, wikitext):
        return pypandoc.convert_text(wikitext, to='latex', format='mediawiki')

    def remove_see_also_and_beyond(self, latex: str) -> str:
        """
        Strip out the 'See also' subsection and everything that follows.
        """
        pattern = re.compile(
            r'\\subsection\{See also\}\\label\{see_also\}.*\Z',
            re.DOTALL
        )
        return pattern.sub('', latex)
    
    def phase1_math_cleaning(self, text: str) -> str:
        text = re.sub(r"\{\{mvar\|([^}]+)\}\}", r"\1", text)
        text = re.sub(r"<sub>([^<]+)</sub>", r"_{\1}", text)
        text = re.sub(r"<sup>([^<]+)</sup>", r"^{\1}", text)
        text = re.sub(r"''([^']+)''", r"\1", text)
        text = re.sub(r"\{\{math\|1=(.*?)\}\}", lambda m: f":<math>{m.group(1).strip()}</math>", text)
        text = re.sub(r"\{\{math\|([^=][^}]*)\}\}", lambda m: f":<math>{m.group(1).strip()}</math>", text)
        # text = re.sub(r'(<math>.*?)(</math>)\s*}}', lambda m: m.group(1) + "}}" + m.group(2), text)
        text = re.sub(r"cokernel", "", text)
        return text

    def phase1_cleaning(self, text: str) -> str:
        text = self.phase1_math_cleaning(text)
        text = re.sub(r"\{\{(.*?)\}\}", "", text)
        text = re.sub(r"\{\{visible anchor\|[^|}]+\|text=([^}]+)\}\}",r"\1",text)
        text = re.sub(r"\{\{visible anchor\|[^|}]+\|([^}]+)\}\}",r"\1",text)
        text = re.sub(r"'''(.+?)'''", r"\1", text)
        text = re.sub(r"\{\{em\|(.+?)\}\}", r"\1", text)
        text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
        text = re.sub(r"<ref(?:\s+name=\"[^\"]*\")?>.*?</ref>", "", text)
        text = re.sub(r"\(([^()|]+)\)\|([a-zA-Z]+)(?=\W|$)", "", text)
        text = re.sub(r"[^#|\s]+#[^|\s]+\|", "", text)
        text = re.sub(r"(?:[^\s#|]+|\([^)]+\))#[^|\n]+\|", "", text)
        text = re.sub(r'Image:.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n+', '\n', text).strip()

        return text

    def wrap_latex_symbol(self, match):
        return r"\(" + "\\" + match.group(1) + r"\)"

    def inject_math(self, text: str) -> str:
        text = re.sub(r"\\\(\s*\\begin{align}(.*?)\\end{align}\s*\\\)", r"\\[\n\\begin{aligned}\1\\end{aligned}\n\\]", text, flags=re.DOTALL)
        text = re.sub(r"([a-zA-Z])\\_\\\{([^}]+)\\\}", r"\\(\1_{\2}\\)", text)
        text = re.sub(r"\\mapsto", r"\\to", text)
        text = re.sub(r"\bR\^(\^{0,1}\\?[a-zA-Z0-9+−\-∞]+)(?!\})", r"\\(R^{\1}\\)", text)
        text = re.sub(self.latex_symbol_pattern, self.wrap_latex_symbol, text)
        return text

    def clean_latex_output(self, latex: str) -> str:
        for pattern, repl in self.unicode_math_symbols.items():
            latex = re.sub(pattern, '\('+repl+'\)', latex)
        
        for pattern, repl in self.latex_fixes.items():
            latex = re.sub(pattern, repl, latex)

        latex = re.sub(r'\\footnote\{.*?\}', '', latex, flags=re.DOTALL)
        latex = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', latex)
        latex = re.sub(r'\\url\{[^}]*\}', '', latex)
        latex = re.sub(r'\\includegraphics(\[.*?\])?\{.*?\}', '', latex)
        latex = re.sub(r'\\includesvg(\[.*?\])?\{.*?\}', '', latex)
        latex = re.sub(r'\\caption\{([^}]*)\}', r'\\paragraph{\1}', latex)
        latex = re.sub(r'\|[-|]*', '', latex)
        latex = re.sub(r'style="[^"]*"', '', latex)
        latex = re.sub(r'\{[^\}]*width[^}]*\}', '', latex)
        latex = re.sub(r'\{\s*\}', '', latex)
        latex = re.sub(r'\\\[\\\]', '', latex)
        latex = self.remove_see_also_and_beyond(latex)

        latex = re.sub(r"\\textquotesingle R\\textquotesingle\\\^\\{([^{}]+)\\}", r"R^\1", latex)
        latex = re.sub(r"\\textquotesingle R\\textquotesingle", r"R", latex)
        latex = re.sub(r"\\textquotesingle", r"", latex)

        latex = self.inject_math(latex)

        lines = latex.splitlines()
        cleaned_lines = []
        buffer = ""
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if buffer:
                    cleaned_lines.append(buffer.strip())
                    buffer = ""
                cleaned_lines.append("")
            elif stripped.startswith("\\") and not stripped.startswith("\\ "):
                if buffer:
                    cleaned_lines.append(buffer.strip())
                    buffer = ""
                cleaned_lines.append(stripped)
            else:
                buffer += (" " + stripped)
        if buffer:
            cleaned_lines.append(buffer.strip())

        return "\n".join(cleaned_lines)

    def build_latex_document(self, title, body):
        return f"""
\\documentclass[12pt]{{article}}
\\usepackage{{amsmath, amssymb}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{lmodern}}
\\title{{{title}}}
\\begin{{document}}
\\maketitle

{body}

\\end{{document}}
""".strip()

    def save_latex(self, title, latex_code, output_dir="wikipedia/outputs"):
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, f"{title.replace(' ', '_')}.tex")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(latex_code)
        print(f"LaTeX saved to: {file_path}")

    def wikipedia_to_clean_latex(self, title):
        print(f"Latex Processing: {title}")
        wikitext = self.get_raw_wikitext(title)
        if not wikitext:
            raise ValueError("No data returned")
        wikitext = self.phase1_cleaning(wikitext)
        latex = self.convert_wikitext_to_latex(wikitext)
        latex = self.clean_latex_output(latex)
        full_doc = self.build_latex_document(title, latex)
        return full_doc












# if __name__ == "__main__":
#     wiki = WikipediaToLatexConverter()
#     wiki_text = wiki.wikipedia_to_clean_latex("Scalar multiplication")

    # import wikipedia
    # with (open("linear_map.txt", "w", encoding="utf-8") as f):
    #     f.write(wikipedia.page("Linear map").content)

    # samples = [
    #     "{{mvar|T}}",
    #     "{{math|1=ker ''T'' = {0<sub>''V''</sub>} }}",
    #     "{{math|1=dim(ker ''T'') = 0}}",
    #     "{{math|1=cokernel|coker ''T'' = {0<sub>''W''</sub>} }}",
    #     "{{math|''T'': ''V'' → ''V''}}",
    #     "{{math|1=''T''<sup>2</sup> = ''T''}}",
    #     "{{math|1=''T'' = ''kI''}}",
    #     "{{math|1=''RT'' = ''ST''}}",
    #     "{{math|1=''R'' = ''S''}}",
    # ]
    # for s in samples:
    #     print(wiki.convert_wiki_math_to_html(s))

    # print(wiki.phase1_cleaning(r"{{visible anchor|Label|text=Target}}"))
    # print(wiki.phase1_cleaning(r"{{visible anchor|Label|Target}}"))
    # print(wiki.phase1_cleaning("[[text]]"))

    # print(wiki.phase1_cleaning("<ref>text</ref>"))
    # print(wiki.phase1_cleaning("{{em|{{visible anchor|extendingkkkk by linearity|extend by linearity}}}}"))
    # print(wiki.phase1_cleaning("'''text'''"))

    # lraw = wiki.convert_wikitext_to_latex(raw)

    # html_output = pypandoc.convert_text(wiki_text, format='mediawiki', to='html')
    # latex_output = pypandoc.convert_text(html_output, format='html', to='latex')
    # full_doc = wiki.build_latex_document("Linear map", latex_output)
    # wiki.save_latex("Linear map", full_doc)

    # print(latex_output)

#     input_text = r"""
# ===Monomorphism===
# <math>T</math> is said to be \textit{[[injective]]} or a \textit{[[monomorphism]]} if any of the following equivalent conditions are true:
# # <math>T</math> is [[injective|one-to-one]] as a map of [[set (mathematics)|sets]].
# # <math>\ker \textit{T} = \{0_{\textit{V}}\}</math>
# # <math>\dim(\ker \textit{T}) = 0</math>
#     """
#     print(pypandoc.convert_text(input_text, format='mediawiki', to='latex'))








