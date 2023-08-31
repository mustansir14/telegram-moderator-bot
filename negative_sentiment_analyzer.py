import openai


class NegativeSentimentAnalyzer:
    def __init__(self, openai_api_key: str) -> None:
        openai.api_key = openai_api_key

    def is_negative(self, text: str) -> bool:
        prompt = f'Consider the text delimited by triple backticks and intelligently determine if it contains offensive or hate speech. The goal should be to not just identify isolated bad words but to understand the context of sentences in which they are used. The aim is to maintain a positive and respectful community environment without stifling genuine conversation. Ensure false positives (e.g., "Fuck yeah that was great") are minimized while true negatives (e.g., "Fuck, that was so bad") are captured.\n```{text}```\nProvide a single character as output, either 1 or 0, where 1 means that the text has negative sentiment, and 0 means it does not. Do not explain your answer.'
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return bool(int(response.choices[0].message["content"]))


if __name__ == "__main__":
    sentiment_analyzer = NegativeSentimentAnalyzer("asdasd")
    sentiment_analyzer.is_negative("I am gonna kill him")
