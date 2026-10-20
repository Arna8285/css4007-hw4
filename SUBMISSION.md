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

During implementation, I created two Python tools: `lookup` and `calculate`, in `tools_hw4.py`. I added input validation and safe arithmetic using Python's `ast` module. I also created automated tests and implemented three strategies to compare their accuracy, time, and token usage.

### B2 — Tests

I created two test files: `test_lookup.py` and `test_calculate.py`. I ran the tests using `pytest` on Windows with Python 3.13.2.

**Pytest output:**

```text
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.1.1, pluggy-1.7.0
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

============================= 14 passed in 0.03s ==============================
```

All 14 tests passed successfully. The tests verify correct lookup results, data corrections, unit conversion, arithmetic operations, and error handling.

### B3 — The loop

**Round limit:** I set a maximum of 20 interaction rounds for the S3 tool-assisted strategy using `for step in range(20)`. This prevents infinite loops and excessive API calls.If the model does not produce a final answer within 20 rounds, the loop stops and returns `ERROR: Tool calling limit reached`. This error indicates that the question was not answered within the allowed number of rounds.

**Where the logs are:** All experimental results are saved in the `outputs/` folder. The logs contain question IDs, answers, token usage, execution time, and tool-call arguments and results.

**Real Q-09 conversation compared with my A3 version:** In Part A, I manually planned seven tool calls: four `lookup` calls and three `calculate` calls. In the actual implementation, the model selected tool calls dynamically rather than following a fixed handwritten sequence. Both approaches aimed to compare the 2025 population densities of Brightwater and Millbrook.

**Limitation:** Individual tool-call durations and explicit round identifiers were not consistently recorded in the saved logs.

### B4 — Three strategies

I evaluated three strategies on 20 questions, with two runs per strategy.

- **S1 — Direct:** the model received the corpus and answered directly.
- **S2 — Self-consistency:** the model generated five samples and selected an answer by voting.
- **S3 — Tool-assisted:** the model used lookup and calculate tools to find evidence and perform calculations.

#### Overall results

| Run | Strategy | Correct / 20 | Unanswered | Input tokens | Output tokens | Median seconds | Total seconds | Estimated cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 | 19 | 0 | 44980 | 6131 | 4.43 | 97.47 | 0.016353 |
| 1 | S2 | 20 | 0 | 232500 | 26053 | 17.88 | 396.57 | 0.077764 |
| 1 | S3 | 17 | 0 | 39475 | 4527 | 6.21 | 121.54 | 0.013327 |
| 2 | S1 | 19 | 0 | 44980 | 6360 | 3.91 | 84.73 | 0.016628 |
| 2 | S2 | 20 | 0 | 232500 | 25629 | 19.45 | 400.37 | 0.077255 |
| 2 | S3 | 17 | 0 | 42390 | 4732 | 6.10 | 116.19 | 0.014156 |

The cost figures are estimates based on assumed prices of $0.20 per million input tokens and $1.20 per million output tokens, not verified billing charges.

#### Per-question accuracy — Run 1

| Question | S1 | S2 | S3 |
|---|---|---|---|
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

#### Per-question accuracy — Run 2

| Question | S1 | S2 | S3 |
|---|---|---|---|
| Q-01 | Correct | Correct | Correct |
| Q-02 | Correct | Correct | Correct |
| Q-03 | Correct | Correct | Correct |
| Q-04 | Correct | Correct | Correct |
| Q-05 | Wrong | Correct | Correct |
| Q-06 | Correct | Correct | Correct |
| Q-07 | Correct | Correct | Correct |
| Q-08 | Correct | Correct | Wrong |
| Q-09 | Correct | Correct | Correct |
| Q-10 | Correct | Correct | Correct |
| Q-11 | Correct | Correct | Correct |
| Q-12 | Correct | Correct | Correct |
| Q-13 | Correct | Correct | Correct |
| Q-14 | Correct | Correct | Correct |
| Q-15 | Correct | Correct | Wrong |
| Q-16 | Correct | Correct | Correct |
| Q-17 | Correct | Correct | Wrong |
| Q-18 | Correct | Correct | Correct |
| Q-19 | Correct | Correct | Correct |
| Q-20 | Correct | Correct | Correct |

#### Interpretation

S2 achieved the highest accuracy: 20/20 in both runs. However, it required substantially more tokens and time than S1 or S3. S1 achieved 19/20 in both runs and was much faster. S3 achieved 17/20 in both runs, showing that access to tools alone does not guarantee correct reasoning or unit handling.

The experiment files are stored in `outputs/`, including individual strategy results, two-run accuracy summaries, the final comparison CSV, and the C1 tool-description experiment. The tool logs record arguments and results. Individual tool-call durations and explicit round identifiers were not captured in every log, which limits detailed per-call timing analysis.

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

I compared my detailed tool descriptions against vague descriptions on five questions.

| Question | Calls (detailed) | Calls (vague) | Detailed result | Vague result |
|---|---:|---:|---|---|
| Q-01 | 7 | 7 | Correct | Correct |
| Q-05 | 7 | 7 | Correct | Correct, but less precise |
| Q-08 | 8 | 5 | No numerical final answer | Incorrect: approximately 1.064 million |
| Q-09 | 7 | 7 | Correct | Correct |
| Q-17 | 5 | 8 | Incorrect unit handling | Correct: 884.46 tenge per resident |

These results do not show that detailed descriptions always improve accuracy. The effect depends on the question. For Q-05, the detailed description improved precision. For Q-08, neither configuration produced a satisfactory result. For Q-17, the vague description happened to produce the correct answer while the detailed version failed.

Tool descriptions influence how a model chooses and uses tools, but clear descriptions cannot eliminate arithmetic, retrieval, or unit-conversion errors.

### C2 — Three mistakes explained

**S1 — Direct strategy, Q-15.** In Run 1, S1 returned an incorrect numerical result due to a precision-related error. This illustrates how direct reasoning can fail even when the relevant information is included in the prompt. In Run 2, its incorrect question was Q-05 instead, showing variation between runs.

**S2 — Voting strategy, Q-20.** S2 did not make an accuracy error in either run. Therefore, I analyzed an expensive question instead. For Q-20, five samples were generated and the selected numerical answer was 2993.34 for Ashgrove. The question consumed approximately 11,660 input tokens and 3,289 output tokens, with an estimated cost of $0.006279. This shows the main disadvantage of voting: repeated generation increases cost even when the final answer is correct.

**S3 — Tool-assisted strategy, Q-08.** In Run 1, the strategy failed to retrieve or apply the required tariff information correctly. In Run 2, a factor-of-1000 unit error contributed to an incorrect numerical answer. This shows that a correct calculator result is not sufficient when the expression or units supplied to the calculator are wrong.

### C3 — Which strategy I would use, and what would change it

For this particular task, I would choose **S1 as the default strategy** when speed and cost matter, because it achieved 95% accuracy in both runs with much lower resource use than S2.

I would choose **S2 when accuracy is the highest priority** and additional time and token costs are acceptable. It achieved 100% accuracy in both experimental runs, although this small experiment does not guarantee perfect accuracy on new questions.

I would use **S3 when external lookup, auditable calculations, or large datasets make tools necessary**, but I would add validation of source selection, units, and final numerical values. Its current implementation was less accurate than the other strategies.

### C4 — How sure I can be

The results provide useful evidence, but the experiment is small: only 20 questions and two runs per strategy. The questions come from one synthetic corpus and may not represent other datasets or tasks.

Accuracy, timing, and token usage may vary with the model, prompts, hardware, and execution conditions. Estimated monetary costs are based on assumed token prices rather than actual billing records.

I am confident about the observed results for these runs, but less confident that the same ranking will hold for every new task. More questions, repeated trials, and tests on different corpora would make the conclusions stronger.

### Final questions

**1. When the model sends a `tool_calls` message, what has actually run so far?**

When the model sends a `tool_calls` message, it has only requested a tool execution. The tool has not run yet. My Python loop reads the request, executes the appropriate function, and returns the result to the model.

**2. Why does `arguments` arrive as a string, and what goes wrong if you pass it straight into your function?**

The arguments arrive as a JSON-formatted string because they are generated as part of the model's response. My code must parse the string using `json.loads()` and validate the inputs. Passing the raw string directly may cause errors because the function expects named parameters.

**3. How many tokens do your two tool definitions add to every S3 request? Measure it.**

My two tool definitions add approximately **269 tokens**, measured using the `o200k_base` tokenizer. These definitions are included in S3 requests, so they contribute to input-token usage.

**4. How much more did S2 cost than S1? Give the number from your table and explain it.**

In Run 1, S2 cost approximately **$0.077764**, while S1 cost **$0.016353**. The difference was **$0.061411**, meaning S2 cost about **4.76 times as much**. This happened because S2 generated five samples per question instead of one.

**5. Which question needed the most rounds in S3, and why?**

In Run 1, Q-11 and Q-20 each required **10 tool calls**, the highest recorded number. These questions involved multiple information-retrieval and calculation steps. However, the logs record tool calls rather than explicit interaction-round counts, so the exact number of rounds cannot be confirmed from these records.

**6. What would you change in `lookup` if there were 100,000 documents?**

I would add a search index instead of scanning all documents for every request. I would also use metadata filters, retrieve only relevant passages, and return source IDs. This would make lookup faster and more scalable.

**7. What stops your `calculate` from running dangerous code? Could the model still make it misbehave?**

My calculator uses Python's `ast` module and allows only selected arithmetic operations. It rejects function calls, attribute access, and dangerous expressions instead of executing arbitrary Python code. However, the model can still provide an incorrect formula or wrong units, so the numerical
