---
name: unit-tests-skill
description: Instructions of how to structure the unit tests. Use it every time when you are instructed to write, review, analyze unit tests
compatibility: uv, python, pytest
---

When writing, reviewing, analyzing unit tests, follow the following instructions.

# Test naming convention
When test case is an single case, always name test function as `test_<function-thats-being-testes>_when_<condition>`.
When test case has multiple cases, e.g. parameterized unit test, always name test function as `test_<function-thats-being-testes>_when_<mutual-condition>`.

Examples when test function contains a single condition:
- `test_parse_when_flags_are_missing`
- `test_file_load_when_file_doesnt_exist`
- `test_file_load_when_file_format_is_unsupported`

Examples when test function contains a multiple condition:
- `test_parse_when_proper_flags_are_provided`
- `test_file_load_when_supported_file_format_are_provided`

# AAA test patter
Every test must use and AAA pattern. AAA stands for Assign, Act and Assert section. Always separate these section with comments, put the comments are above the section itself.

Example:
``` python
def test_from_dict_when_only_error_rate_is_provided():
    # Assign
    data = {
        "error-rate": {
            "sensors": {"temperature": 0.1},
            "computer": {"cpu_utilization": 0.25},
            "battery": {"battery_temperature": 0.5},
            "solar_panel": {"current_voltage": 0.75},
        },
    }

    # Act
    config = Config.from_dict(data)

    # Assert
    assert config.dimensions.sensors.temperature.error_rate == ErrorRate.LOW
    assert config.dimensions.computer.cpu_utilization.error_rate == ErrorRate.MEDIUM
    assert config.dimensions.battery.battery_temperature.error_rate == ErrorRate.HIGH
    assert config.dimensions.solar_panel.current_voltage.error_rate == ErrorRate.CRITICAL
```
If there is no local setup, collapse the two lines: write `# Assign` immediately followed by `# Act` on the next line, with no blank line between them. This applies when all inputs come from imported constants (e.g., `value_consts.py`) or are passed in as parametrize arguments.

## Parametrized tests
Use `@pytest.mark.parametrize` for multiple scenarios of the same behavior. 
When case are complicated, each complicated case must have an inline comment (on the opening bracket line) describing the scenario.
Parametrize cases are lists `[...]`, not tuples.

```python
@pytest.mark.parametrize(
    "param1, param2, param3",
    [
        [ # describe this scenario
            value1,
            value2,
            value3
        ],
        [ # describe this scenario
            value1,
            value2,
            value3
        ],
    ],
)
def test_function_thats_being_testes_when_mutual_condition(
    param1: Type,
    param2: Type,
    param3: Type
):
    # Assign
    # Act
    result = module.function(param1)

    # Assert
    assert result.field == param2
    assert result.other_field is param3
```

## Error / exception tests
Use `pytest.raises` as a context manager, then assert on the exception detail after the `with` block.
Strive to be as precise as possible, 
- it is important to assert the error message
- use Exception class as narrow as possible

```python
def test_function_thats_being_testes_when_condition():
    with pytest.raises(ExceptionType) as caught_error:
        # Act
        module.function(bad_input)

    # Assert
    assert str(caught_error.value) == 'Expected error message'
```

# Final instructions
- Keep each test focused on one behavior
- Write tests as module-level functions, not inside classes
- Always add type annotations to test function parameters
- Be strict and explicit as much as possible
