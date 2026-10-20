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

<!-- what changed in your plan, and why. "None" is an answer too. -->

### B2 — Tests

```text
<!-- pytest output -->
```

### B3 — The loop

- Round limit, and why:
- Where the logs are:
- Real Q-09 conversation compared with my A3 version, what is different:

### B4 — Three strategies

**What I kept the same:**

<!-- model, temperature, k, prompts, answer format, anything else -->

**My rule for a correct answer** (written before the first full run):

| Run | Strategy | Correct /20 | Unanswered | Input tokens | Output tokens | Median seconds per question | Total seconds | Cost ($) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | S1 direct | | | | | | | |
| 1 | S2 think and vote (k = ) | | | | | | | |
| 1 | S3 tools | | | | | | | |
| 2 | S1 direct | | | | | | | |
| 2 | S2 think and vote (k = ) | | | | | | | |
| 2 | S3 tools | | | | | | | |

**Per question (run 1):**

| Question | S1 | S2 | S3 |
|---|:---:|:---:|:---:|
| Q-01 | | | |
| Q-02 | | | |
| Q-03 | | | |
| Q-04 | | | |
| Q-05 | | | |
| Q-06 | | | |
| Q-07 | | | |
| Q-08 | | | |
| Q-09 | | | |
| Q-10 | | | |
| Q-11 | | | |
| Q-12 | | | |
| Q-13 | | | |
| Q-14 | | | |
| Q-15 | | | |
| Q-16 | | | |
| Q-17 | | | |
| Q-18 | | | |
| Q-19 | | | |
| Q-20 | | | |

---

## Part C — Explain and choose (Hard)

### C1 — Does the tool description matter?

| Question | Calls (your description) | Calls (vague) | Answer (yours) | Answer (vague) |
|---|---:|---:|---|---|
| | | | | |

### C2 — Three mistakes explained

### C3 — Which strategy I would use, and what would change it

### C4 — How sure I can be

### Final questions

1.
2.
3.
4.
5.
6.
7.
8.
