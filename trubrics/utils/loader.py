import json

import requests  # type: ignore

from trubrics.context import FeedbackContext


def save_test_to_json(trubric_context: FeedbackContext, tracking: bool = False) -> None:
    test_json = trubric_context.json()
    if tracking:
        url = "http://localhost:5000"
        headers = {"Content-type": "application/json"}
        requests.post(
            url + "/tests/v1/add",
            data=test_json,
            headers=headers,
        )
    else:
        with open(
            "examples/data/feedback.json",
            "w",
        ) as file:
            file.write(test_json)


def get_business_test_data(
    tracking: bool = False,
) -> FeedbackContext:
    if tracking:
        raise Exception("to be replaced with read from test tracking API")
    else:
        with open(
            "../data/feedback.json",
            "r",
        ) as file:
            saved_test = json.load(file)
            return saved_test
