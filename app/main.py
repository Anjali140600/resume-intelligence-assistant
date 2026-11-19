import os
import sys

import plotly.graph_objects as go
import streamlit as st

# Allow imports from the project root when Streamlit starts this file directly.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.nlp_engine import SemanticMatcher
from utils.skill_extractor import extract_skills, group_skills_by_category, match_skills
from utils.text_processing import clean_text, extract_text_from_pdf


st.set_page_config(
    page_title="Resume Intelligence Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .score-note {color: #667085; font-size: 0.88rem; margin-top: -0.5rem;}
        .skill-chip {background: #f2f4f7; border-radius: 6px; padding: 3px 7px;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def load_nlp_model():
    return SemanticMatcher()


def render_recommendations(
    overall_score: float,
    semantic_score: float,
    skill_coverage: float,
    matching_skills: list,
    missing_skills: list,
):
    """Render specific recommendations tied to the analysis results."""
    st.subheader("💡 Detailed Improvement Plan")

    if overall_score >= 0.8:
        st.success("Strong match. Focus on evidence, measurable results, and final ATS polish.")
    elif overall_score >= 0.6:
        st.info("Good foundation. Closing the priority gaps below should make the résumé more targeted.")
    else:
        st.warning("The résumé needs stronger alignment. Start with the priority actions below before applying.")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Priority actions", "Missing skills", "Bullet rewrites", "ATS checklist"]
    )

    with tab1:
        priority_number = 1
        if semantic_score < 0.65:
            st.markdown(
                f"**{priority_number}. Rewrite the professional summary for this role**  \n"
                "Use 2–3 lines containing the target job title, your relevant experience, "
                "the role's main domain, and 3–5 skills you genuinely possess."
            )
            st.code(
                "[Target role] with [X years/projects] of experience in [domain]. "
                "Skilled in [relevant skills], with experience delivering [measurable outcome].",
                language=None,
            )
            priority_number += 1

        if missing_skills:
            top_gaps = ", ".join(missing_skills[:6])
            st.markdown(
                f"**{priority_number}. Address the highest-value skill gaps**  \n"
                f"Review these first: **{top_gaps}**. Add a skill only when you can support it "
                "with real work, a project, coursework, or certification."
            )
            priority_number += 1

        st.markdown(
            f"**{priority_number}. Move the most relevant evidence upward**  \n"
            "Put the projects and experience most similar to the job near the top. Remove or shorten "
            "older bullets that do not support the target role."
        )
        priority_number += 1

        st.markdown(
            f"**{priority_number}. Quantify outcomes**  \n"
            "Replace duty-only statements with impact: time saved, accuracy, revenue, users, "
            "latency, data volume, cost reduction, or percentage improvement."
        )

        if matching_skills:
            st.markdown("**Strengths already aligned with the job:**")
            st.write(" · ".join(matching_skills))

    with tab2:
        if not missing_skills:
            st.success("No explicit skill gaps were detected. Verify that each important skill is demonstrated in an experience or project bullet, not only listed.")
        else:
            st.caption("These are skills found in the job description but not found in the résumé.")
            grouped_missing = group_skills_by_category(missing_skills)
            for category, skills in grouped_missing.items():
                with st.expander(f"{category} ({len(skills)})", expanded=True):
                    for skill in skills:
                        st.markdown(
                            f"- **{skill}** — if you have used it, add where you used it, what you built, "
                            "and the result. Otherwise, treat it as a learning gap; do not claim experience you do not have."
                        )

    with tab3:
        st.markdown("Use this structure: **Action + task + technology + measurable result**.")
        st.markdown("**Weak:** Responsible for machine-learning models and data analysis.")
        st.markdown(
            "**Stronger:** Built and evaluated a classification model using Python and scikit-learn, "
            "improving validation F1 score from **[A]** to **[B]**."
        )
        st.markdown("**Weak:** Worked on APIs and databases.")
        st.markdown(
            "**Stronger:** Developed **[number]** REST endpoints with FastAPI and PostgreSQL, "
            "reducing average response time by **[percentage]**."
        )
        if missing_skills:
            examples = ", ".join(missing_skills[:3])
            st.info(
                f"For this job, create truthful evidence-based bullets around **{examples}** if you "
                "have actually used them. Replace bracketed placeholders with your real figures."
            )

    with tab4:
        checklist = [
            "Use the exact target job title in the summary when it accurately describes your profile.",
            "Use standard headings: Summary, Skills, Experience, Projects, Education, Certifications.",
            "Place important keywords naturally in context; avoid copying the whole job description.",
            "Show important skills in achievement bullets as well as in the Skills section.",
            "Use simple formatting: one column, readable fonts, and no text embedded in images.",
            "Use consistent dates and verb tense, and check spelling carefully.",
            "Keep links selectable and export a text-based PDF rather than a scanned PDF.",
            "Never add a missing skill unless you can honestly explain your experience in an interview.",
        ]
        for item in checklist:
            st.markdown(f"- {item}")

    with st.expander("How this score is calculated"):
        st.markdown(
            f"- **Semantic alignment ({semantic_score * 100:.1f}%)**: chunked comparison of job requirements "
            "against the full résumé, so later résumé sections are not ignored.\n"
            f"- **Skill coverage ({skill_coverage * 100:.1f}%)**: percentage of detected job skills also found in the résumé.\n"
            "- **Overall score**: 75% semantic alignment + 25% skill coverage. If the job description has "
            "no recognized skills, semantic alignment is used alone. This is a targeting aid, not a hiring probability."
        )


matcher = load_nlp_model()

st.title("📄 Resume Intelligence Assistant")
st.markdown(
    "Compare your résumé against a job description to measure alignment, identify skill gaps, "
    "and receive a prioritized improvement plan."
)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Upload Résumé")
    resume_file = st.file_uploader("Upload a text-based PDF", type=["pdf"])
with col2:
    st.subheader("Job Description")
    job_description = st.text_area("Paste the complete job description", height=220)

if st.button("Analyze Match", type="primary", width="stretch"):
    if not resume_file:
        st.error("Please upload a résumé PDF.")
    elif not job_description.strip():
        st.error("Please provide a job description.")
    else:
        with st.spinner("Comparing the full documents and identifying skill gaps..."):
            resume_text = clean_text(extract_text_from_pdf(resume_file))
            jd_text = clean_text(job_description)

            if len(resume_text.split()) < 30:
                st.error(
                    "Very little text could be read from this PDF. Please use a text-based PDF; "
                    "scanned/image PDFs require OCR before analysis."
                )
                st.stop()

            resume_skills = extract_skills(resume_text)
            jd_skills = extract_skills(jd_text)
            skill_results = match_skills(resume_skills, jd_skills)
            matching_skills = skill_results["matching"]
            missing_skills = skill_results["missing"]
            skill_coverage = skill_results["coverage"]

            semantic_score = matcher.calculate_similarity(resume_text, jd_text)
            overall_score = (
                0.75 * semantic_score + 0.25 * skill_coverage
                if jd_skills
                else semantic_score
            )

        st.success("Analysis complete")
        st.header("Match Analysis")

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Overall Match", f"{overall_score * 100:.1f}%")
        mcol2.metric("Semantic Alignment", f"{semantic_score * 100:.1f}%")
        mcol3.metric("Skill Coverage", f"{skill_coverage * 100:.1f}%" if jd_skills else "N/A")
        mcol4.metric("Missing Skills", len(missing_skills))
        st.markdown(
            '<p class="score-note">Scores measure résumé targeting and detected evidence—not your ability or likelihood of being hired.</p>',
            unsafe_allow_html=True,
        )

        st.divider()
        vcol1, vcol2 = st.columns([1, 1])
        with vcol1:
            st.subheader("Skill Coverage")
            if jd_skills:
                fig = go.Figure(
                    data=[go.Pie(
                        labels=["Matched", "Missing"],
                        values=[len(matching_skills), len(missing_skills)],
                        hole=0.55,
                        marker_colors=["#12B76A", "#F04438"],
                    )]
                )
                fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No skills from the current dictionary were detected in the job description. The overall score uses semantic alignment only.")

        with vcol2:
            st.subheader("Detected Skills")
            st.markdown(f"**Job skills detected:** {len(jd_skills)}")
            st.markdown("**Matching:**")
            st.write(" ".join(f"`{skill}`" for skill in matching_skills) or "None detected")
            st.markdown("**Missing:**")
            st.write(" ".join(f"`{skill}`" for skill in missing_skills) or "None detected")

        st.divider()
        render_recommendations(
            overall_score,
            semantic_score,
            skill_coverage,
            matching_skills,
            missing_skills,
        )
