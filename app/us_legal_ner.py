import spacy
from spacy.language import Language
from spacy.tokens import Span, Doc
import re
from typing import List, Dict
from app.us_legal_entities import US_LEGAL_ENTITIES

# Load base transformer model
nlp = spacy.load("en_core_web_sm")  # Using small model for faster loading

@Language.component("us_legal_entity_ruler")
def us_legal_entity_ruler(doc: Doc) -> Doc:
    """Extract US-specific legal entities"""
    new_ents = []
    text = doc.text
    
    # Extract US case numbers
    for pattern in US_LEGAL_ENTITIES["CASE_NUMBER"]:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            span = doc.char_span(start, end, label="CASE_NUMBER")
            if span:
                new_ents.append(span)
    
    # Extract US courts
    for pattern in US_LEGAL_ENTITIES["US_COURT"]:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            start, end = match.span()
            span = doc.char_span(start, end, label="US_COURT")
            if span:
                new_ents.append(span)
    
    # Extract US citations
    for pattern in US_LEGAL_ENTITIES["US_CITATION"]:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            span = doc.char_span(start, end, label="US_CITATION")
            if span:
                new_ents.append(span)
    
    # Extract US statutes
    for pattern in US_LEGAL_ENTITIES["US_STATUTE"]:
        for match in re.finditer(pattern, text):
            start, end = match.span()
            span = doc.char_span(start, end, label="US_STATUTE")
            if span:
                new_ents.append(span)
    
    doc.ents = tuple(new_ents) + doc.ents
    return doc

# Add custom component
nlp.add_pipe("us_legal_entity_ruler", before="ner")

def extract_us_legal_metadata(text: str) -> Dict:
    """Extract comprehensive US legal metadata"""
    doc = nlp(text[:100000])  # Process up to 100k chars
    
    metadata = {
        "case_numbers": [],
        "courts": [],
        "citations": [],
        "statutes": [],
        "plaintiffs": [],
        "defendants": [],
        "judges": [],
        "attorneys": [],
        "dates": [],
        "locations": [],
        "organizations": [],
        "case_type": None,
        "jurisdiction": None,
    }
    
    for ent in doc.ents:
        if ent.label_ == "CASE_NUMBER":
            metadata["case_numbers"].append(ent.text)
        elif ent.label_ == "US_COURT":
            metadata["courts"].append(ent.text)
        elif ent.label_ == "US_CITATION":
            metadata["citations"].append(ent.text)
        elif ent.label_ == "US_STATUTE":
            metadata["statutes"].append(ent.text)
        elif ent.label_ == "PERSON":
            context = doc[max(0, ent.start-5):min(len(doc), ent.end+5)].text.lower()
            if any(kw in context for kw in ["plaintiff", "petitioner"]):
                metadata["plaintiffs"].append(ent.text)
            elif any(kw in context for kw in ["defendant", "respondent"]):
                metadata["defendants"].append(ent.text)
            elif any(kw in context for kw in ["judge", "justice", "hon."]):
                metadata["judges"].append(ent.text)
            elif any(kw in context for kw in ["attorney", "counsel", "esq"]):
                metadata["attorneys"].append(ent.text)
        elif ent.label_ == "DATE":
            metadata["dates"].append(ent.text)
        elif ent.label_ == "GPE":
            metadata["locations"].append(ent.text)
        elif ent.label_ == "ORG":
            metadata["organizations"].append(ent.text)
    
    metadata["case_type"] = _determine_case_type(text)
    metadata["jurisdiction"] = _determine_jurisdiction(metadata["courts"])
    
    for key in metadata:
        if isinstance(metadata[key], list):
            metadata[key] = list(set(metadata[key]))
    
    return metadata

def _determine_case_type(text: str) -> str:
    text_lower = text.lower()
    if "bankruptcy" in text_lower:
        return "bankruptcy"
    elif "criminal" in text_lower:
        return "criminal"
    elif "patent" in text_lower:
        return "intellectual_property"
    elif "employment" in text_lower:
        return "employment"
    return "civil"

def _determine_jurisdiction(courts: List[str]) -> str:
    federal_indicators = ["federal", "u.s.", "circuit", "district"]
    for court in courts:
        if any(ind in court.lower() for ind in federal_indicators):
            return "federal"
    return "state"
