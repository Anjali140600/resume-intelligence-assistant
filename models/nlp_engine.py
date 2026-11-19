import re

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticMatcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, text_list: list) -> np.ndarray:
        return self.model.encode(text_list, normalize_embeddings=True)

    @staticmethod
    def _chunk_text(text: str, max_words: int = 110) -> list[str]:
        """Split long documents so content after the model token limit is scored."""
        sentences = re.split(r"(?<=[.!?;])\s+", text.strip())
        chunks, current, current_size = [], [], 0

        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            while len(words) > max_words:
                if current:
                    chunks.append(" ".join(current))
                    current, current_size = [], 0
                chunks.append(" ".join(words[:max_words]))
                words = words[max_words:]
            if current and current_size + len(words) > max_words:
                chunks.append(" ".join(current))
                current, current_size = [], 0
            current.append(" ".join(words))
            current_size += len(words)

        if current:
            chunks.append(" ".join(current))
        return chunks or [text]

    def calculate_similarity(self, resume_text: str, job_text: str) -> float:
        """Score how well job-description content is represented in the resume."""
        if not resume_text or not job_text:
            return 0.0

        resume_chunks = self._chunk_text(resume_text)
        job_chunks = self._chunk_text(job_text)
        resume_embeddings = self.generate_embeddings(resume_chunks)
        job_embeddings = self.generate_embeddings(job_chunks)
        similarities = cosine_similarity(job_embeddings, resume_embeddings)

        # Directional JD coverage does not punish a resume for useful experience
        # unrelated to this vacancy. Baseline correction creates a clearer scale.
        raw_coverage = float(np.mean(np.max(similarities, axis=1)))
        calibrated = (raw_coverage - 0.15) / 0.65
        return float(np.clip(calibrated, 0.0, 1.0))
