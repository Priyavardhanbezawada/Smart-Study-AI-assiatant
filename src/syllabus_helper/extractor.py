# topic_extractor.py
import re

def extract_topics(text: str) -> list[str]:
    """
    Extracts potential course topics from raw text using regular expressions.
    This pattern looks for lines starting with 'Unit', 'Module', numbers, or bullets.
    """
    pattern = re.compile(
        r"^\s*(?:unit|module|section|part)\s*\d+[:.\s-]*\s*(.+)" 
        r"|^\s*\d+\.\s+([A-Za-z\s,]+)"
        r"|^\s*-\s+([A-Za-z\s,]+)"
        , re.IGNORECASE | re.MULTILINE
    )

    matches = pattern.findall(text)
    topics = [item.strip() for group in matches for item in group if item]
    cleaned_topics = [re.sub(r'[\d\.:-]*$', '', topic).strip() for topic in topics if len(topic.strip()) > 3]

    if not cleaned_topics:
        print("Warning: Could not automatically extract topics. The syllabus format may not be recognized.")
        
    return list(dict.fromkeys(cleaned_topics))
