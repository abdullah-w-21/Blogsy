import streamlit as st
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from crewai import Agent, Task, Crew, Process, LLM
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import Tool
from langchain.tools import StructuredTool
from typing import Optional
import json
import requests
from datetime import datetime
import time
import wikipedia
from googleapiclient.discovery import build
import wikipediaapi
import pandas as pd

# Load environment variables
load_dotenv()

# Initialize Streamlit secrets for API keys
if not st.secrets.get("GEMINI_API_KEY"):
    st.error("Please set GEMINI_API_KEY in your secrets.toml file!")
    st.stop()

# Set API key from secrets
os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# Initialize LLM with Gemini
llm = LLM(
    model='gemini/gemini-1.5-flash',
    api_key=st.secrets["GEMINI_API_KEY"]
)


# Usage tracking function
def track_usage(topic: str, content_length: int, generation_time: float):
    """Track usage statistics in a JSON file"""
    usage_data = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "content_length": content_length,
        "generation_time": generation_time,
    }

    try:
        # Load existing data
        if os.path.exists("usage_stats.json"):
            with open("usage_stats.json", "r") as f:
                data = json.load(f)
        else:
            data = []

        # Append new usage data
        data.append(usage_data)

        # Save updated data
        with open("usage_stats.json", "w") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        st.warning(f"Failed to track usage: {str(e)}")


# Store generated content
def store_content(topic: str, content: str, metadata: dict):
    """Store generated content with metadata"""
    content_data = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "content": content,
        "metadata": metadata
    }

    try:
        # Load existing content
        if os.path.exists("generated_content.json"):
            with open("generated_content.json", "r") as f:
                data = json.load(f)
        else:
            data = []

        # Append new content
        data.append(content_data)

        # Save updated content
        with open("generated_content.json", "w") as f:
            json.dump(data, f, indent=2)

    except Exception as e:
        st.warning(f"Failed to store content: {str(e)}")


# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia("Bloggenapp (abdullahwasim2112@gmail.com)",'en')


def get_wikipedia_content(query: str, max_results: int = 3) -> list:
    """Get relevant Wikipedia articles"""
    try:
        # Search Wikipedia
        search_results = wikipedia.search(query, results=max_results)
        wiki_results = []

        for title in search_results:
            try:
                # Get full page content
                page = wiki_wiki.page(title)
                if page.exists():
                    # Get the first section (usually the most relevant)
                    summary = page.summary[:500] + "..."  # Truncate to 500 chars
                    wiki_results.append({
                        "title": title,
                        "link": page.fullurl,
                        "snippet": summary
                    })
            except Exception:
                continue

        return wiki_results
    except Exception as e:
        st.warning(f"Wikipedia search error: {str(e)}")
        return []


# Free search function combining Wikipedia
def free_search(query: str) -> dict:
    """Perform free web search using Wikipedia"""
    if 'search_status' in st.session_state:
        st.session_state.search_status.markdown(f"🔎 Researching: {query}")

    try:
        # Get Wikipedia results
        wiki_results = get_wikipedia_content(query)

        # Format results
        formatted_results = {
            "organic": wiki_results
        }

        # Display search results in UI
        if 'search_results' in st.session_state:
            with st.session_state.search_results.expander("📚 Search Results", expanded=False):
                st.json(formatted_results)

        return formatted_results

    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return {"organic": []}


# Create search tool
search_tool = StructuredTool.from_function(
    func=free_search,
    name="Web Search",
    description="Searches the web for articles and information based on the provided query. Input should be a specific search query string."
)

# Agent configurations
planner = Agent(
    role="Strategic Content Planner",
    goal="Develop a comprehensive, data-driven content strategy that engages the target audience and provides unique insights on {topic}",
    backstory="""You are an expert content strategist with years of experience in digital content planning. 
    Your strength lies in identifying trending angles, understanding audience psychology, and structuring content 
    that drives engagement. You have a track record of planning viral content that both educates and entertains.""",
    llm=llm,
    tools=[search_tool],
    allow_delegation=False,
    verbose=True
)

writer = Agent(
    role="Expert Content Creator",
    goal="Create an engaging, well-researched, and authoritative article that provides unique insights and actionable value on {topic}",
    backstory="""You are a skilled content creator with expertise in crafting compelling narratives. Follows EEAT ( Experience, Expertise, Authoritativeness, and Trustworthiness) priciple to generate content.
    Your writing style combines deep research with storytelling elements, making complex topics accessible 
    and engaging. You excel at creating content that resonates with readers and drives discussion.""",
    llm=llm,
    allow_delegation=False,
    verbose=True
)

editor = Agent(
    role="Senior Content Editor",
    goal="Refine and polish the content to ensure it meets the highest standards of quality, readability, and impact",
    backstory="""You are a meticulous editor with an eye for detail and a deep understanding of what makes 
    content compelling. You excel at improving clarity, flow, and engagement while maintaining the author's 
    voice. Your edits consistently elevate content to its highest potential.""",
    llm=llm,
    allow_delegation=False,
    verbose=True
)

# Task configurations
plan = Task(
    description="""
    Develop a comprehensive content strategy by:
    1. Conducting thorough research on {topic} to identify:
       - Latest trends and developments
       - Key industry insights and statistics
       - Unique angles and perspectives
       - Gaps in existing content

    2. Create a detailed audience analysis:
       - Primary demographic and psychographic profiles
       - Key pain points and interests
       - Information needs and content preferences
       - Level of expertise on the topic

    3. Develop a strategic content outline including:
       - Hook and unique value proposition
       - Key arguments and insights
       - Supporting data points and examples
       - Logical flow of information

    4. Identify optimization opportunities:
       - Primary and secondary keywords
       - Relevant sources and citations
       - Content hooks for different platforms
       - Engagement triggers and discussion points

    Use the Web Search tool to validate trends and gather supporting evidence.
    """,
    expected_output="""A detailed content strategy document including:
    1. Research findings and key insights
    2. Audience analysis
    3. Structured content outline
    4. SEO and engagement strategy""",
    agent=planner,
)

write = Task(
    description="""
    Create an exceptional piece of content following these guidelines:
    1. Craft a compelling narrative that:
       - Opens with a powerful hook
       - Presents unique insights and perspectives
       - Maintains reader engagement throughout
       - Supports claims with credible data

    2. Structure the content effectively:
       - Use clear, engaging headlines and subheadings
       - Maintain logical flow between sections
       - Include relevant examples and case studies
       - Create smooth transitions

    3. Optimize for engagement:
       - Incorporate narrative elements and storytelling
       - Use active voice and conversational tone
       - Include thought-provoking questions
       - Add relevant analogies and metaphors

    4. Ensure content meets these criteria:
       - Matches specified length of {length} words
       - Naturally incorporates {keywords}
       - Addresses points from {bullet_points}
       - Provides actionable takeaways

    5. Focus on reader value:
       - Offer practical insights
       - Include expert perspectives
       - Address potential questions
       - Provide clear conclusions
    """,
    expected_output="A polished, engaging article that educates, entertains, and provides genuine value to readers.",
    agent=writer,
)

edit = Task(
    description="""
    Enhance the content through careful editing:
    1. Structural Analysis:
       - Verify logical flow and progression
       - Ensure strong opening and conclusion
       - Check section transitions
       - Validate argument coherence

    2. Content Quality:
       - Verify factual accuracy
       - Check data and statistics
       - Ensure balanced perspective
       - Validate source credibility

    3. Language Enhancement:
       - Improve sentence variety
       - Eliminate redundancy
       - Enhance clarity and impact
       - Maintain consistent tone

    4. Technical Review:
       - Fix grammar and punctuation
       - Check formatting consistency
       - Verify keyword usage
       - Optimize headings and subheadings

    5. Final Polish:
       - Enhance readability
       - Strengthen calls-to-action
       - Improve engagement elements
       - Ensure professional presentation
    """,
    expected_output="A thoroughly polished, professional article ready for publication.",
    agent=editor
)

# Create crew
crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan, write, edit],
    verbose=True
)


# Streamlit frontend
def main():
    st.title("Professional Blog Generator")
    st.markdown("""
    This AI-powered tool will generate a professional blog post based on your inputs.
    Watch the creative process unfold in real-time! 🚀
    """)

    # Initialize session state variables
    if 'blog_content' not in st.session_state:
        st.session_state.blog_content = None
    if 'process_status' not in st.session_state:
        st.session_state.process_status = st.empty()
    if 'search_status' not in st.session_state:
        st.session_state.search_status = st.empty()
    if 'search_results' not in st.session_state:
        st.session_state.search_results = st.empty()
    if 'agent_outputs' not in st.session_state:
        st.session_state.agent_outputs = st.empty()

    # Input form
    with st.form("blog_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input(
                "Topic",
                help="Enter the main topic of your blog post"
            )
            keywords = st.text_input(
                "Keywords (comma-separated)",
                help="Enter relevant keywords separated by commas"
            )

        with col2:
            length = st.number_input(
                "Word Count",
                min_value=300,
                max_value=5000,
                value=800,
                help="Specify the desired length of your blog post"
            )

        bullet_points = st.text_area(
            "Key Points",
            help="Enter key points to be covered in the blog post"
        )

        submitted = st.form_submit_button("Generate Blog Post ✨")

    # Generate content
    if submitted:
        start_time = time.time()

        if not topic or not keywords or not bullet_points:
            st.error("Please fill in all the required fields!")
            return

        # Create tabs for output and progress
        progress_tab, output_tab = st.tabs(["Generation Progress", "Final Output"])

        with progress_tab:
            # Progress tracking
            st.subheader("🔄 Real-time Progress")
            process_container = st.container()
            research_container = st.container()
            agent_container = st.container()

            with process_container:
                status_placeholder = st.empty()
                progress_bar = st.progress(0)

            with research_container:
                st.subheader("🔍 Research Progress")
                st.session_state.search_status = st.empty()
                st.session_state.search_results = st.container()

            with agent_container:
                st.subheader("🤖 Agent Activities")
                planner_output = st.expander("Content Planner", expanded=True)
                writer_output = st.expander("Content Writer", expanded=True)
                editor_output = st.expander("Content Editor", expanded=True)

            # Initialize input
            inputs = {
                "topic": topic,
                "keywords": [k.strip() for k in keywords.split(",")],
                "bullet_points": [p.strip() for p in bullet_points.split("\n") if p.strip()],
                "length": length
            }

            try:
                # Update progress
                status_placeholder.markdown("### 🎯 Starting Content Generation")
                progress_bar.progress(10)

                # Execute planner
                status_placeholder.markdown("### 📋 Planning Content Strategy")
                result = crew.kickoff(inputs=inputs)

                # Update planner output
                planner_output.markdown("#### Content Strategy")
                planner_output.markdown(str(plan.output))
                progress_bar.progress(40)

                # Update writer output
                status_placeholder.markdown("### ✍️ Writing Content")
                writer_output.markdown("#### Initial Draft")
                writer_output.markdown(str(write.output))
                progress_bar.progress(70)

                # Update editor output
                status_placeholder.markdown("### 📝 Editing and Polishing")
                editor_output.markdown("#### Final Edited Version")
                editor_output.markdown(str(edit.output))
                progress_bar.progress(100)

                status_placeholder.markdown("### ✅ Content Generation Complete!")

                # Store content in session
                st.session_state.blog_content = str(edit.output)

                # Calculate generation time
                generation_time = time.time() - start_time

                # Track usage
                track_usage(topic, len(st.session_state.blog_content), generation_time)

                # Store generated content
                metadata = {
                    "keywords": keywords.split(","),
                    "word_count": length,
                    "bullet_points": bullet_points.split("\n"),
                    "generation_time": generation_time
                }
                store_content(topic, st.session_state.blog_content, metadata)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                return

        with output_tab:
            st.subheader("📚 Final Blog Post")

            if st.session_state.blog_content:
                try:
                    # Convert to string
                    content_str = str(st.session_state.blog_content)

                    # Download button
                    st.download_button(
                        label="Download Blog Post",
                        data=content_str,
                        file_name=f"blog_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown"
                    )

                    # Display the final blog post
                    st.markdown(content_str, unsafe_allow_html=True)

                    # Display metadata
                    with st.expander("📊 Content Metadata"):
                        st.json({
                            "Topic": topic,
                            "Keywords": keywords.split(","),
                            "Word Count": length,
                            "Generation Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Number of Key Points": len(bullet_points.split("\n")),
                            "Content Length": len(content_str),
                            "Generation Time": f"{time.time() - start_time:.2f} seconds"
                        })

                    # Display usage statistics
                    with st.expander("📊 Usage Statistics"):
                        if os.path.exists("usage_stats.json"):
                            with open("usage_stats.json", "r") as f:
                                usage_data = pd.DataFrame(json.load(f))

                                # Display generation time trend
                                st.subheader("Generation Time Trend")
                                st.line_chart(usage_data.set_index("timestamp")["generation_time"])

                                # Display content length trend
                                st.subheader("Content Length Trend")
                                st.line_chart(usage_data.set_index("timestamp")["content_length"])

                                # Display raw data
                                st.subheader("Raw Usage Data")
                                st.dataframe(usage_data)

                except Exception as e:
                    st.error(f"Error handling content: {str(e)}")


if __name__ == "__main__":
    main()
