from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SemanticMatcher:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the Semantic Matcher with a pre-trained Sentence Transformer model.
        This model translates sentences into multi-dimensional embeddings.
        """
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, text_list: list) -> np.ndarray:
        """
        Generates dense vector embeddings for a list of texts.
        """
        return self.model.encode(text_list)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculates the cosine similarity between two texts.
        Returns a float between 0.0 and 1.0.
        Cosine similarity measures the cosine of the angle between two vectors.
        """
        if not text1 or not text2:
            return 0.0
            
        embeddings = self.generate_embeddings([text1, text2])
        
        # Calculate cosine similarity between the two embeddings
        sim_matrix = cosine_similarity([embeddings[0]], [embeddings[1]])
        
        # Extract the scalar value and ensure it's clamped between 0 and 1
        similarity_score = sim_matrix[0][0]
        return float(max(0.0, min(1.0, similarity_score)))
