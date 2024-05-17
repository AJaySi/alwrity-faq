import time #Iwish
import os
import json
import requests
import streamlit as st
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import google.generativeai as genai

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity - AI Writer",
    )
    st.markdown(f"""
      <style>
      [class="st-emotion-cache-7ym5gk ef3psqc12"]{{
            display: inline-block;
            padding: 5px 20px;
            background-color: #4681f4;
            color: #FBFFFF;
            width: 300px;
            height: 35px;
            text-align: center;
            text-decoration: none;
            font-size: 16px;
            border-radius: 8px;’
      }}
      </style>
    """
    , unsafe_allow_html=True)
    # Title and description
    st.title("✍️ Alwrity - AI Blog FAQ Generator")

    # Input section
    with st.expander("**PRO-TIP** - Read the instructions below.", expanded=True):
        input_blog_keywords = st.text_input('**Enter main keywords of your blog!** (2-3 words that define your blog)')
        col1, col2, space = st.columns([5, 5, 0.5])
        with col1:
            input_title_type = st.selectbox('Blog Type', ('General', 'How-to Guides', 'Tutorials', 'Listicles', 'Newsworthy Posts', 'FAQs', 'Checklists/Cheat Sheets'), index=0)
        with col2:
            input_title_intent = st.selectbox('Search Intent', ('Informational Intent', 'Commercial Intent', 'Transactional Intent', 'Navigational Intent'), index=0)

        # Generate Blog FAQ button
        if st.button('**Generate Blog FAQs**'):
            with st.spinner():
                # Clicking without providing data, really ?
                if not input_blog_keywords:
                    st.error('** 🫣Provide Inputs to generate Blog Tescription. Blog Keywords, is required!**')
                elif input_blog_keywords:
                    blog_faqs = generate_blog_faqs(input_blog_keywords, input_title_type, input_title_intent)
                    if blog_faqs:
                        st.subheader('**👩🔬🧕Go Rule search ranking with these Blog FAQs!**')
                        st.code(blog_faqs)
                    else:
                        st.error("💥**Failed to generate blog FAQs. Please try again!**")


# Function to generate blog metadesc
def generate_blog_faqs(input_blog_keywords, input_title_type, input_title_intent):
    """ Function to call upon LLM to get the work done. """
    # Fetch SERP results & PAA questions for FAQ.
    serp_results, people_also_ask = get_serp_results(input_blog_keywords)

    # If keywords and content both are given.
    if serp_results:
        prompt = f"""As a SEO expert and experienced content writer, 
        I will provide you with following 'blog keywords' and 'google serp results'.
        Your task is to write 5 SEO optimised and detailed FAQs.

        Follow the below guidelines for generating the blog titles:
        1). Your FAQ should be based on 'People also ask' and 'Related Queries' from given serp results.
        2). Always include answer for each FAQ, in your response.
        4). Optimise your response for blog type of {input_title_type}.
        5). Optimise your response FAQs, such that it can feature in google rich snippets.\n

        blog keywords: '{input_blog_keywords}'\n
        google serp results: '{serp_results}'
        people_also_ask: '{people_also_ask}'
        """
        st.write(people_also_ask)
        blog_faqs = generate_text_with_exception_handling(prompt)
        return blog_faqs


def get_serp_results(search_keywords):
    """ """
    serp_results = perform_serperdev_google_search(search_keywords)
    people_also_ask = [item.get("question") for item in serp_results.get("peopleAlsoAsk", [])]
    return serp_results, people_also_ask


def perform_serperdev_google_search(query):
    """
    Perform a Google search using the Serper API.

    Args:
        query (str): The search query.

    Returns:
        dict: The JSON response from the Serper API.
    """
    # Get the Serper API key from environment variables
    serper_api_key = os.getenv('SERPER_API_KEY')

    # Check if the API key is available
    if not serper_api_key:
        st.error("SERPER_API_KEY is missing. Set it in the .env file.")

    # Serper API endpoint URL
    url = "https://google.serper.dev/search"
    # FIXME: Expose options to end user. Request payload
    payload = json.dumps({
        "q": query,
        "gl": "in",
        "hl": "en",
        "num": 10,
        "autocorrect": True,
        "page": 1,
        "type": "search",
        "engine": "google"
    })

    # Request headers with API key
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }

    # Send a POST request to the Serper API with progress bar
    with st.spinner("Searching Google..."):
        response = requests.post(url, headers=headers, data=payload, stream=True)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}, {response.text}")



@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_text_with_exception_handling(prompt):
    """
    Generates text using the Gemini model with exception handling.

    Args:
        api_key (str): Your Google Generative AI API key.
        prompt (str): The prompt for text generation.

    Returns:
        str: The generated text.
    """

    try:
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        return convo.last.text

    except Exception as e:
        st.exception(f"GEMINI: An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    main()
