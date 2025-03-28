import openai
import string

SENSITIVITY = 5 # between 1 to 100


class NegativeSentimentAnalyzer:
    def __init__(self, openai_api_key: str) -> None:
        openai.api_key = openai_api_key
        self.blacklist_unigram = ["scam", "fraud",
                                  "ponzi", "scheme"]
        self.blacklist_bigram = ["money laundering"]

    def is_negative(self, text: str) -> bool:
        text = text.replace("!", "")
        if self.contains_word_from_blacklist(text):
            return True
        # prompt = f'Consider the text delimited by triple backticks and intelligently determine if it contains offensive or hate speech. The goal should be to not just identify isolated bad words but to understand the context of sentences in which they are used. The aim is to maintain a positive and respectful community environment in the group without stifling genuine conversation. Ensure false positives (e.g., "Fuck this was a good trade") are minimized while true negatives (e.g., "Fuck the system") are captured. The use of the word "fuck" can also be used to describe happiness, like "Fuck that was a good trade", so text like this should not be marked as offensive. The output you provide will be used to montior messages in a group chat related to finance and stocks, so if a message says anything bad or derogatory about the group, or says that the group lies or tricks people, it should be considered offensive. The group is called FredTrading. You do not need to be too sensitive, so words like "shit" and "stupid" should be allowed. However, any sorts of illegal drugs or acts should not be allowed. "Stupid" is allowed.\n```{text}```\nProvide a single character as output, either 1 or 0, where 1 means that the text contains offensive or hate speech, and 0 means it does not. Do not explain your answer.'
        prompt = f'You are a chat group moderator bot. You will be provided with a text message sent by a member in the gorup and your goal is to detect if the message contains offensive or hate speech towards the group or other members of the group. The group is called FredTrading, and is related to forex trading and advising. Ensure false positives (e.g., "Fuck this was a good trade") are minimized while true negatives (e.g., "Fuck the system") are captured. Understand that swearing is allowed, as long as it is not targetted towards the group or other members in the group. Members should be able to express their emotions by saying things like "Shit!" or "Fuck yeah!". We need to make sure that the group is a safe environment for other members. On a scale of 1 to 100, the sensitivity should be {SENSITIVITY}. Consider the message delimited by triple backticks, and determine if it is offensive or not. \n```{text}```\nProvide a single character as output, either 1 or 0, where 1 means that the text contains offensive or hate speech, and 0 means it does not. Do not explain your answer.'
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        return bool(int(response.choices[0].message["content"]))

    def contains_word_from_blacklist(self, text: str):
        text = text.translate(str.maketrans('', '', string.punctuation))
        words = text.lower().split()
        for word in words:
            if word in self.blacklist_unigram:
                return True
        bi_grams = [words[i] + " " + words[i+1] for i in range(len(words) - 1)]
        for bi_gram in bi_grams:
            if bi_gram in self.blacklist_bigram:
                return True
        return False
