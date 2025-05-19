import pytest

from medsplex.chunker import Chunker

CONFIG = {
    "compliant": {
        "regex": "\\b(?:compliant|noncompliant|noncompliance|poor compliance)\\b"
    },
    "engaged": {"regex": "\\b(?:engaged|engagement|engages)\\b"},
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
    chunker = Chunker(CONFIG)
    chunks = chunker.run(
        text=text,
        nchr=nchr,
    )

    assert chunks == expected_chunks


@pytest.mark.parametrize("nchr", (0, -1, -100, "foo"))
def test_run_nchar_is_positive_integer(nchr):
    chunker = Chunker(CONFIG)
    with pytest.raises(Exception) as err:
        chunker.run(
            text="The patient is compliant with the treatment plan. However, there are concerns about their engagement.",
            nchr=nchr,
        )
    assert str(err.value) == f"nchr should be integer >0, but found {nchr}."


def test_run_nchar_greater_than_text_length(caplog):
    chunker = Chunker(CONFIG)
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
