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
        page_title="Alwrity - AI Business Letter Writer (Beta)",
        layout="wide",
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

    # Hide top header line
    hide_decoration_bar_style = '<style>header {visibility: hidden;}</style>'
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Hide footer
    hide_streamlit_footer = '<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>'
    st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

    with st.expander("**PRO-TIP** - Read the instructions below.", expanded=True):
        col1, col2, col3 = st.columns([5, 5, 5])
        with col1:
            product_service_name = st.text_input("Brand/Product/Service Name:")
            call_to_action_options = ["Shop Now", "Learn More", "Sign Up", "Get a Quote", "Download", "Other"]
            call_to_action = st.selectbox("Call to Action:", call_to_action_options)
            if call_to_action == "Other":
                call_to_action = st.text_input("Enter custom CTA:")
        with col2:
            key_benefit_usp = st.text_input("Keywords (Optional):")
            target_audience = st.text_input("Specify Target Audience:", 
                                                placeholder=f"Specify Target Audience to attract")

    if st.button('**Write Google Ads Copy**'):
        with st.status("Assigning AI professional to write your Google Ads copy..", expanded=True) as status:
            if not product_service_name or not target_audience or not key_benefit_usp:
                st.error("🚫 Error: Enter all the details, least you can do..")
            else:
                response = google_ads_writer(product_service_name, call_to_action, key_benefit_usp, target_audience, status)
                if response:
                    st.subheader(f'**🧕🔬👩 Alwrity can make mistakes. Your Final Google Ads!**')
                    st.write(response)
                else:
                    st.error("💥**Failed to write Letter. Please try again!**")


def google_ads_writer(product_service_name, call_to_action, key_benefit_usp, target_audience, status):
    """ Email project_update_writer """

    prompt = f"""## Google Ads Description Generation Request

        **Product/Service:** {product_service_name}
        **Target Audience:** {target_audience}
        **Key Benefit/USP:** {key_benefit_usp}
        **Call to Action:** {call_to_action}
        
        ## Instructions for AI
        
        * Generate three compelling and concise Google Ads descriptions, each within the character limit (approximately 90 characters).
        * Highlight the key benefit/USP and tailor the message to the target audience.
        * Include a strong call to action (CTA) that aligns with the campaign goals.
        * Incorporate the Product/Service Name, ensuring it complements the ad copy.
        * Ensure ad descriptions are tailored for given Target Audience.
        * Focus on creating a sense of urgency and scarcity where appropriate.
        * Ensure ad descriptions are clear, specific, and easy to understand.
        * Maintain a consistent tone and style throughout the ad copy.
        * Consider using ad extensions for additional information and visibility.
        
        ## Output Format
        
        * Two separate ad descriptions, each on a new line.
        """
    status.update(label="Writing Google Ads Description...")
    try:
        response = generate_text_with_exception_handling(prompt)
        return response
    except Exception as err:
        st.error(f"Exit: Failed to get response from LLM: {err}")
        exit(1)


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

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[])
        convo.send_message(prompt)
        return convo.last.text

    except Exception as e:
        st.exception(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    main()
