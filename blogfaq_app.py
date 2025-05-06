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
from bs4 import BeautifulSoup


def main():
    # Set page configuration
    st.set_page_config(
        page_title="ALwrity - AI Blog FAQ Generator",
        layout="wide",
    )
    # Custom CSS for theme
    st.markdown("""
        <style>
                ::-webkit-scrollbar-track {
        background: #e1ebf9;
        }
        ::-webkit-scrollbar-thumb {
            background-color: #90CAF9;
            border-radius: 10px;
            border: 3px solid #e1ebf9;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #64B5F6;
        }
        ::-webkit-scrollbar {
            width: 16px;
        }
        div.stButton > button:first-child {
            background: #1565C0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 2px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
            font-weight: bold;
        }
        </style>
    """
    , unsafe_allow_html=True)
    # Hide top header line
    st.markdown('<style>header {visibility: hidden;}</style>', unsafe_allow_html=True)
    # Hide footer
    st.markdown('<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>', unsafe_allow_html=True)

    # Tool title and description at the top
    st.markdown('<h1 style="display:flex;align-items:center;font-size:2.5rem;gap:0.5rem;">🤖 ALwrity Blog FAQ Generator</h1>', unsafe_allow_html=True)
    st.markdown('<div style="color:#1976D2;font-size:1.2rem;margin-bottom:1.5rem;">Generate SEO-optimized, Google-rich FAQs for your blog in seconds.</div>', unsafe_allow_html=True)

    # How it works section
    with st.expander('ℹ️ How it works', expanded=False):
        st.markdown('''
        1. **Enter your main blog keywords** or paste a blog URL to scrape and rewrite its FAQs.
        2. **(Optional)** Choose your blog type, search intent, and output language.
        3. **(Optional)** Provide your own API keys if you have them.
        4. Click **Generate Blog FAQs** to get SEO-optimized FAQs (and schema markup if selected).
        5. Copy and use the results in your blog!
        ''')

    # --- API Key Input Section ---
    with st.expander("API Configuration 🔑", expanded=False):
        st.markdown('''If the default Gemini or Serper API key is unavailable or exceeds its limits, you can provide your own API key below.<br>
        <a href="https://aistudio.google.com/app/apikey" target="_blank">Get Gemini API Key</a> | 
        <a href="https://serper.dev" target="_blank">Get SERPER API Key</a>
        ''', unsafe_allow_html=True)
        user_gemini_api_key = st.text_input("Gemini API Key", type="password", help="Paste your Gemini API Key here if you have one. Otherwise, the tool will use the default key if available.")
        user_serper_api_key = st.text_input("SERPER API Key (for Google research)", type="password", help="Paste your Serper API Key here if you have one. Otherwise, the tool will use the default key if available.")

    # --- FAQ Generation Form ---
    st.markdown('<h3 style="margin-top:2rem;">2️⃣ Enter Your Blog Details</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        input_blog_keywords = st.text_input('🔑 Main Blog Keywords', placeholder="e.g., content marketing, SEO, social media", help="Enter 2-3 main keywords for your blog. This helps the tool research relevant FAQs.")
        input_title_type = st.selectbox('📝 Blog Type', ('General', 'How-to Guides', 'Tutorials', 'Listicles', 'Newsworthy Posts', 'FAQs', 'Checklists/Cheat Sheets'), index=0, help="Select the type of blog for more tailored FAQs.")
        input_blog_url = st.text_input('🔗 Blog URL (optional)', placeholder="https://yourblog.com/post", help="Paste your blog post URL to scrape and rewrite its FAQs. Leave blank if you only want to use keywords.")
    with col2:
        input_title_intent = st.selectbox('🔍 Search Intent', ('Informational Intent', 'Commercial Intent', 'Transactional Intent', 'Navigational Intent'), index=0, help="Choose the main intent behind your blog post.")
        show_schema = st.checkbox('Generate FAQPage Schema Markup (JSON-LD)', value=False, help="Check to include schema markup for FAQs. This helps with Google rich snippets.")
        faq_language = st.selectbox('🌐 FAQ Output Language', options=["English", "Spanish", "French", "German", "Other"], help="Select the language for your FAQs.")
        if faq_language == "Other":
            faq_language = st.text_input("Specify Language", placeholder="e.g., Italian, Chinese", help="Enter your preferred language for the FAQ output.")

    # Fetch SERP results & PAA for dropdown
    serp_results, people_also_ask = get_serp_results(input_blog_keywords, user_serper_api_key) if input_blog_keywords else ({}, [])
    # Show SERP research results clearly in the UI
    if input_blog_keywords and (serp_results or people_also_ask):
        st.markdown('<h4 style="margin-top:1.5rem; color:#1976D2;">🔎 SERP Research Results</h4>', unsafe_allow_html=True)
        if not people_also_ask:
            st.info('No "People Also Ask" results found for your keywords.')
        else:
            st.markdown('**People Also Ask:**')
            for idx, q in enumerate(people_also_ask, 1):
                st.markdown(f"{idx}. {q}")
        related = serp_results.get('relatedQuestions') or serp_results.get('relatedSearches')
        if not related:
            st.info('No related queries found for your keywords.')
        else:
            st.markdown('**Related Queries:**')
            for idx, q in enumerate(related, 1):
                if isinstance(q, dict) and 'question' in q:
                    st.markdown(f"{idx}. {q['question']}")
                elif isinstance(q, dict) and 'text' in q:
                    st.markdown(f"{idx}. {q['text']}")
                else:
                    st.markdown(f"{idx}. {q}")

    # FAQ Scraping Preview
    scraped_faqs = None
    if input_blog_url:
        with st.spinner("Scraping blog for FAQs..."):
            scraped_faqs = scrape_faqs_from_url(input_blog_url)
        if scraped_faqs:
            with st.expander('Preview Scraped FAQs from Blog URL', expanded=False):
                for idx, faq in enumerate(scraped_faqs, 1):
                    st.markdown(f"**Q{idx}:** {faq['question']}")
                    st.markdown(f"**A{idx}:** {faq['answer']}")
        else:
            st.info('No FAQs found or failed to scrape FAQs from the provided blog URL. Try another URL or enter keywords instead.')

    st.markdown('<h3 style="margin-top:2rem;">3️⃣ Generate FAQs</h3>', unsafe_allow_html=True)
    if st.button('✨ Generate Blog FAQs'):
        with st.spinner("Generating your SEO-optimized FAQs..."):
            if not input_blog_keywords and not input_blog_url:
                st.error('Please enter your main blog keywords or a blog URL!')
            else:
                blog_faqs = generate_blog_faqs(input_blog_keywords, input_title_type, input_title_intent, user_gemini_api_key, user_serper_api_key, show_schema, input_blog_url, serp_results, people_also_ask, scraped_faqs, faq_language)
                if blog_faqs:
                    st.subheader('**🎉 Your SEO-Boosting Blog FAQs! 🚀**')
                    with st.expander("**Final - Blog FAQ Output 🎆🎇**", expanded=True):
                        # Render FAQs as a numbered list for readability
                        faqs_part = blog_faqs.split('FAQPage')[0] if show_schema and 'FAQPage' in blog_faqs else blog_faqs
                        st.markdown(faqs_part)
                        # Copy All FAQs button
                        st.download_button("Copy All FAQs", faqs_part, file_name="faqs.txt")
                        # If schema is present, show and allow copy
                        if show_schema and 'FAQPage' in blog_faqs:
                            schema_part = 'FAQPage' + blog_faqs.split('FAQPage',1)[1]
                            st.code(schema_part, language='json')
                            st.download_button("Copy Schema Markup", schema_part, file_name="faq_schema.json")
                else:
                    st.error("We couldn't generate FAQs. Please check your input or try again later.")

    # Help & Support Section
    with st.expander('❓ Help & Troubleshooting', expanded=False):
        st.markdown('''
        - **Not getting results?** Make sure you entered keywords or a valid blog URL.
        - **API key issues?** Double-check your API keys or leave blank to use the default.
        - **No FAQs scraped?** Some blogs may not use standard FAQ formats. Try another URL or use keywords.
        - **Still stuck?** [See our support & documentation](https://github.com/AJaySi/AI-Writer)
        ''')

    st.markdown('<div class="footer">Made with ❤️ by ALwrity | <a href="https://github.com/AJaySi/AI-Writer" style="color:#1976D2;">Support</a></div>', unsafe_allow_html=True)


# Function to generate blog metadesc
def generate_blog_faqs(input_blog_keywords, input_title_type, input_title_intent, user_gemini_api_key=None, user_serper_api_key=None, show_schema=False, input_blog_url=None, serp_results=None, people_also_ask=None, scraped_faqs=None, faq_language="English"):
    """ Function to call upon LLM to get the work done. """
    # Use provided serp_results and people_also_ask if available, else fetch
    if serp_results is None or people_also_ask is None:
        serp_results, people_also_ask = get_serp_results(input_blog_keywords, user_serper_api_key)

    if scraped_faqs:
        prompt = f"""As a SEO expert and experienced content writer, you are given the following FAQs scraped from a blog. Your task is to rewrite these FAQs and their answers to be unique, SEO-optimized, concise (40–50 words per answer), and suitable for Google rich snippets. Format each FAQ clearly. Write the output in {faq_language}. {'Also provide FAQPage schema markup (JSON-LD) after the FAQs.' if show_schema else ''}\n\nScraped FAQs:\n{scraped_faqs}\n"""
        blog_faqs = generate_text_with_exception_handling(prompt, user_gemini_api_key)
        return blog_faqs

    if serp_results:
        prompt = f"""As a SEO expert and experienced content writer, I will provide you with the following 'blog keywords' and 'Google SERP results'.\nYour task is to write 5 SEO-optimized and detailed FAQs for a blog.\n\nFollow these guidelines for generating the FAQs:\n1. Base each FAQ on 'People also ask' and 'Related Queries' from the given SERP results.\n2. Each FAQ must have a unique, non-overlapping question and a concise answer (ideally 40–50 words) optimized for Google rich snippets.\n3. Include an answer for each FAQ, using clear, user-friendly language and natural keyword integration (avoid keyword stuffing).\n4. Optimize your response for the blog type: {input_title_type}.\n5. Format the output for easy copy-paste, with each question and answer clearly separated.\n6. Write the output in {faq_language}.\n"""
        if input_blog_url:
            prompt += f"7. Use the following blog URL as additional context for relevance: {input_blog_url}\n"
        if show_schema:
            prompt += "8. After listing the 5 FAQs and their answers, also provide valid FAQPage schema markup (JSON-LD) for all 5 FAQs, ready for direct use on a blog.\n"
        prompt += f"\nblog keywords: '{input_blog_keywords}'\ngoogle serp results: '{serp_results}'\npeople_also_ask: '{people_also_ask}'\n"
        blog_faqs = generate_text_with_exception_handling(prompt, user_gemini_api_key)
        return blog_faqs


def get_serp_results(search_keywords, user_serper_api_key=None):
    try:
        serp_results = perform_serperdev_google_search(search_keywords, user_serper_api_key)
        people_also_ask = [item.get("question") for item in serp_results.get("peopleAlsoAsk", [])]
        return serp_results, people_also_ask
    except Exception as e:
        st.warning(f"SERP research failed: {e}")
        return {"peopleAlsoAsk": [], "relatedQuestions": [], "relatedSearches": []}, []


def perform_serperdev_google_search(query, user_serper_api_key=None):
    """
    Perform a Google search using the Serper API.

    Args:
        query (str): The search query.

    Returns:
        dict: The JSON response from the Serper API.
    """
    # Get the Serper API key from environment variables
    serper_api_key = user_serper_api_key or os.getenv('SERPER_API_KEY')

    # Check if the API key is available
    if not serper_api_key:
        st.error("SERPER_API_KEY is missing. Set it in the .env file or provide it in the sidebar.")
        return {"peopleAlsoAsk": [], "relatedQuestions": [], "relatedSearches": []}

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
        try:
            response = requests.post(url, headers=headers, data=payload, stream=True)

            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error: {response.status_code}, {response.text}")
                return {"peopleAlsoAsk": [], "relatedQuestions": [], "relatedSearches": []}
        except Exception as e:
            st.error(f"SERPER API request failed: {e}")
            return {"peopleAlsoAsk": [], "relatedQuestions": [], "relatedSearches": []}


def scrape_faqs_from_url(url):
    """Scrape FAQ questions and answers from a blog URL."""
    try:
        resp = requests.get(url, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        faqs = []
        # Look for common FAQ patterns (expand as needed)
        for faq_section in soup.find_all(['section', 'div'], class_=lambda x: x and 'faq' in x.lower()):
            questions = faq_section.find_all(['h2', 'h3', 'h4', 'p', 'span'], string=True)
            for q in questions:
                text = q.get_text(strip=True)
                if '?' in text and len(text) > 10:
                    # Try to find the next sibling as answer
                    answer = q.find_next_sibling(['p', 'div', 'span'])
                    answer_text = answer.get_text(strip=True) if answer else ''
                    faqs.append({'question': text, 'answer': answer_text})
        # Fallback: look for <details> or <summary> tags
        for details in soup.find_all('details'):
            summary = details.find('summary')
            if summary:
                question = summary.get_text(strip=True)
                answer = details.get_text(strip=True).replace(question, '').strip()
                faqs.append({'question': question, 'answer': answer})
        return faqs if faqs else None
    except Exception as e:
        st.warning(f"Failed to scrape FAQs from the blog URL: {e}")
        return None


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def generate_text_with_exception_handling(prompt, user_gemini_api_key=None):
    """
    Generates text using the Gemini model with exception handling.

    Args:
        prompt (str): The prompt for text generation.
        user_gemini_api_key (str, optional): User-provided Gemini API key.

    Returns:
        str: The generated text.
    """

    try:
        api_key = user_gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            st.error("GEMINI_API_KEY is missing. Please provide it in the sidebar or set it in the environment.")
            return None
        genai.configure(api_key=api_key)

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
