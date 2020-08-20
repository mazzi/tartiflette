import pytest


@pytest.mark.asyncio
@pytest.mark.with_schema_stack(preset="coercion")
@pytest.mark.parametrize(
    "query,variables,expected",
    [
        ("""query { intField }""", None, {"data": {"intField": "SUCCESS"}}),
        (
            """query { intField(param: null) }""",
            None,
            {"data": {"intField": "SUCCESS-None"}},
        ),
        (
            """query { intField(param: 10) }""",
            None,
            {"data": {"intField": "SUCCESS-13"}},
        ),
        (
            """query ($param: Int) { intField(param: $param) }""",
            None,
            {"data": {"intField": "SUCCESS"}},
        ),
        (
            """query ($param: Int) { intField(param: $param) }""",
            {"param": None},
            {"data": {"intField": "SUCCESS-None"}},
        ),
        (
            """query ($param: Int) { intField(param: $param) }""",
            {"param": 20},
            {"data": {"intField": "SUCCESS-23"}},
        ),
        (
            """query ($param: Int = null) { intField(param: $param) }""",
            None,
            {"data": {"intField": "SUCCESS-None"}},
        ),
        (
            """query ($param: Int = null) { intField(param: $param) }""",
            {"param": None},
            {"data": {"intField": "SUCCESS-None"}},
        ),
        (
            """query ($param: Int = null) { intField(param: $param) }""",
            {"param": 20},
            {"data": {"intField": "SUCCESS-23"}},
        ),
        (
            """query ($param: Int = 30) { intField(param: $param) }""",
            None,
            {"data": {"intField": "SUCCESS-33"}},
        ),
        (
            """query ($param: Int = 30) { intField(param: $param) }""",
            {"param": None},
            {"data": {"intField": "SUCCESS-None"}},
        ),
        (
            """query ($param: Int = 30) { intField(param: $param) }""",
            {"param": 20},
            {"data": {"intField": "SUCCESS-23"}},
        ),
        (
            """query ($param: Int!) { intField(param: $param) }""",
            None,
            {
                "data": None,
                "errors": [
                    {
                        "message": "Variable < $param > of required type < Int! > was not provided.",
                        "path": None,
                        "locations": [{"line": 1, "column": 8}],
                    }
                ],
            },
        ),
        (
            """query ($param: Int!) { intField(param: $param) }""",
            {"param": None},
            {
                "data": None,
                "errors": [
                    {
                        "message": "Variable < $param > of non-null type < Int! > must not be null.",
                        "path": None,
                        "locations": [{"line": 1, "column": 8}],
                    }
                ],
            },
        ),
        (
            """query ($param: Int!) { intField(param: $param) }""",
            {"param": 20},
            {"data": {"intField": "SUCCESS-23"}},
        ),
    ],
)
async def test_coercion_int_field(schema_stack, query, variables, expected):
    assert await schema_stack.execute(query, variables=variables) == expected
