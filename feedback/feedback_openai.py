import openai
import config
import time
class openAI: 
    def feedback_ai(self):

        openai.api_key = ""
        try:
            # Check if the message qualifies as meaningful feedback
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=prompt,
                max_tokens=1,
                n=1,
                stop=None,
                temperature=1,
                top_p=0.5,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response.choices[0].text.strip()   
        except openai.error.AuthenticationError:
            return "AuthenticationError: Please check your OpenAI API credentials."
            
    
openai_instance = OpenAI()
persona = '''I am a bot which gives yes/no answers to if I think some text is meaningful feedback (yes) or not meaningful (no)'''
