import openai
from dotenv import load_dotenv
import os
import re

load_dotenv()


def remove_special_characters(input_string):
    pattern = r"[^a-zA-Z0-9\s]"
    return re.sub(pattern, "", input_string)


class OpenAI:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def feedback_ai(self, message):
        message_scrub = remove_special_characters(message)
        prompt = f"""you are a feedback curator dedicated to evaluating various types of feedback, including constructive criticism and positive feedback. This persona understands that feedback serves multiple purposes, not only for guiding improvement and acknowledging what's done right but also acknowledging what is done wrong, especially the value of providing actionable and constructive suggestions for improvement. you are not overly picky about what feedback is constructive, as long as criticisms include some steps to address them.  Is the following feedback constructive?\n{message_scrub}\n 'Yes' or 'No'?"""
        try:
            # Check if the message qualifies as meaningful feedback
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=3,
                n=1,
                stop=None,
                temperature=0.5,
                top_p=0.2,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].text.strip()

        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."
