import spacy

# Load spaCy model for advanced NLP tasks (optional, used here to show integration)
# We handle the download gracefully if not present
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# A comprehensive predefined list of ML, Data Science, and Software Engineering skills
COMMON_SKILLS = [
    "python", "java", "c++", "c", "javascript", "typescript", "ruby", "php", "go", "rust",
    "sql", "nosql", "mysql", "postgresql", "mongodb", "cassandra", "redis",
    "machine learning", "deep learning", "nlp", "natural language processing", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "spacy", "nltk", "huggingface", "transformers", "sentence transformers",
    "aws", "gcp", "azure", "docker", "kubernetes", "jenkins", "git", "github", "gitlab",
    "linux", "bash", "shell scripting", "data analysis", "data modeling", "statistics",
    "flask", "django", "fastapi", "streamlit", "react", "angular", "vue", "html", "css",
    "hadoop", "spark", "kafka", "airflow", "snowflake", "bigquery", "tableau", "power bi",
    "excel", "agile", "scrum", "mlops", "ci/cd", "rest api", "graphql"
]

def extract_skills(text: str) -> set:
    """
    Extracts potential skills from the given text using keyword matching.
    Returns a set of extracted skills in lowercase.
    """
    text_lower = text.lower()
    extracted_skills = set()
    
    for skill in COMMON_SKILLS:
        # Basic word boundary check could be added, but simple 'in' works decently for tech terms
        # A more robust regex: re.search(rf'\b{re.escape(skill)}\b', text_lower)
        import re
        if re.search(rf'\b{re.escape(skill)}\b', text_lower):
            extracted_skills.add(skill)
            
    return extracted_skills

def match_skills(resume_skills: set, jd_skills: set) -> dict:
    """
    Compares resume skills and Job Description (JD) skills.
    Returns a dictionary of matching and missing skills.
    """
    matching_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills.difference(resume_skills)
    
    return {
        "matching": list(matching_skills),
        "missing": list(missing_skills)
    }
