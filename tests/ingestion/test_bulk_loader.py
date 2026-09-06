import pytest

from astraquant.ingestion.bulk_market_data import (
    select_securities,
)


SECURITIES = [
    {"symbol": "AAA"},
    {"symbol": "BBB"},
    {"symbol": "CCC"},
    {"symbol": "DDD"},
    {"symbol": "EEE"},
]


def test_select_securities_with_limit_and_offset():
    result = select_securities(
        SECURITIES,
        limit=2,
        offset=1,
    )

    assert result == [
        {"symbol": "BBB"},
        {"symbol": "CCC"},
    ]


def test_select_securities_with_limit_only():
    result = select_securities(
        SECURITIES,
        limit=3,
    )

    assert result == [
        {"symbol": "AAA"},
        {"symbol": "BBB"},
        {"symbol": "CCC"},
    ]


def test_select_securities_with_offset_only():
    result = select_securities(
        SECURITIES,
        offset=3,
    )

    assert result == [
        {"symbol": "DDD"},
        {"symbol": "EEE"},
    ]


def test_select_securities_without_limit_or_offset():
    result = select_securities(SECURITIES)

    assert result == SECURITIES


def test_select_securities_offset_beyond_range():
    result = select_securities(
        SECURITIES,
        offset=10,
    )

    assert result == []


def test_select_securities_rejects_negative_offset():
    with pytest.raises(
        ValueError,
        match="OFFSET cannot be negative",
    ):
        select_securities(
            SECURITIES,
            offset=-1,
        )


def test_select_securities_rejects_invalid_limit():
    with pytest.raises(
        ValueError,
        match="LIMIT must be greater than zero",
    ):
        select_securities(
            SECURITIES,
            limit=0,
        )

def test_iter_security_batches():
    from astraquant.ingestion.bulk_market_data import iter_security_batches

    batches = list(
        iter_security_batches(
            SECURITIES,
            batch_size=2,
        )
    )

    assert batches == [
        [
            {"symbol": "AAA"},
            {"symbol": "BBB"},
        ],
        [
            {"symbol": "CCC"},
            {"symbol": "DDD"},
        ],
        [
            {"symbol": "EEE"},
        ],
    ]


def test_iter_security_batches_rejects_invalid_batch_size():
    from astraquant.ingestion.bulk_market_data import iter_security_batches

    with pytest.raises(
        ValueError,
        match="BATCH_SIZE must be greater than zero",
    ):
        list(iter_security_batches(SECURITIES, batch_size=0))
