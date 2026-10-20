# HW4 — submission

 **AI assistance:** I used ChatGPT to understand the assignment, plan the solution, and get help with Python code and debugging. I will check the code and analyze my own results.

---

## Part A — Plan on paper (Easy)

> Commit this whole part before any `.py` file exists.

### A1 — The steps

| # | Step | What goes in (types) | What comes out (types) | When it goes wrong | Tool, loop, or model? |
|---|---|---|---|---|---|
| 1 | Understand the question | Question (str) | District names and required metric (str) | Unclear question | Model |
| 2 | Find the data | District name and field (str) | Values and source IDs (dict) | Missing or ambiguous district | lookup tool |
| 3 | Check the data | Retrieved facts (dict) | Valid 2025 facts (dict) | Archived data, corrections, or unknown units | lookup tool |
| 4 | Prepare calculation | Valid numbers (float) | Arithmetic expression (str) | Missing values or wrong formula | Model |
| 5 | Calculate | Arithmetic expression (str) | Numeric result (float) | Invalid expression or division by zero | calculate tool |
| 6 | Compare results | Numeric results (float) | District name and difference | Equal values or missing result | Model |
| 7 | Format the answer | Name (str), difference (float) | Final answer (str) | Wrong rounding or format | Model |

**How the steps connect:**

Question → Model understands the question → lookup finds the data → lookup checks corrections and units → Model prepares the formula → calculate performs arithmetic → Model compares the results → Final answer.

The output of each step becomes the input of the next step. The model decides which tools to call, and the loop executes the tools and returns their results to the model.

**What I am assuming:**

1. I use the 2025 census population and 2025 budget data unless the question asks for another year.
2. I ignore archived 2019 profiles because they contain old information.
3. I use correction notice NR-16, so Brightwater's correct area is 921.4 km², not 912.4 km².
4. I convert all measurements to the same units before calculating. For example, 1 megalitre = 1,000 cubic metres.
5. I use the 2025 water tariff of 142.35 tenge per cubic metre when needed.
6. I use 365 days for calculations involving daily water consumption in 2025.
7. I keep full precision during calculations and round only the final answer to the required decimal places.

### A2 — The two tools

#### `lookup`
```json

{
  "type": "function",
  "function": {
    "name": "lookup",
    "description": "Find a specific field for a district in the Nine Rivers Region. Use current 2025 profiles, ignore archived profiles, apply correction notices, and return the value with its unit and source document ID. Return an error for unknown districts or fields.",
    "parameters": {
      "type": "object",
      "properties": {
        "district": {
          "type": "string",
          "description": "Exact district name, such as Brightwater."
        },
        "field": {
          "type": "string",
          "description": "Field to find, such as population_2025, population_2020, area_km2, budget_2025, water_2025, schools, pupils, roads_km, founded_year, or water_tariff_2025."
        }
      },
      "required": ["district", "field"],
      "additionalProperties": false
    }
  }
}
```

| Case | What the tool returns |
|---|---|
| Success | Returns the value, unit, and source document ID. |
| Unknown district | Returns an error message and suggests similar district names. |
| Unknown field | Returns an error explaining that the requested field is not available. |
| Archived profile | Ignores archived data and uses the current 2025 profile. |
| Corrected value | Uses the correction notice instead of the incorrect value. |
| Invalid input | Returns an error if the district or field is empty or invalid. |

**Worst thing it could do with strange or dangerous input:** The lookup tool could return incorrect data if a district name is ambiguous or an archived profile is used by mistake. To prevent this, it validates inputs, checks exact district names, ignores archived profiles, and applies correction notices. It only reads local data files and does not execute user input as code.

#### `calculate`

```json
{
  "type": "function",
  "function": {
    "name": "calculate",
    "description": "Safely calculate arithmetic expressions using numbers and basic operators. Use this tool for mathematical calculations. Reject invalid expressions, division by zero, dangerous code, and excessively large calculations.",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "An arithmetic expression, such as 44675 / 921.4. Allowed operators are +, -, *, and /."
        }
      },
      "required": ["expression"],
      "additionalProperties": false
    }
  }
}
```

| Case | What the tool returns |
|---|---|
| Success | Returns the calculated numeric result. |
| Invalid expression | Returns an error message without executing the expression. |
| Division by zero | Returns an error explaining that division by zero is not allowed. |
| Dangerous code | Rejects function calls, attribute access, and unsupported operations. |
| Very large calculation | Returns an error if the expression or result exceeds the safety limits. |
| Empty input | Returns an error if the expression is empty. |

**Worst thing it could do with strange or dangerous input:** The worst risk is executing dangerous Python code or causing the program to freeze with extremely large calculations. To prevent this, I will use the ast module instead of eval or exec. The tool will allow only basic arithmetic operators and will limit expression size, number size, and calculation complexity.

### A3 — Q-09 by hand

```json

[
  {
    "role": "user",
    "content": "Which district has the higher population density in 2025, Brightwater or Millbrook, and by how many residents per square kilometre?"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "id": "call_1",
        "type": "function",
        "function": {
          "name": "lookup",
          "arguments": "{\"district\":\"Brightwater\",\"field\":\"population_2025\"}"
        }
      },
      {
        "id": "call_2",
        "type": "function",
        "function": {
          "name": "lookup",
          "arguments": "{\"district\":\"Brightwater\",\"field\":\"area_km2\"}"
        }
      },
      {
        "id": "call_3",
        "type": "function",
        "function": {
          "name": "lookup",
          "arguments": "{\"district\":\"Millbrook\",\"field\":\"population_2025\"}"
        }
      },
      {
        "id": "call_4",
        "type": "function",
        "function": {
          "name": "lookup",
          "arguments": "{\"district\":\"Millbrook\",\"field\":\"area_km2\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_1",
    "content": "{\"value\":44675,\"unit\":\"residents\",\"source\":\"NR-05\"}"
  },
  {
    "role": "tool",
    "tool_call_id": "call_2",
    "content": "{\"value\":921.4,\"unit\":\"km2\",\"source\":\"NR-16\"}"
  },
  {
    "role": "tool",
    "tool_call_id": "call_3",
    "content": "{\"value\":37203,\"unit\":\"residents\",\"source\":\"NR-11\"}"
  },
  {
    "role": "tool",
    "tool_call_id": "call_4",
    "content": "{\"value\":758.6,\"unit\":\"km2\",\"source\":\"NR-11\"}"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "id": "call_5",
        "type": "function",
        "function": {
          "name": "calculate",
          "arguments": "{\"expression\":\"44675 / 921.4\"}"
        }
      },
      {
        "id": "call_6",
        "type": "function",
        "function": {
          "name": "calculate",
          "arguments": "{\"expression\":\"37203 / 758.6\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_5",
    "content": "{\"result\":48.485}"
  },
  {
    "role": "tool",
    "tool_call_id": "call_6",
    "content": "{\"result\":49.042}"
  },
  {
    "role": "assistant",
    "tool_calls": [
      {
        "id": "call_7",
        "type": "function",
        "function": {
          "name": "calculate",
          "arguments": "{\"expression\":\"37203 / 758.6 - 44675 / 921.4\"}"
        }
      }
    ]
  },
  {
    "role": "tool",
    "tool_call_id": "call_7",
    "content": "{\"result\":0.557}"
  },
  {
    "role": "assistant",
    "content": "ANSWER: Millbrook | 0.6"
  }
]
```

**My arithmetic:**
**Formula:**

Population density = Population / Area

**1. Brightwater:**

Population = 44,675 (NR-05)

Corrected area = 921.4 km² (NR-16)

Density = 44,675 / 921.4 = 48.485 residents/km²

**2. Millbrook:**

Population = 37,203 (NR-11)

Area = 758.6 km² (NR-11)

Density = 37,203 / 758.6 = 49.042 residents/km²

**3. Difference:**

49.042 − 48.485 = 0.557 ≈ 0.6 residents/km²

**Conclusion:**

Millbrook has a higher population density than Brightwater in 2025. The difference is approximately 0.6 residents per square kilometre.

**Final answer:**

ANSWER: Millbrook | 0.6

### A4 — Why I split it this way

I divided the task into two tools: lookup and calculate.

The lookup tool finds information from the documents, and the calculate tool performs mathematical operations.

Another option was to create one large tool that finds the data and calculates the final answer.

I did not choose this option because two separate tools are easier to test, debug, and understand. They also help identify whether a mistake comes from incorrect data or a calculation.

This approach makes the solution more flexible and reliable.

---



## Part B — Build it and run it (Medium)

### What I changed from Part A while coding

I implemented two separate Python tools: `lookup` and `calculate`.

The `lookup` tool reads the local corpus, ignores archived profiles, and applies the corrected area for Brightwater (NR-16). I later added the `water_tariff_2025` field from NR-15 because it was needed for water-cost questions.

The `calculate` tool uses Python's `ast` module instead of `eval` to perform arithmetic safely.

I also added error handling, unit conversion, pytest tests, and JSON result logging.

### B2 — Tests

I used pytest to test both tools. All 14 tests passed.

```text
collected 14 items

test_lookup.py::test_population PASSED
test_lookup.py::test_corrected_area PASSED
test_lookup.py::test_water_conversion PASSED
test_lookup.py::test_budget PASSED
test_lookup.py::test_correct_source PASSED
test_lookup.py::test_unknown_district PASSED
test_lookup.py::test_unknown_field PASSED

test_calculate.py::test_addition PASSED
test_calculate.py::test_multiplication PASSED
test_calculate.py::test_division PASSED
test_calculate.py::test_negative_numbers PASSED
test_calculate.py::test_zero_division PASSED
test_calculate.py::test_dangerous_input PASSED
test_calculate.py::test_unsupported_operation PASSED

============================== 14 passed in 0.04s ==============================
```

The tests covered normal calculations, corrected data, invalid inputs, division by zero, and dangerous expressions.

### B3 — The loop

- **Round limit, and why:** I used a bounded tool-calling loop to prevent infinite calls, excessive API costs, and long execution times. The exact limit should be confirmed from the notebook.
- **Where the logs are:** The logs are stored in the `results/` folder as JSON files. These include S1, S2, and S3 results from both runs, accuracy summaries, and the final comparison table.
- **Real Q-09 conversation compared with my A3 version, what is different:** In Part A, I planned four `lookup` calls and three `calculate` calls. In the actual S3 experiment, the final answer was also Millbrook, with a difference of approximately 0.56 residents/km², which rounds to 0.6. The exact tool-call sequence still needs to be checked against the saved trace.

### B4 — Three strategies

**What I kept the same:**

All strategies answered the same 20 questions using the same Nine Rivers dataset and reference answers.

I used the `gpt-5.6-luna` model and performed two runs for each strategy.

- **S1 Direct:** The model received the corpus and answered directly.
- **S2 Think and Vote:** The model generated five independent answers and selected the most frequent result (k = 5).
- **S3 Tools:** The model used `lookup` and `calculate` to retrieve data and perform calculations.

**My rule for a correct answer:**

An answer is correct if the selected district or yes/no decision matches the reference answer and the numerical result matches at the required decimal precision.

I accepted extra precision when rounding produced the reference value. Wrong units, missing answers, and incorrect numerical values were counted as errors.

### Results across two runs

| Strategy | Run 1 | Run 2 | Average accuracy | Average time | Average tokens |
|---|---:|---:|---:|---:|---:|
| S1 Direct | 19/20 | 19/20 | 95% | 4.55 s | 2,561 |
| S2 Voting (k=5) | 20/20 | 20/20 | 100% | 19.92 s | 12,917 |
| S3 Tools | 17/20 | 17/20 | 85% | 5.94 s | 2,278 |

### Execution time and token usage

| Run | Strategy | Correct /20 | Total tokens | Total seconds |
|---|---|---:|---:|---:|
| 1 | S1 Direct | 19 | 51,111 | 97.47 |
| 1 | S2 Voting | 20 | 258,553 | 396.57 |
| 1 | S3 Tools | 17 | 44,002 | 121.54 |
| 2 | S1 Direct | 19 | 51,340 | 84.73 |
| 2 | S2 Voting | 20 | 258,129 | 400.37 |
| 2 | S3 Tools | 17 | 47,122 | 116.19 |

### Estimated API cost

The following costs were calculated using assumed rates of $0.20 per million input tokens and $1.20 per million output tokens. These are estimates, not verified billing amounts.

| Strategy | Average cost per question | Total cost (40 questions) |
|---|---:|---:|
| S1 Direct | $0.000825 | $0.032981 |
| S2 Voting | $0.003875 | $0.155018 |
| S3 Tools | $0.000687 | $0.027484 |

### Per question (run 1)

| Question | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| Q-01 | Correct | Correct | Correct |
| Q-02 | Correct | Correct | Correct |
| Q-03 | Correct | Correct | Correct |
| Q-04 | Correct | Correct | Correct |
| Q-05 | Correct | Correct | Correct |
| Q-06 | Correct | Correct | Correct |
| Q-07 | Correct | Correct | Correct |
| Q-08 | Correct | Correct | Wrong |
| Q-09 | Correct | Correct | Correct |
| Q-10 | Correct | Correct | Correct |
| Q-11 | Correct | Correct | Correct |
| Q-12 | Correct | Correct | Correct |
| Q-13 | Correct | Correct | Correct |
| Q-14 | Correct | Correct | Correct |
| Q-15 | Wrong | Correct | Wrong |
| Q-16 | Correct | Correct | Correct |
| Q-17 | Correct | Correct | Wrong |
| Q-18 | Correct | Correct | Correct |
| Q-19 | Correct | Correct | Correct |
| Q-20 | Correct | Correct | Correct |

### Run 2 errors

S1 made one error in Q-05, reporting 4,235.31 instead of 14,235.31 tenge per resident.

S2 answered all 20 questions correctly.

S3 made three errors:
- Q-08: Incorrect water-cost unit conversion.
- Q-15: Incorrect rounding precision.
- Q-17: Incorrect water-cost scale.

---

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

The tool descriptions explain which data the model should retrieve, how to handle corrections, and when to use arithmetic.

A detailed description may help the model select the correct fields and avoid archived data.

To measure the effect, the same question must be tested with detailed and vague tool descriptions while keeping the other settings unchanged.

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---:|---:|---|---|
| Q-09 | To verify | Not tested | Millbrook, 0.6 residents/km² | Not tested |

The vague-description experiment has not yet been completed, so I cannot claim a measured improvement.

### C2 — Three mistakes explained

**Mistake 1 — Missing data in S3 (Q-08, Run 1)**

S3 could not calculate the household water cost because the original `lookup` tool did not expose the water tariff.

The tariff was available in document NR-15, but the tool could not retrieve it.

I improved the tool by adding the `water_tariff_2025` field.

This shows that a model can fail when the tool does not provide all necessary information.

**Mistake 2 — Unit conversion error in S3 (Q-08, Run 2)**

S3 reported a difference of 72,456.15 million tenge.

The correct result was 72.46 million tenge.

Correct calculation:

(3315 - 2806) × 1000 × 142.35 = 72,456,150 tenge

72,456,150 / 1,000,000 = 72.45615 million tenge

S3's reported result was 1,000 times too large.

This error shows the importance of checking measurement units.

**Mistake 3 — Incorrect quantity and scale in S3 (Q-17)**

In the first run, S3 calculated a difference in water volume instead of money.

In the second run, it reported approximately 884,457.16 tenge per resident.

The correct difference was approximately 884.46 tenge per resident, rounded to 884.

This demonstrates that retrieving the correct data is not enough. The model must also use the correct formula and units.

**Additional errors:**

In Q-15, S1 and S3 reported 17.6 instead of 17.61 in Run 1.

In Run 2, S1 corrected this error, but S3 repeated it.

S1 also made a numerical reporting error in Q-05 of Run 2.

### C3 — Which strategy I would use, and what would change it

I would choose **S1 Direct** for this small dataset because it offers a good balance between accuracy, speed, and cost.

S1 achieved 95% accuracy and required only 4.55 seconds per question on average.

S2 achieved the highest accuracy at 100%, but it was much slower and used approximately five times more tokens.

S3 used the fewest tokens but achieved only 85% accuracy and made serious unit-conversion errors.

I would choose **S2 Voting** when accuracy is the most important requirement and higher time and cost are acceptable.

I would consider **S3 Tools** for larger datasets where retrieving specific information is necessary. However, I would first improve unit validation, tool descriptions, and answer formatting.

### C4 — How sure I can be

My conclusions are based on 20 questions and two runs per strategy.

The results show how the strategies performed on this particular dataset, but they do not guarantee the same performance on other tasks.

S2 achieved 100% accuracy in both runs, but voting does not always guarantee a correct answer.

S3 showed that tools can help retrieve information, but incorrect unit conversion can still produce wrong results.

There are also limitations in the experiment:

- The dataset is small.
- The questions use similar numerical operations.
- Some answers were evaluated manually.
- The S3 tool interface changed between the two runs.
- The API costs are estimates rather than verified billing charges.

For a more reliable comparison, I would test more questions, repeat each strategy more times, use consistent tool definitions, and save complete tool-call logs.

### Final questions

The original template contains eight numbered placeholders without question text. These questions must be added from the original assignment before submission.

1. [Original question 1 needed]
2. [Original question 2 needed]
3. [Original question 3 needed]
4. [Original question 4 needed]
5. [Original question 5 needed]
6. [Original question 6 needed]
7. [Original question 7 needed]
8. [Original question 8 needed]
