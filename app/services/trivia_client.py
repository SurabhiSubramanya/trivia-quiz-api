# Open Trivia DB API wrapper

import html
import random
import httpx

OPENTDB_URL = "https://opentdb.com/api.php"
OPENTDB_CATEGORIES_URL = "https://opentdb.com/api_category.php"


async def fetch_questions(amount: int = 10, category: int = None, difficulty: str = None) -> list[dict]:
    """
    Fetch questions from Open Trivia DB and return a list of dicts with:
      - question_text
      - correct_answer
      - options (shuffled list of all choices)
    Raises httpx.HTTPError on network failure, ValueError if API returns no results.
    """
    params = {"amount": amount, "type": "multiple"}
    if category is not None:
        params["category"] = category
    if difficulty is not None:
        params["difficulty"] = difficulty

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(OPENTDB_URL, params=params)
        response.raise_for_status()

    data = response.json()

    # response_code 0 = success, 1 = no results
    if data.get("response_code") != 0:
        raise ValueError(f"Open Trivia DB returned response_code {data.get('response_code')}")

    questions = []
    for item in data["results"]:
        question_text = html.unescape(item["question"])
        correct_answer = html.unescape(item["correct_answer"])
        options = [html.unescape(opt) for opt in item["incorrect_answers"]] + [correct_answer]
        random.shuffle(options)

        questions.append({
            "question_text": question_text,
            "correct_answer": correct_answer,
            "options": options,
        })

    return questions


async def fetch_categories() -> list[dict]:
    """
    Fetch available trivia categories from Open Trivia DB.
    Returns a list of dicts with 'id' and 'name'.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(OPENTDB_CATEGORIES_URL)
        response.raise_for_status()

    return response.json().get("trivia_categories", [])
