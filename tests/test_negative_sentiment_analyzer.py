from negative_sentiment_analyzer import NegativeSentimentAnalyzer
import pytest

from dotenv import load_dotenv
import os

load_dotenv()

# Test cases

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Create the analyzer object globally
@pytest.fixture(scope="module")
def analyzer():
    return NegativeSentimentAnalyzer(OPENAI_API_KEY)

# Test cases


def test_hate_speech(analyzer):
    result = analyzer.is_negative("Fuck you")
    assert result == True


def test_non_offensive_language_1(analyzer):
    result = analyzer.is_negative("We had a loss today")
    assert result == False


def test_non_offensive_language_2(analyzer):
    result = analyzer.is_negative("SL was hit")
    assert result == False


def test_non_offensive_language_3(analyzer):
    result = analyzer.is_negative("I am pretty")
    assert result == False


def test_hate_speech_2(analyzer):
    result = analyzer.is_negative("You're stupid")
    assert result == True


def test_non_offensive_language_4(analyzer):
    result = analyzer.is_negative("fucking amazing")
    assert result == False


def test_hate_speech_3(analyzer):
    result = analyzer.is_negative("Suck my dick")
    assert result == True


def test_hate_speech_4(analyzer):
    result = analyzer.is_negative("Fuck off")
    assert result == True


def test_hate_speech_5(analyzer):
    result = analyzer.is_negative("You are a worthless piece of shit")
    assert result == True


def test_non_offensive_language_5(analyzer):
    result = analyzer.is_negative("Hell yeah")
    assert result == False


def test_non_offensive_language_6(analyzer):
    result = analyzer.is_negative("We took another loss today")
    assert result == False


def test_non_offensive_language_7(analyzer):
    result = analyzer.is_negative("So sorry to hear that")
    assert result == False


def test_hate_speech_6(analyzer):
    result = analyzer.is_negative("Lets do weed")
    assert result == True


def test_hate_speech_7(analyzer):
    result = analyzer.is_negative("fuck this was a good trade")
    assert result == False
