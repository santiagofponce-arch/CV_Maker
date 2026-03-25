import os
from google import genai
from google.genai import types

def get_client(api_key: str) -> genai.Client:
    if not api_key:
        raise ValueError("Gemini API key not found. Please provide a GEMINI_API_KEY.")
    return genai.Client(api_key=api_key)

def generate_tailored_cv(base_cv: str, job_description: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
    """Takes the user's base CV and a job description to generate a tailored CV."""
    client = get_client(api_key)

    system_prompt = (
        "You are an expert career coach and technical recruiter. Your task is to extract "
        "and highlight the most relevant skills, experiences, and accomplishments from the "
        "provided Base CV that align explicitly with the requirements in the Job Description. "
        "Rules:\n"
        "1. DO NOT invent or hallucinate any experience, skills, or metrics that are not in the Base CV.\n"
        "2. Keep the format clean, professional, and ATS-friendly (use plain text with basic markdown for headers and lists). DO NOT use bolding (**text**) or italics (*text*).\n"
        "3. Emphasize keywords found in the job description where the candidate has genuine experience, but do NOT bold them.\n"
        "4. Be concise but impactful with bullet points.\n"
        "5. Output ONLY the exact CV content. DO NOT include any conversational preamble, AI comments, or introductory/concluding text like 'Here is your tailored CV'."
    )

    user_prompt = f"""
    --- JOB DESCRIPTION ---
    {job_description}

    --- BASE CV ---
    {base_cv}

    Please provide a tailored version of the CV based on the above rules.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.3,
            )
        )
        return response.text
    except Exception as e:
        if "404" in str(e) and model != "gemini-2.5-flash":
            print(f"Model {model} failed, falling back to gemini-2.5-flash")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                )
            )
            return response.text
        raise e

def generate_cover_letter(base_cv: str, job_description: str, api_key: str, model: str = "gemini-2.5-flash") -> str:
    """Generates a human-sounding, highly personalized cover letter based on the job and CV."""
    client = get_client(api_key)

    system_prompt = (
        "You are writing a cover letter on behalf of the applicant. You MUST write in a "
        "highly conversational, genuine, and human tone. You are strictly forbidden from "
        "using common AI buzzwords and clichés such as: 'Delve', 'Tapestry', 'In today's fast-paced world', "
        "'A testament to', 'Look no further', 'Thrill', or 'Bucket'. \n"
        "Rules:\n"
        "1. Keep it short and impactful (250-350 words max).\n"
        "2. Write exactly as a modern, experienced professional would email a hiring manager.\n"
        "3. Focus on 1 or 2 specific accomplishments from the Base CV that directly prove "
        "the core requirement in the Job Description.\n"
        "4. Start with a direct, confident hook, not 'I am writing to express my interest'.\n"
        "5. Print only the cover letter text. No preamble or meta-commentary."
    )

    user_prompt = f"""
    --- JOB DESCRIPTION ---
    {job_description}

    --- BASE CV ---
    {base_cv}

    Write the cover letter following the rules strictly.
    """

    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.7,
            )
        )
        return response.text
    except Exception as e:
        if "404" in str(e) and model != "gemini-2.5-flash":
            print(f"Model {model} failed, falling back to gemini-2.5-flash")
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                )
            )
            return response.text
        raise e
