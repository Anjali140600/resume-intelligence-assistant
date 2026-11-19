import re


# Canonical skills and common ways employers/candidates write them. Aliases let
# the comparison recognize equivalent spellings instead of requiring exact text.
SKILL_ALIASES = {
    # Programming languages
    "python": ["python"], "java": ["java"], "c++": ["c++"], "c": ["c"],
    "c#": ["c#", "c sharp"], "javascript": ["javascript", "java script"],
    "typescript": ["typescript", "type script"], "go": ["golang", "go"],
    "rust": ["rust"], "ruby": ["ruby"], "php": ["php"], "r": ["r language"],
    "scala": ["scala"], "kotlin": ["kotlin"], "swift": ["swift"],
    # Data, AI and analytics
    "machine learning": ["machine learning", "ml models"],
    "deep learning": ["deep learning", "neural networks"],
    "natural language processing": ["natural language processing", "nlp"],
    "computer vision": ["computer vision", "image recognition"],
    "generative ai": ["generative ai", "genai", "gen ai"],
    "large language models": ["large language models", "large language model", "llms", "llm"],
    "prompt engineering": ["prompt engineering", "prompt design"],
    "rag": ["retrieval augmented generation", "rag"],
    "tensorflow": ["tensorflow"], "pytorch": ["pytorch", "torch"], "keras": ["keras"],
    "scikit-learn": ["scikit-learn", "sklearn"], "pandas": ["pandas"],
    "numpy": ["numpy"], "scipy": ["scipy"], "matplotlib": ["matplotlib"],
    "seaborn": ["seaborn"], "spacy": ["spacy"], "nltk": ["nltk"],
    "hugging face": ["hugging face", "huggingface"], "transformers": ["transformers"],
    "data analysis": ["data analysis", "data analytics"],
    "data science": ["data science"], "statistics": ["statistics", "statistical analysis"],
    "a/b testing": ["a/b testing", "ab testing"], "time series": ["time series"],
    "feature engineering": ["feature engineering"], "model deployment": ["model deployment"],
    "mlops": ["mlops", "ml ops"], "etl": ["etl", "extract transform load"],
    "data engineering": ["data engineering"], "data modeling": ["data modeling", "data modelling"],
    # Databases and big data
    "sql": ["sql"], "nosql": ["nosql", "no sql"], "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"], "sql server": ["sql server", "mssql"],
    "oracle": ["oracle database", "oracle db"], "mongodb": ["mongodb", "mongo db"],
    "cassandra": ["cassandra"], "redis": ["redis"], "dynamodb": ["dynamodb"],
    "elasticsearch": ["elasticsearch", "elastic search"], "neo4j": ["neo4j"],
    "hadoop": ["hadoop"], "spark": ["apache spark", "pyspark", "spark"],
    "kafka": ["apache kafka", "kafka"], "airflow": ["apache airflow", "airflow"],
    "snowflake": ["snowflake"], "bigquery": ["bigquery", "big query"],
    "databricks": ["databricks"], "dbt": ["dbt"],
    # Cloud and DevOps
    "aws": ["amazon web services", "aws"], "azure": ["microsoft azure", "azure"],
    "gcp": ["google cloud platform", "google cloud", "gcp"],
    "docker": ["docker"], "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"], "ansible": ["ansible"], "jenkins": ["jenkins"],
    "github actions": ["github actions"], "gitlab ci": ["gitlab ci"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous delivery", "continuous deployment"],
    "linux": ["linux"], "bash": ["bash"], "shell scripting": ["shell scripting", "shell scripts"],
    "git": ["git"], "github": ["github"], "gitlab": ["gitlab"],
    "monitoring": ["monitoring", "observability"], "prometheus": ["prometheus"],
    "grafana": ["grafana"],
    # Backend, frontend and APIs
    "flask": ["flask"], "django": ["django"], "fastapi": ["fastapi", "fast api"],
    "spring boot": ["spring boot"], ".net": [".net", "dotnet"],
    "node.js": ["node.js", "nodejs", "node js"], "express.js": ["express.js", "expressjs"],
    "streamlit": ["streamlit"], "react": ["react.js", "reactjs", "react"],
    "angular": ["angular"], "vue": ["vue.js", "vuejs", "vue"],
    "next.js": ["next.js", "nextjs", "next js"], "html": ["html", "html5"],
    "css": ["css", "css3"], "bootstrap": ["bootstrap"], "tailwind css": ["tailwind css", "tailwind"],
    "rest api": ["rest api", "rest apis", "restful api", "restful apis", "restful services"],
    "graphql": ["graphql"], "microservices": ["microservices", "micro services"],
    # BI, delivery, quality and security
    "tableau": ["tableau"], "power bi": ["power bi", "powerbi"],
    "excel": ["microsoft excel", "ms excel", "excel"], "looker": ["looker"],
    "agile": ["agile"], "scrum": ["scrum"], "jira": ["jira"],
    "project management": ["project management"], "stakeholder management": ["stakeholder management"],
    "communication": ["communication skills", "written communication", "verbal communication"],
    "leadership": ["leadership", "team leadership"], "problem solving": ["problem solving"],
    "unit testing": ["unit testing", "unit tests"], "pytest": ["pytest"],
    "selenium": ["selenium"], "junit": ["junit"], "test automation": ["test automation"],
    "cybersecurity": ["cybersecurity", "cyber security"], "oauth": ["oauth", "oauth2"],
}


SKILL_CATEGORIES = {
    "Programming": {"python", "java", "c++", "c", "c#", "javascript", "typescript", "go", "rust", "ruby", "php", "r", "scala", "kotlin", "swift"},
    "AI & Data": {"machine learning", "deep learning", "natural language processing", "computer vision", "generative ai", "large language models", "prompt engineering", "rag", "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "scipy", "matplotlib", "seaborn", "spacy", "nltk", "hugging face", "transformers", "data analysis", "data science", "statistics", "a/b testing", "time series", "feature engineering", "model deployment", "mlops", "etl", "data engineering", "data modeling"},
    "Databases & Big Data": {"sql", "nosql", "mysql", "postgresql", "sql server", "oracle", "mongodb", "cassandra", "redis", "dynamodb", "elasticsearch", "neo4j", "hadoop", "spark", "kafka", "airflow", "snowflake", "bigquery", "databricks", "dbt"},
    "Cloud & DevOps": {"aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins", "github actions", "gitlab ci", "ci/cd", "linux", "bash", "shell scripting", "git", "github", "gitlab", "monitoring", "prometheus", "grafana"},
    "Web & APIs": {"flask", "django", "fastapi", "spring boot", ".net", "node.js", "express.js", "streamlit", "react", "angular", "vue", "next.js", "html", "css", "bootstrap", "tailwind css", "rest api", "graphql", "microservices"},
    "Business & Delivery": {"tableau", "power bi", "excel", "looker", "agile", "scrum", "jira", "project management", "stakeholder management", "communication", "leadership", "problem solving"},
    "Testing & Security": {"unit testing", "pytest", "selenium", "junit", "test automation", "cybersecurity", "oauth"},
}


def _contains_alias(text: str, alias: str) -> bool:
    """Match a skill without allowing it inside a longer alphanumeric word."""
    if alias == "c":
        # Do not report C separately when the text contains C++ or C#.
        return re.search(r"(?<![a-z0-9+#])c(?![a-z0-9+#])", text) is not None
    pattern = rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])"
    return re.search(pattern, text) is not None


def extract_skills(text: str) -> set:
    """Extract normalized skills, including common abbreviations and aliases."""
    normalized_text = text.lower().replace("–", "-").replace("—", "-")
    return {
        canonical
        for canonical, aliases in SKILL_ALIASES.items()
        if any(_contains_alias(normalized_text, alias) for alias in aliases)
    }


def group_skills_by_category(skills) -> dict:
    """Group skills for clearer gap explanations in the UI."""
    remaining = set(skills)
    grouped = {}
    for category, category_skills in SKILL_CATEGORIES.items():
        matches = sorted(remaining.intersection(category_skills))
        if matches:
            grouped[category] = matches
            remaining.difference_update(matches)
    if remaining:
        grouped["Other"] = sorted(remaining)
    return grouped


def match_skills(resume_skills: set, jd_skills: set) -> dict:
    """Return deterministic matching/missing skills and JD coverage."""
    matching_skills = sorted(resume_skills.intersection(jd_skills))
    missing_skills = sorted(jd_skills.difference(resume_skills))
    coverage = len(matching_skills) / len(jd_skills) if jd_skills else 0.0
    return {"matching": matching_skills, "missing": missing_skills, "coverage": coverage}
