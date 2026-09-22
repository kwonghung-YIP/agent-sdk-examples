import asyncio
from dataclasses import asdict
import json
from pathlib import Path
import os

from agents import Agent, Runner, trace, RunResult

msgLogPath = Path("messages/first-example")

agent = Agent(
    name="Solution Architect",
    instructions="You provide advice for any software development question.",
    model="gpt-5-nano"
)

async def main() -> None:
    for msgfile in list(msgLogPath.glob("*.json")):
        os.remove(msgfile)

    with trace("Workflow Trace"):
        result = await Runner.run(agent, input="which OpenAI model supoort image input?")
        for input in result.to_input_list():
            print(type(input))
            print(input)

        for resp in result.raw_responses:
            print(type(resp))
            print(resp)

        print(type(result))
        print(result)
        print(result.final_output)

        #with open(msgLogPath / f"result.json", mode="w") as f:
        #    json.dump(asdict(result), f, indent=4)
        
if __name__ == "__main__":
    asyncio.run(main())