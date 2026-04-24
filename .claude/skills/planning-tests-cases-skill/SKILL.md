---
name: planning-tests-cases-skill
description: Instructions of how to plan the test cases. Use it every time when you are instructed to write a plan for writing a tests. you should load the `unit-tests-skill` as well, it goes together
compatibility: uv, python, pytest
---

Every time when you are asked to create a plan for writing a unit test, do the following:  
[ ] Load `/unit-tests-skill` — naming conventions and structure rules from that skill apply to all test cases planned here  
[ ] Identify what function should be tested  
[ ] Identify the test cases that each function should have  
[ ] Determine what test cases are single vs what test can be parameterized, always prefer parametrized tests  
[ ] Draft all test implementations before showing the plan — see Reporting Format below  
[ ] Report using the Reporting Format below  

---

## Test Case Selection Rules

When deciding which test cases to cover for a given function, apply these rules. Not all rules apply to every function — read the code block being tested and only apply rules that are relevant.

### 1. Enum-typed parameters → test every valid value (parametrized)
If a function accepts or returns an enum, every enum member must appear as a parameter set.
Never test just one or two "representative" values.

### 2. Factory / parser functions → plan both positive and negative cases
Always plan both positive (happy path) and negative (error) cases.

### 3. Required fields → test each missing individually; mind the error-handling strategy
For every required field: one parameter set where only that field is absent.
- **Lazy error handling** (collects all errors before raising): add at least one parameter set with two or more missing fields simultaneously to verify error accumulation.
- **Eager error handling** (raises on first error): do not test combinations — test each missing field in order of validation priority, since order matters here.

### 4. Boundary values → look at the code, cover every boundary
Look at the code block being tested and identify all boundary values (the edges of accepted input ranges) and clearly invalid values outside those boundaries. Every distinct boundary must have its own test case. Add one or two representative in-boundary examples.

*Example: for a field that must be a positive integer, the lower boundaries are 0 and -1; clearly invalid non-boundary values are a numeric string like `"1"` and a word like `"one"`; in-boundary examples are 1 and 10.*

### 5. Collection / list fields → cover the shapes the code differentiates (when relevant)
When the code under test handles a collection input, look at the code to identify which shapes it treats differently (e.g., empty, single item, partial, complete, containing invalid entries). Only cover the shapes the code actually differentiates.

### 6. Resource / I/O operations → cover only the error paths present in the code (when relevant)
When the code under test performs I/O (file, network, etc.), look at which error paths are explicitly handled. Only write test cases for error scenarios that the code actually catches and handles differently.

### 7. Entry points that accept options → cover valid combinations and defined failure modes (when relevant)
When the code under test accepts user-provided options and dispatches on them, identify: which options are valid standalone, which must appear together, and which missing or invalid options produce a defined failure. Cover all valid option combinations and the defined failure modes.

*Example: a CLI parser — test each flag alone if valid standalone, all flags together in at least two orderings, and missing a required flag.*

### 8. Error messages → assert exact strings, not just exception types
When a function raises a custom exception, the test must assert `str(caught_error.value) == expected_message`.

### 9. Default / optional values → one dedicated positive test
When a function has optional parameters with defaults, include one test that omits all optional parameters and asserts the defaults are applied correctly.

### 10. Parametrize preference threshold
If two or more test cases differ only in one input value and one expected output value → always parametrize.
If a test requires materially different setup or assertions → keep it as a standalone test.

---

## Test File Organization

### File splitting
Keep all cases in one file until the file reaches 10 test functions — at that point, stop and decide whether splitting makes sense before adding more. The decision belongs to the user, not the model. How to split depends on what makes orientation easier — common options are:
  - by polarity: `test_<module>_positive_cases.py` / `test_<module>_negative_cases.py`
  - by feature: `test_<module>_<feature>.py`

### Folder structure
Test folder structure must mirror the `src/` folder structure.

### Ordering within a file
Write tests from high-level feature to low-level feature. Group features together: positive tests first, then negative tests.

### Shared test data
When the same input data or expected output objects are needed across multiple test files, extract them into a `value_consts.py` file inside the same test package. Do not create this file for data used only in a single test file — keep that data local to the file instead. Name constants in UPPER_SNAKE_CASE with explicit type annotations.

```python
# value_consts.py
VALID_CONFIG_INPUT: dict = {
    "output-format": "json",
    ...
}

EXPECTED_CONFIG: Config = Config(
    output_format=OutputFormat.JSON,
    ...
)
```

When a test needs to derive a variant of a shared constant (e.g., one field changed), always use `copy.deepcopy()` — never mutate the original constant directly.

```python
# Assign
data = copy.deepcopy(VALID_CONFIG_INPUT)
data["output-format"] = "csv"
```

---

## Reporting Format

**Before showing the plan, draft all test implementations in full.** The user must never wait for model processing during collaboration — everything is ready to write the moment the plan appears.

Progress is tracked by module. Within each module, test cases are grouped by function. Present one module at a time and wait for the user's response before moving to the next.

````
## Test Plan

**Progress**
[ ] `<module_a>.py` (<N> test cases)
[ ] `<module_b>.py` (<N> test cases)
[ ] `<module_c>.py` (<N> test cases)

---

### Current module: `<module_a>.py`

#### `function_name()`

**Positive cases**

1. `test_fn_when_<condition>` — single
   Asserts: <one-line description of what is verified>

2. `test_fn_when_<mutual-condition>` — parametrized (<N> cases)
   a. `<input_a>` → `<expected_a>`
   b. `<input_b>` → `<expected_b>`

**Negative cases**

3. `test_fn_when_<condition>` — single
   Raises: `ExceptionType("exact error message")`

4. `test_fn_when_<mutual-condition>` — parametrized (<N> cases)
   a. `<input_a>` → `"<message a>"`
   b. `<input_b>` → `"<message b>"`

---

**Your input:**
- approve: 1, 2, 3
- reject: 4, 5
- modify:
  - <test case number> — <what to modify>
  - <test case number><letter of parametrized case> — <what to modify>
````

After the user responds to a module: apply modifications, mark that module `[x]` in Progress, then present the next module.

Once all modules are marked `[x]`, create a `test_plan.md` file containing all approved test cases so a separate agent can implement them.

### Example

````
## Test Plan

**Progress**
[ ] `yaml_loader.py` (2 test cases)
[ ] `config.py` (12 test cases)

---

### Current module: `yaml_loader.py`

#### `yaml_loader.load()`

**Positive cases**

1. `test_load_when_valid_yaml_file_is_provided` — single
   Asserts: returns a `dict` matching the YAML file contents

**Negative cases**

2. `test_load_when_file_cannot_be_loaded` — parametrized (3 cases)
   a file does not exist → `"File not found: <path>"`
   b file has no read permission → `"Could not read file: <path>"`
   c file contains invalid YAML syntax → `"Invalid YAML in file: <path>"`

---
