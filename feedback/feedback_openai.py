import openai
import time
class openAI: 
    def feedback_ai(self):

        openai.api_key = ""
        try:

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": 'assistant', "content": f'{self}'}],
            )

            answer = response["choices"][0]["message"]["content"]
            usage = response["usage"]["total_tokens"]

            return answer, usage


        except openai.error.RateLimitError as e:

            retry_time = e.retry_after if hasattr(e, 'retry_after') else 30
            print(f"Rate limit exceeded. Retrying in {retry_time} seconds...")
            time.sleep(retry_time)
            return feedback_ai(self)
