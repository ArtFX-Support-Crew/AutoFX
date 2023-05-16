import openai
import config
class OpenAI: 
    def __init__ (self):
        self.persona = config.persona
        openai.api_key = config.openai_api_key
    def feedback_ai(self, message):
        prompt = f'{self.persona}\n\n{message}'
        openai.api_key = config.openai_api_key
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
            
    

