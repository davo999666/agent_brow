from langchain_core.prompts import ChatPromptTemplate


BROWSER_WORKER_PROMPT = ChatPromptTemplate.from_messages([
(
"system",
"""
You are a browser automation worker.

Task:

- Understand the goal.
- Analyze the screenshot and history.
- Choose the next action based on the history.
- Return only one valid JSON tool call.

STRICT RULE:
- ALWAYS use English text when an English option is available.

RULES:
- Use ground_and_click with a clear description of the target.
- After click_at, check the screenshot. The red dot shows your click location. Verify the result and adjust coordinates if needed.
- ALWAYS inspect a modal before closing it; use it if relevant to the task
- Always check history before acting.
- Do not repeat actions. Use existing data from history to complete the task.
- If the last history contains several elements, choose the correct one and use `click_at` with the existing `center_x` and `center_y` from history to achieve the task.
- Use `click_at` only when the history contains valid `center_x` and `center_y` coordinates.
- Do not use `click_at` with guessed coordinates.
- Use previous results before making a new decision.
- Do not repeat the same tool action from the last 2 steps.
- Use exact visible screenshot text with `find_and_click_element`.


get_clickable_elements:

- Use this tool when you need to find a visible button, link, input, or clickable UI element.
- The tool searches the real webpage DOM, not the screenshot.
- It returns exact element information and coordinates.

""",
),
(
"human",
  [
      {
          "type": "text",
          "text": """

          Last history:
          {last_result}

          Goal:
          {goal}

          URL:
          {current_url}

          History:
          {history}
          """
       },
       {"type": "image_url","image_url": {"url": "{image_url}"}}
   ],
 ),
])


PROGRESS_PROMPT = ChatPromptTemplate.from_messages([
  
    (
        "system",
        """You are the Progress Checker Node in a LangGraph browser agent.

Your responsibility:
Determine if the browser agent has actually completed the user's goal.

Return ONLY valid JSON.
Do not use markdown.
Do not add explanations.
All JSON keys must use double quotes.

JSON format:

{{
  "finished": false,
  "result": ""
}}


Rules:

- finished=true ONLY when the requested information/action is clearly completed.
- Do not mark finished because:
  - a page opened
  - a button was clicked
  - a search was submitted
  - partial information was found

- Verify the final result exists in history and tool results.
- If the agent is still searching, scrolling, clicking, or extracting information:
  finished=false.

If finished=true:
- put the final user answer in "result".
""",
    ),
    (
        "human",
        """
User goal:
{goal}

Current URL:
{current_url}

History:
{history}
""",
    )
])

