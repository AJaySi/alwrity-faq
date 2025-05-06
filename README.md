# Alwrity - AI Blog FAQ Generator

### [Try Here Online:](https://www.alwrity.com/ai-blog-faqs-generator) 

Alwrity is a Streamlit application that leverages the power of Google's Generative AI (Gemini) to automatically generate SEO-optimized FAQs for your blog posts. This tool helps you enhance user engagement, improve search ranking, and provide valuable information to your readers.

## Features

- **Keyword-based FAQ generation:**
  - Enter your main blog keywords and get relevant, SEO-optimized FAQs.
  - Alwrity researches Google search results and "People Also Ask" data for you.
- **Blog type and search intent optimization:**
  - Choose your blog type (e.g., How-to, Listicle, News) and search intent (e.g., Informational, Transactional) for tailored FAQs.
- **Blog URL FAQ rewriting:**
  - Paste a blog URL to scrape and rewrite its FAQs in an SEO-friendly way.
- **Schema Markup (JSON-LD):**
  - Optionally generate FAQPage schema markup for Google rich snippets.
- **Transparent SERP research:**
  - See the actual "People Also Ask" and related queries researched by the tool.
- **Multilingual output:**
  - Choose your preferred language for the FAQ output.
- **User-friendly UI:**
  - Helpful tooltips, onboarding, and troubleshooting built in.

## Getting Started (No Coding Required!)

1. **Clone or Download the Repository**
   - Click the green "Code" button above and choose "Download ZIP" or use:
     ```sh
     git clone https://github.com/AJaySi/alwrity-faq.git
     ```
2. **Install Python Requirements**
   - Open a terminal in the project folder and run:
     ```sh
     pip install -r requirements.txt
     ```
3. **(Optional) Set API Keys**
   - For best results, get free API keys for [Gemini](https://aistudio.google.com/app/apikey) and [Serper](https://serper.dev).
   - You can enter these in the app sidebar, or set them as environment variables:
     - `GEMINI_API_KEY`
     - `SERPER_API_KEY`
4. **Run the App**
   - In your terminal, run:
     ```sh
     streamlit run blogfaq_app.py
     ```
   - The app will open in your browser.

## How to Use

1. **Enter your main blog keywords** or paste a blog URL to scrape and rewrite its FAQs.
2. *(Optional)* Choose your blog type, search intent, and output language.
3. *(Optional)* Enter your own API keys in the sidebar if you have them.
4. Click **Generate Blog FAQs**.
5. View, copy, and use the generated FAQs (and schema markup if selected) in your blog post.
6. See the actual Google research results in the app for transparency.

## Support & Documentation

- [GitHub Issues & Support](https://github.com/AJaySi/AI-Writer)
- [Try the tool online](https://www.alwrity.com/ai-blog-faqs-generator)

---

*Made with ❤️ by ALwrity*

