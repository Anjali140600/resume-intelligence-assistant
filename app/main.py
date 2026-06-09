import streamlit as st
import sys
import os
import plotly.express as px
import plotly.graph_objects as go

# Add the project root to the path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_processing import extract_text_from_pdf, clean_text
from utils.skill_extractor import extract_skills, match_skills
from models.nlp_engine import SemanticMatcher

# Set page configuration for a professional look
st.set_page_config(
    page_title="Resume Intelligence Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI styling
st.markdown("""
<style>
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the NLP engine
# We use @st.cache_resource to ensure we only load the model once
@st.cache_resource
def load_nlp_model():
    return SemanticMatcher()

matcher = load_nlp_model()

st.title("📄 Resume Intelligence Assistant")
st.markdown("Compare your resume against job descriptions to get an intelligent matching score and recommendations.")

# Layout: Two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Resume")
    resume_file = st.file_uploader("Upload your resume in PDF format", type=["pdf"])

with col2:
    st.subheader("Job Description")
    job_description = st.text_area("Paste the job description text here", height=200)

if st.button("Analyze Match", type="primary"):
    if not resume_file:
        st.error("Please upload a resume.")
    elif not job_description.strip():
        st.error("Please provide a job description.")
    else:
        with st.spinner("Analyzing semantics and extracting skills..."):
            # 1. Extract text from PDF
            resume_text_raw = extract_text_from_pdf(resume_file)
            
            # 2. Clean text
            resume_text = clean_text(resume_text_raw)
            jd_text = clean_text(job_description)
            
            # 3. Compute Similarity Score
            similarity = matcher.calculate_similarity(resume_text, jd_text)
            match_percentage = round(similarity * 100, 2)
            
            # 4. Extract Skills
            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text)
            
            # 5. Match Skills
            skill_match_results = match_skills(resume_skills, jd_skills)
            matching_skills = skill_match_results["matching"]
            missing_skills = skill_match_results["missing"]
            
        st.success("Analysis Complete!")
        
        # Display Results
        st.markdown("---")
        st.header("Analysis Results")
        
        # Top Metrics Row
        mcol1, mcol2, mcol3 = st.columns(3)
        with mcol1:
            st.metric(label="Semantic Match Score", value=f"{match_percentage}%")
        with mcol2:
            st.metric(label="Matching Skills Found", value=len(matching_skills))
        with mcol3:
            st.metric(label="Missing Skills", value=len(missing_skills))
            
        st.markdown("---")
        
        # Visualizations & Details
        vcol1, vcol2 = st.columns([1, 1])
        
        with vcol1:
            st.subheader("Skill Match Visualization")
            # Create a simple pie chart of skills
            total_jd_skills = len(jd_skills)
            if total_jd_skills > 0:
                labels = ['Matching Skills', 'Missing Skills']
                values = [len(matching_skills), len(missing_skills)]
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker_colors=['#2ecc71', '#e74c3c'])])
                fig.update_layout(margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No common tech skills detected in the Job Description. The score is based purely on semantic text similarity.")

        with vcol2:
            st.subheader("Skill Details")
            st.markdown("**Matching Skills:**")
            if matching_skills:
                st.write(" ".join([f"`{s}`" for s in matching_skills]))
            else:
                st.write("None detected.")
                
            st.markdown("**Missing Skills:**")
            if missing_skills:
                st.write(" ".join([f"`{s}`" for s in missing_skills]))
            else:
                st.write("None detected. Great job!")

        # Recommendations
        st.markdown("---")
        st.subheader("💡 Improvement Recommendations")
        if match_percentage < 50:
            st.warning("Your resume has low semantic similarity with the job description. Consider rewriting your experiences to align with the core themes of the JD.")
        elif match_percentage < 75:
            st.info("Good match! You can improve your chances by incorporating some of the missing skills naturally into your experience sections.")
        else:
            st.success("Excellent match! Your resume aligns highly with the job description.")
            
        if missing_skills:
            st.markdown("Consider adding these keywords if you have experience with them:")
            st.markdown(", ".join([f"**{s}**" for s in missing_skills]))
