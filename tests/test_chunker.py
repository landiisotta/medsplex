import pytest
from pydantic import ValidationError

from medsplex.chunker import Chunker

CONFIG = {
    "compliant": {
        "regex": "\\b(?:compliant|noncompliant|noncompliance|poor compliance)\\b",
        "privileging_score": 2,
        "stigmatizing_score": 1.5,
    },
    "engaged": {
        "regex": "\\b(?:engaged|engagement|engages)\\b",
        "privileging_score": 2.3,
        "stigmatizing_score": 5,
    },
}


@pytest.mark.parametrize(
    "text, nchr, expected_chunks",
    (
        (
            "The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
            5,
            [
                {"keyword": "compliant", "text": "t is compliant with"},
                {"keyword": "engaged", "text": "heir engagement."},
            ],
        ),
        (
            "The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
            10,
            [
                {"keyword": "compliant", "text": "atient is compliant with the "},
                {"keyword": "engaged", "text": "out their engagement."},
            ],
        ),
        ("", 10, []),
    ),
)
def test_run(text, nchr, expected_chunks):
    chunker = Chunker(config=CONFIG)
    chunks = chunker.run(
        text=text,
        nchr=nchr,
    )

    assert chunks == expected_chunks


@pytest.mark.parametrize("nchr", (0, -1, -100, "foo"))
def test_run_nchar_is_positive_integer(nchr):
    chunker = Chunker(config=CONFIG)
    with pytest.raises(Exception) as err:
        chunker.run(
            text="The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
            nchr=nchr,
        )
    assert str(err.value) == f"nchr should be integer >0, but found {nchr}."


def test_run_nchar_greater_than_text_length(caplog):
    chunker = Chunker(config=CONFIG)
    chunks = chunker.run(
        text="The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
        nchr=3000,
    )
    assert chunks == [
        {
            "keyword": "compliant",
            "text": "The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
        },
        {
            "keyword": "engaged",
            "text": "The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
        },
    ]
    assert "Text length 101 is less than 3000." in caplog.text


def test_chunker_not_valid_regex():
    with pytest.raises(ValidationError) as err:
        # This regex is invalid
        Chunker(config={"compliant": {"regex": "*abc"}})
    assert (
        str(err.value)
        == "1 validation error for Chunker\nconfig.compliant.regex\n  Value error, Invalid regex pattern: *abc. Error: nothing to repeat at position 0 [type=value_error, input_value='*abc', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/value_error"
    )


def test_chunker_not_valid_privileging_valence():
    with pytest.raises(ValidationError) as err:
        # This valence is greater than 5 or less than 1
        Chunker(
            config={
                "compliant": {
                    "privileging_score": 0.2,
                }
            }
        )
    assert (
        str(err.value)
        == "2 validation errors for Chunker\nconfig.compliant.privileging_score.[key]\n  Input should be a valid dictionary or instance of Regex [type=model_type, input_value='privileging_score', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/model_type\nconfig.compliant.privileging_score\n  Input should be a valid dictionary or instance of Valence [type=model_type, input_value=0.2, input_type=float]\n    For further information visit https://errors.pydantic.dev/2.11/v/model_type"
    )


def test_chunker_not_valid_stigmatizing_valence():
    with pytest.raises(ValidationError) as err:
        # This valence is greater than 5 or less than 1
        Chunker(
            config={
                "compliant": {
                    "stigmatizing_score": 6,
                }
            }
        )
    assert (
        str(err.value)
        == "2 validation errors for Chunker\nconfig.compliant.stigmatizing_score.[key]\n  Input should be a valid dictionary or instance of Regex [type=model_type, input_value='stigmatizing_score', input_type=str]\n    For further information visit https://errors.pydantic.dev/2.11/v/model_type\nconfig.compliant.stigmatizing_score\n  Input should be a valid dictionary or instance of Valence [type=model_type, input_value=6, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.11/v/model_type"
    )
