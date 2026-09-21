import asyncio
import os
from pathlib import Path
import json
from dataclasses import asdict

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage
)
from claude_agent_sdk.types import (
    HookMatcher, 
    PermissionResultAllow
)

i:int = 0
msgLogPath = Path("messages/resume-session")

answers = None

async def ask_user_question_hook(input_data, tool_use_id, context):
    """PreToolUse hook. Fires for every tool call; we only act on AskUserQuestion."""
    global answers

    tool_name = input_data.get("tool_name")
    print(f"ask_user_question_hook:{tool_name}")
    if tool_name != "AskUserQuestion":
        return {}  # let everything else through untouched
    #return {}

    #session_id = context.get("session_id")

    #print(input_data)
    #print(session_id)
    #print(tool_use_id)
    #print(json.dumps(input_data))
 
    if answers is None:
        answer = {
            "tool_use_id": tool_use_id,
            "questions": input_data["tool_input"].get("questions", []),
        }

        answers = {}
        questions = input_data["tool_input"].get("questions", [])
        for q in questions:
            answers[q["question"]] = q["options"][0]["label"]

        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "defer",
            }
        }

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {
                **input_data["tool_input"],
                "answers": answers,
            },
        }
    }


async def can_use_tool(
    tool_name: str, input_data: dict, context
) -> PermissionResultAllow:
    print("can_use_tool")
    if tool_name == "AskUserQuestion":
        answers = {}
        questions = input_data.get("questions", [])
        for q in questions:
            answers[q["question"]] = q["options"][0]["label"]
        updated_input = {
            "questions": questions,
            "answers": answers
        }
        return PermissionResultAllow(updated_input=updated_input) 
    return PermissionResultAllow(updated_input=input_data)

async def question_and_stop() -> str:
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a Senior Developer",
        can_use_tool=can_use_tool,
        #allowed_tools=[
        #    "AskUserQuestion"
        #],
        hooks={
            "PreToolUse": [HookMatcher(matcher="AskUserQuestion", hooks=[ask_user_question_hook])],
        },
    )

    session_id:str = None

    async for message in query(
        prompt="Find out which program language [Java/Python/JavaScript] the user are working on, and provide the offical reference URL for reference. Ask the user directly and do not answer base on the local codebase. You just need to provide the URL and don't need to ask further question afterward.",
        options=options
    ):
        print_message(message)

        if isinstance(message, ResultMessage):
            session_id = message.session_id

    return session_id

async def answer_and_resume(sessionId:str) -> None:
    options = ClaudeAgentOptions(
        model="claude-haiku-4-5-20251001",
        system_prompt="You are a Senior Developer",
        can_use_tool=can_use_tool,
        #allowed_tools=[
        #    "AskUserQuestion"
        #],
        hooks={
            "PreToolUse": [HookMatcher(matcher="AskUserQuestion", hooks=[ask_user_question_hook])],
        },
        resume=sessionId
    )

    async for message in query(
        prompt="",
        options=options
    ):
        print_message(message)

def print_message(message):

    global i
    print(message)

    i = i + 1
    with open(msgLogPath / f"resume_session_{i}_{type(message).__name__}.json", mode="w") as f:
        json.dump(asdict(message), f, indent=4)

async def main() -> None:

    for msgfile in list(msgLogPath.glob("resume_session_*.json")):
        os.remove(msgfile)

    sessionId:str = await question_and_stop()
    print("resume with answer")
    await answer_and_resume(sessionId)

if __name__ == "__main__":
    asyncio.run(main())