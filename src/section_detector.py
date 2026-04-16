import re
import logging

logger = logging.getLogger(__name__)

SECTION_PATTERNS = {
    "Facts": [
        r"(?:facts?\s+of\s+the\s+case|brief\s+facts|factual\s+matrix|factual\s+background|prosecution\s+case)",
    ],
    "Issues": [
        r"(?:issue[s]?\s+(?:framed|raised|involved)|question[s]?\s+of\s+law|point[s]?\s+for\s+determination)",
    ],
    "Statutes": [
        r"(?:section\s+\d+[A-Z]?\s+(?:of\s+)?(?:IPC|CrPC|CPC|Constitution|Act))",
    ],
    "Arguments": [
        r"(?:learned\s+counsel|submissions?\s+of|contended\s+that|argued\s+that|appellant\s+contends)",
    ],
    "Decision": [
        r"(?:appeal\s+is\s+(?:dismissed|allowed)|petition\s+is\s+(?:accepted|rejected|dismissed|allowed)|order(?:ed)?\s+accordingly|disposed\s+of|conviction\s+is\s+(?:upheld|set\s+aside)|acquitted|sentenced)",
    ]
}


def detect_sections(text):
    if not text:
        return {"Facts": "", "Issues": "", "Statutes": "", "Arguments": "", "Decision": ""}

    sections = {}

    sections["Facts"] = _extract_section(
        text,
        r"(?:facts?\s+of\s+the\s+case|brief\s+facts|factual\s+matrix)",
        r"(?:issue[s]?\s+framed|submissions?|decision|judgment|arguments?)"
    )

    if not sections["Facts"]:
        sentences = text.split(".")
        fact_sentences = []
        for s in sentences[:10]:
            if any(kw in s.lower() for kw in ["case", "prosecution", "accused", "appellant", "petitioner", "respondent"]):
                fact_sentences.append(s.strip())
        sections["Facts"] = ". ".join(fact_sentences[:5])

    sections["Issues"] = _extract_section(
        text,
        r"(?:issue[s]?\s+framed|question[s]?\s+of\s+law|point[s]?\s+for\s+determination)",
        r"(?:decision|judgment|submission|argument)"
    )

    statute_matches = re.findall(
        r"Section\s+\d+[A-Z]?\s+(?:of\s+)?(?:the\s+)?(?:Indian\s+Penal\s+Code|IPC|CrPC|CPC|Constitution|"
        r"NI\s+Act|NDPS\s+Act|IT\s+Act|Hindu\s+(?:Marriage|Succession)\s+Act|Motor\s+Vehicles?\s+Act|"
        r"National\s+Security\s+Act|Representation\s+of\s+People\s+Act|Income\s+Tax\s+Act|"
        r"Negotiable\s+Instruments?\s+Act|Prevention\s+of\s+Illicit\s+Traffic|Evidence\s+Act)",
        text, re.IGNORECASE
    )

    if not statute_matches:
        statute_matches = re.findall(r"Section\s+\d+[A-Z]?\s+\w+", text, re.IGNORECASE)

    sections["Statutes"] = list(set(statute_matches))

    sections["Arguments"] = _extract_section(
        text,
        r"(?:learned\s+counsel|submissions?\s+of|contended\s+that)",
        r"(?:decision|judgment|this\s+court\s+(?:finds|holds|observes))"
    )

    decision_patterns = [
        r"(appeal\s+is\s+(?:dismissed|allowed)[\.\s])",
        r"(petition\s+is\s+(?:accepted|rejected|dismissed|allowed)[\.\s])",
        r"(conviction\s+is\s+(?:upheld|set\s+aside|confirmed)[\.\s])",
        r"(accused\s+is\s+(?:acquitted|convicted)[\.\s])",
        r"(decree\s+(?:for\s+\w+\s+)?is\s+(?:granted|decreed|dismissed)[\.\s])",
        r"(claim\s+petition\s+is\s+(?:allowed|dismissed)[\.\s])",
        r"(writ\s+petition\s+is\s+(?:dismissed|allowed)[\.\s])",
        r"(detenue?\s+is\s+directed\s+to\s+be\s+released[\.\s])",
    ]

    decision_text = ""
    for pattern in decision_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            decision_text = match.group(1).strip()
            break

    sections["Decision"] = decision_text

    return sections


def _extract_section(text, start_pattern, end_pattern):
    match = re.search(f"{start_pattern}(.*?){end_pattern}", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()[:500]
    return ""


def extract_statute_codes(text):
    codes = []
    pattern = r"Section\s+(\d+[A-Z]?)\s+(?:of\s+)?(?:the\s+)?(\w[\w\s]*?)(?:\.|,|\s+and\s+|\s+read)"

    for match in re.finditer(pattern, text, re.IGNORECASE):
        section_num = match.group(1)
        act_name = match.group(2).strip()
        codes.append({"section": section_num, "act": act_name})

    if not codes:
        simple_pattern = r"Section\s+(\d+[A-Z]?)\s+(\w+)"
        for match in re.finditer(simple_pattern, text, re.IGNORECASE):
            codes.append({"section": match.group(1), "act": match.group(2)})

    return codes