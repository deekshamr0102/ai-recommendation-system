"""
Streamlit web application for the AI Lifestyle Recommendation System.
Provides user-friendly interface for getting personalized recommendations.
"""

import streamlit as st
import json
import logging

# Add src to path
import sys

from src.recommender import RecommendationEngine
from src.config import PAGE_TITLE, PAGE_ICON, LAYOUT
from src.utils import OutputFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# Streamlit page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1em;
        font-weight: 500;
    }
    .recommendation-box {
        border: 2px solid #1f77b4;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        background-color: #f0f2f6;
    }
    .cost-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .reasoning-box {
        background-color: #e7f3ff;
        border: 1px solid #b3d9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    """, unsafe_allow_html=True)


@st.cache_resource
def load_recommendation_engine():
    try:
        return RecommendationEngine()
    except Exception as e:
        st.error(f"Engine failed to load: {e}")
        raise e


def display_movie_recommendation(movie: dict):
    """Display movie recommendation."""
    if not movie:
        return

    st.subheader("🎬 Movie Recommendation")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"*{movie.get('title', 'N/A')}*")
        st.write(f"Genre: {', '.join(movie.get('genre', []))}")
        st.write(f"Duration: {movie.get('duration_minutes', 'N/A')} minutes")
        st.write(f"Rating: {'⭐' * int(movie.get('rating', 0) / 2)}")

    with col2:
        st.metric("Rating", f"{movie.get('rating', 'N/A')}/10")

    st.write(f"Description: {movie.get('description', 'N/A')}")
    st.write(f"Mood Tags: {', '.join(movie.get('mood_tags', []))}")


def display_restaurant_recommendation(restaurant: dict):
    """Display restaurant recommendation."""
    if not restaurant:
        return

    st.subheader("🍽️ Restaurant Recommendation")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"*{restaurant.get('name', 'N/A')}*")
        st.write(f"Cuisine: {', '.join(restaurant.get('cuisine', []))}")
        st.write(f"Location: {restaurant.get('location', 'N/A').title()}")
        st.write(f"Ambiance: {', '.join(restaurant.get('ambiance', []))}")

    with col2:
        st.metric("Price Range", restaurant.get('price_range', 'N/A'))

    st.write(f"Description: {restaurant.get('description', 'N/A')}")
    st.write(f"Suitable for groups of: {', '.join(map(str, restaurant.get('group_size', [])))}")


def display_activity_recommendation(activity: dict):
    """Display activity recommendation."""
    if not activity:
        return

    st.subheader("🎯 Activity Recommendation")
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"*{activity.get('name', 'N/A')}*")
        st.write(f"Type: {', '.join(activity.get('type', []))}")
        st.write(f"Duration: {activity.get('duration_minutes', 'N/A')} minutes")
        st.write(f"Location: {activity.get('location', 'N/A').title()}")

    with col2:
        st.metric("Cost per Person", f"${activity.get('cost_per_person', 'N/A')}")

    st.write(f"Description: {activity.get('description', 'N/A')}")
    st.write(f"Suitable for groups of: {', '.join(map(str, activity.get('group_size', [])))}")


def display_recommendations(result: dict):
    """Display recommendation results."""
    if result.get("status") == "error":
        st.error(f"❌ Error: {result.get('message')}")
        return

    # Display cost estimate
    estimated_cost = result.get("estimated_cost", 0)
    st.markdown(
        f"""
        
            💰 Estimated Total Cost: ${estimated_cost:.2f}
        
        """,
        unsafe_allow_html=True
    )

    # Display recommendations
    col1, col2, col3 = st.columns(3)

    with col1:
        display_movie_recommendation(result.get("movie"))

    with col2:
        display_restaurant_recommendation(result.get("restaurant"))

    with col3:
        display_activity_recommendation(result.get("activity"))

    # Display reasoning
    reasoning = result.get("reasoning")
    if reasoning:
        st.markdown(
            f"""
            
                💡 Why These Recommendations?
                {reasoning}
            
            """,
            unsafe_allow_html=True
        )

    # Display raw JSON
    with st.expander("📋 View Raw JSON Output"):
        st.json(result)


def main():
    """Main Streamlit application."""
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")

    # Sidebar
    with st.sidebar:
        st.header("About")
        st.write(
            """
            This AI-powered system recommends movies, restaurants, and activities
            based on your natural language input.

            *Features:*
            - 🤖 Phase 1: LLM-based understanding
            - 🔍 Phase 2: Embedding-based retrieval
            - 🎯 Multi-domain recommendations
            - 💰 Cost estimation
            - 📝 Personalized reasoning

            *How it works:*
            1. Describe your mood, occasion, budget, and preferences
            2. The system extracts structured information
            3. Embeddings find similar recommendations
            4. LLM generates personalized explanations
            5. Receive structured recommendations
            """
        )

        st.markdown("---")
        st.write("*Example Inputs:*")
        examples = [
            "I'm feeling adventurous with my 3 friends downtown with $50 budget",
            "Date night, romantic mood, $100 budget in the city",
            "Family gathering, relaxed, suburban area, 6 people",
            "Solo relaxation, calm mood, free or cheap activities"
        ]
        for example in examples:
            st.caption(f"💬 {example}")

    # Main content
    st.header("Get Your Personalized Recommendations")

    # User input
    user_input = st.text_area(
        "Describe your mood, occasion, budget, location, and group size:",
        placeholder="Example: I'm feeling adventurous and want to take my 3 friends out. We have $50 budget per person in downtown area.",
        height=100
    )

    # Tabs for different interaction modes
    tab1, tab2 = st.tabs(["Quick Recommendation", "Advanced Options"])

    with tab1:
        if st.button("🚀 Get Recommendations", key="quick_recommend"):
            if not user_input.strip():
                st.warning("⚠️ Please enter your preferences")
            else:
                with st.spinner("🔄 Analyzing your preferences and retrieving recommendations..."):
                    try:
                        engine = load_recommendation_engine()
                        result = engine.get_recommendations(user_input)
                        display_recommendations(result)
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
                        logger.error(f"Error in recommendation: {e}")

    with tab2:
        st.write("*Advanced Options* (Optional - these help refine recommendations)")

        col1, col2 = st.columns(2)

        with col1:
            budget = st.number_input(
                "Budget (USD)",
                min_value=0,
                max_value=500,
                value=0,
                step=10,
                help="Leave as 0 if not specified in text"
            )

            people_count = st.number_input(
                "Number of People",
                min_value=1,
                max_value=20,
                value=1,
                help="Leave as 1 if solo"
            )

        with col2:
            location = st.selectbox(
                "Location Type",
                ["Not specified", "Downtown", "Suburban", "Rural", "Beach", "Mountain"],
                help="Select if not mentioned in description"
            )

            occasion = st.selectbox(
                "Occasion",
                ["Not specified", "Date Night", "Family Gathering", "Friends Hangout",
                 "Solo", "Business", "Celebration", "Relaxation"],
                help="Select if not mentioned in description"
            )

        # Build enhanced input
        enhanced_input = user_input

        if budget > 0:
            enhanced_input += f" Budget: ${budget}"

        if people_count > 1:
            enhanced_input += f" Group size: {people_count} people"

        if location != "Not specified":
            enhanced_input += f" Location: {location}"

        if occasion != "Not specified":
            enhanced_input += f" Occasion: {occasion}"

        if st.button("🚀 Get Advanced Recommendations", key="advanced_recommend"):
            if not user_input.strip():
                st.warning("⚠️ Please enter your preferences")
            else:
                with st.spinner("🔄 Analyzing your preferences with advanced options..."):
                    try:
                        engine = load_recommendation_engine()
                        result = engine.get_recommendations(enhanced_input)
                        display_recommendations(result)
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
                        logger.error(f"Error in advanced recommendation: {e}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        
            AI Lifestyle Recommendation System | Powered by Hugging Face Transformers & SentenceTransformers
            Phase 1: LLM-Based | Phase 2: Embedding-Based Retrieval
        
        """,
        unsafe_allow_html=True
    )



if _name_ == "_main_":
    main()
    
