"""
US-specific legal entity definitions and patterns
"""

US_LEGAL_ENTITIES = {
    "CASE_NUMBER": [
        r"\d:\d{2}-[a-z]{2,4}-\d{4,6}",  # Federal: 1:23-cv-12345
        r"[A-Z]{2,4}-\d{4}-\d{4,6}",     # State: CV-2023-001234
        r"No\.\s*\d{2,4}-\d{3,5}",       # Docket: No. 23-1234
    ],
    
    "US_COURT": [
        r"United States (District|Court of Appeals|Supreme) Court",
        r"U\.S\. (District|Court of Appeals|Supreme) Court",
        r"\d(st|nd|rd|th) Circuit",
        r"(Northern|Southern|Eastern|Western) District of \w+",
        r"[A-Z]{2,3}DC",
        r"(Supreme|Superior|Circuit|District) Court of \w+",
        r"\w+ Court of Appeals",
    ],
    
    "US_CITATION": [
        r"\d+\s+F\.\s?(2d|3d|4th|Supp\.?\s?2d|Supp\.?\s?3d)\s+\d+",
        r"\d+\s+U\.S\.\s+\d+",
        r"\d+\s+S\.Ct\.\s+\d+",
        r"\d+\s+\w+\.?(App\.)?\s?\d?[dth]{0,3}\s+\d+",
        r"\d{4}\s+WL\s+\d+",
    ],
    
    "US_STATUTE": [
        r"\d+\s+U\.S\.C\.\s+§\s+\d+",
        r"\d+\s+C\.F\.R\.\s+§\s+[\d\.]+",
        r"Pub\.\s?L\.\s?No\.\s?\d+-\d+",
        r"\w+\.\s+(Civ\.|Penal|Bus\.|Health|Educ\.)\s?Code\s+§\s+[\d\.]+",
    ],
}
