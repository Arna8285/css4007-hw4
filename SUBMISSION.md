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


- **Round limit, and why:** I set a maximum of 20 model interaction rounds per question using `for step in range(20)`. This prevents infinite tool-calling loops, excessive API costs, and long execution times. If the model does not finish within 20 rounds, the function returns `"ERROR: Tool calling limit reached"`.
- **Where the logs are:** The logs are stored in the `results/` folder as JSON files. These include S1, S2, and S3 results from both runs, accuracy summaries, and the final comparison table.
- **Real Q-09 conversation compared with my A3 version, what is different:** The real S3 conversation used 7 tool calls: 4 `lookup` calls and 3 `calculate` calls, exactly as planned in Part A. The model retrieved the population and area of Brightwater and Millbrook, calculated their population densities, and compared them. The final answer was Millbrook, with a difference of 0.56 residents/km². In my handwritten plan, I rounded the difference to 0.6 residents/km². The real model also used the calculated density values directly in its final subtraction. Both approaches selected the same district.




### B4 — Three strategies

**What I kept the same:**

I used the same model (`gpt-5.6-luna`), dataset of 20 questions, reference answers, and evaluation criteria for all three strategies. Each strategy was tested twice.

S1 answered questions directly using the full corpus. S2 generated five independent answers per question and selected the most frequent answer (k = 5). S3 used the `lookup` and `calculate` tools.

**My rule for a correct answer** (written before the first full run):

An answer is correct when the selected district or yes/no conclusion matches the reference answer, the numerical result matches the required precision, and the units are correct. Incorrect or missing values are counted as wrong.

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | 19 | 0 | 44980 | 6131 | 4.43 | 97.47 | 0.016353 |
| 1 | S2 think and vote (k = 5) | 20 | 0 | 232500 | 26053 | 17.88 | 396.57 | 0.077764 |
| 1 | S3 tools | 17 | 0 | 39475 | 4527 | 6.21 | 121.54 | 0.013327 |
| 2 | S1 direct | 19 | 0 | 44980 | 6360 | 3.91 | 84.73 | 0.016628 |
| 2 | S2 think and vote (k = 5) | 20 | 0 | 232500 | 25629 | 19.45 | 400.37 | 0.077255 |
| 2 | S3 tools | 17 | 0 | 42390 | 4732 | 6.10 | 116.19 | 0.014156 |

**Cost note:** Costs are estimates calculated using assumed prices of $0.20 per million input tokens and $1.20 per million output tokens. They are not verified API billing amounts.

**Per question (run 1):**

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

---


## Part C — Explain and choose (Hard)



### C1 — Does the tool description matter?

I tested five questions (Q-01, Q-05, Q-08, Q-09, and Q-17) using two versions of tool descriptions.

The first version used detailed descriptions explaining how to retrieve district information and perform calculations. The second version used vague descriptions: "Find information." for `lookup` and "Do calculations." for `calculate`.

I kept the same model, questions, tool names, parameters, and Python functions. Only the descriptions were changed.

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---|---|---|---|
| Q-01 | 7 | 7 | Ossbridge, 4.57 (correct) | Ossbridge, 4.57 (correct) |
| Q-05 | 7 | 7 | Coldharbour, 14,235.31 (correct) | Coldharbour, 14,235 (less precise) |
| Q-08 | 8 | 5 | No final numerical answer | Brightwater, 1.064 million tenge (wrong) |
| Q-09 | 7 | 7 | Millbrook, 0.56 (correct) | Millbrook, 0.56 (correct) |
| Q-17 | 5 | 8 | Water volume instead of money (wrong) | Harrowfield, 884.46 tenge/resident (correct) |

**Results and explanation:**

For Q-01 and Q-09, both descriptions produced the same answers and the same number of tool calls.

For Q-05, both versions selected Coldharbour, but the vague version reported a less precise number.

For Q-08, the detailed version made 8 tool calls but could not provide a final numerical answer. The vague version made only 5 calls and produced an incorrect result.

For Q-17, the detailed version made 5 calls and answered using water volume instead of money. The vague version made 8 calls and correctly calculated 884.46 tenge per resident.

**Conclusion:**

Tool descriptions affected the results for some questions. However, the detailed descriptions were not always better. In Q-17, the vague version produced a better answer.

This experiment suggests that tool descriptions can influence model behaviour, but five questions are not enough to prove which description is generally better.



### C2 — Three mistakes explained

**Mistake 1 — Numerical error in S1 (Q-15, Run 1)**

In Run 1, S1 reported 17.6 instead of the expected value of 17.61.

The model had access to the full document collection, but its final numerical answer was not precise enough.

This shows that providing all the necessary information does not guarantee accurate numerical reporting.

**Mistake 2 — Most expensive question in S2 (Q-20, Run 1)**

S2 answered all 20 questions correctly, so I selected its most expensive question, Q-20.

The model generated five answers. All five selected Ashgrove and calculated 2993.34 tenge per resident.

The five samples used 11,660 input tokens and 3,289 output tokens. The estimated cost was $0.006279.

Voting produced a consistent answer, but it required five model calls instead of one. This explains why S2 was more expensive than S1.

**Mistake 3 — Missing tariff and unit conversion in S3 (Q-08)**

In Run 1, S3 could not calculate the household water cost because the `lookup` tool did not expose the water tariff from document NR-15.

I later added the `water_tariff_2025` field to the tool.

In Run 2, S3 produced a numerical answer but reported 72,456.15 million tenge instead of 72.46 million tenge.

The correct calculation is:

(3315 - 2806) × 1000 × 142.35 = 72,456,150 tenge

72,456,150 / 1,000,000 = 72.45615 million tenge

This shows that tools can provide useful information, but the model can still make mistakes when converting units.


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

**1. When the model sends a `tool_calls` message, what has actually run so far?**

The model has only requested a tool call. The Python function has not run yet. My code must read the request, execute the tool, and return the result to the model.

**2. Why does `arguments` arrive as a string, and what goes wrong if you pass it straight into your function?**

The API sends tool arguments as a JSON-formatted string. My Python code must parse and validate it before calling the function. Passing the string directly may cause errors because the function expects named parameters with specific types.


**3. How many tokens do your two tool definitions add to every S3 request? Measure it.**

I measured the two tool definitions using the `o200k_base` tokenizer. Their serialized JSON representation contains 269 tokens. This is an estimate of the tool-definition overhead per S3 request, not an exact measurement of API billing tokens.


**4. How much more did S2 cost than S1? Give the number from your table and explain it.**

Across both runs, S2 cost approximately $0.155019, while S1 cost approximately $0.032981. S2 was about 4.70 times more expensive, a difference of approximately $0.122038. This happened because S2 generated five answers for every question instead of one.


**5. Which question needed the most rounds in S3, and why?**

In Run 1, Q-11 and Q-20 had the highest number of tool calls, with 10 calls each. These questions required multiple data lookups and calculations. However, my saved logs do not record model interaction rounds separately, so I cannot determine which question needed the most rounds.


**6. What would you change in `lookup` if there were 100,000 documents?**

I would not scan every document for every request. Instead, I would build an index or database to retrieve relevant documents faster. I would also keep source identifiers and return only a small amount of relevant information.

**7. What stops your `calculate` from running dangerous code? Could the model still make it misbehave?**

My `calculate` tool uses Python's `ast` module and allows only approved arithmetic operations. It rejects function calls, attribute access, and dangerous expressions such as `__import__('os')`. However, the model can still send invalid expressions or request mathematically incorrect calculations, so validation is still necessary.

**8. For which kind of question did tools help most, and for which did they not help at all?**

Tools were useful for retrieving district data and performing arithmetic calculations, especially for population density and budget comparisons. However, tools did not prevent mistakes involving units or the interpretation of the question. For example, S3 answered Q-17 using water volume instead of money in Run 1.

