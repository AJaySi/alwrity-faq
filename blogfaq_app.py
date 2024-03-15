import time #Iwish
import os
import json
import openai
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)


def main():
    # Set page configuration
    st.set_page_config(
        page_title="Alwrity",
        layout="wide",
        page_icon="img/logo.png"
    )
    # Remove the extra spaces from margin top.
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 0rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)
    st.markdown(f"""
      <style>
      [class="st-emotion-cache-7ym5gk ef3psqc12"]{{
            display: inline-block;
            padding: 5px 20px;
            background-color: #4A55A2;’
            color: #C5DFF8;
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

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    # Sidebar input for OpenAI API Key
    openai_api_key = st.sidebar.text_input("**Enter OpenAI API Key(Optional)**", type="password")
    st.sidebar.image("img/alwrity.jpeg", use_column_width=True)
    st.sidebar.markdown(f"🧕 :red[Checkout Alwrity], complete **AI writer & Blogging solution**:[Alwrity](https://alwrity.netlify.app)")
    
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
                        st.subheader('**👩‍🔬👩‍🔬Go Rule search ranking with these Blog FAQs!**')
                        st.code(blog_faqs)
                        st.balloons()
                    else:
                        st.error("💥**Failed to generate blog FAQs. Please try again!**")

    data_oracle = import_json(r"lottie_files/brain_robot.json")
    st_lottie(data_oracle, key="oracle")
    st.markdown('''
                Generate SEO optimized Blog FAQs - powered by AI (OpenAI GPT-3, Gemini Pro).
                Implemented by [Alwrity](https://alwrity.netlify.app).
                Alwrity will do web research for given keywords OR Blog content.
                It will process 'People Also Ask' questions and generate 5 Frequently Asked Questions(FAQ).
                ''')



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
        blog_faqs = openai_chatgpt(prompt)
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
def openai_chatgpt(prompt, model="gpt-3.5-turbo-0125", temperature=0.2, max_tokens=500, top_p=0.9, n=3):
    """
    Wrapper function for OpenAI's ChatGPT completion.

    Args:
        prompt (str): The input text to generate completion for.
        model (str, optional): Model to be used for the completion. Defaults to "gpt-4-1106-preview".
        temperature (float, optional): Controls randomness. Lower values make responses more deterministic. Defaults to 0.2.
        max_tokens (int, optional): Maximum number of tokens to generate. Defaults to 8192.
        top_p (float, optional): Controls diversity. Defaults to 0.9.
        n (int, optional): Number of completions to generate. Defaults to 1.

    Returns:
        str: The generated text completion.

    Raises:
        SystemExit: If an API error, connection error, or rate limit error occurs.
    """
    # Wait for 10 seconds to comply with rate limits
    for _ in range(10):
        time.sleep(1)

    try:
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            n=n,
            top_p=top_p
            # Additional parameters can be included here
        )
        return response.choices[0].message.content

    except openai.APIError as e:
        st.error(f"OpenAI API Error: {e}")
    except openai.APIConnectionError as e:
        st.error(f"Failed to connect to OpenAI API: {e}")
    except openai.RateLimitError as e:
        st.error(f"Rate limit exceeded on OpenAI API request: {e}")
    except Exception as err:
        st.error(f"OpenAI error: {err}")



# Function to import JSON data
def import_json(path):
    with open(path, "r", encoding="utf8", errors="ignore") as file:
        url = json.load(file)
        return url


if __name__ == "__main__":
    main()
