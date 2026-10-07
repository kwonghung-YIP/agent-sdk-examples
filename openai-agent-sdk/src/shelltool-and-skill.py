import asyncio
import os
import base64
from pathlib import Path
from dataclasses import dataclass, asdict
from jinja2 import Environment, FileSystemLoader

from agents import Agent, Runner, trace, RunContextWrapper, function_tool
from agents import (
    ShellTool, 
    ShellToolLocalEnvironment, 
    ShellToolLocalSkill, 
    ShellExecutor, 
    ShellCommandRequest, 
    ShellResult, 
    ShellCommandOutput,
    ShellCallOutcome,
)
from agents.mcp import (
    MCPServerStdio,
    MCPServerStdioParams,
)

DEFAULT_MODEL=os.environ.get("OPENAI_DEFAULT_MODEL","gpt-6-luna")

@dataclass
class AgentContent:
    agentId: str
    CWD: str

env = Environment(
    loader=FileSystemLoader(searchpath="agents")
)

def load_system_prompt(ctx:RunContextWrapper[AgentContent], agent:Agent) -> str:
    agentId = ctx.context.agentId
    print(f"load_system_prompt:{agentId}.md")
    template = env.get_template(f"{agentId}.md")
    return template.render(asdict(ctx.context))

@function_tool
def read_local_image(file_path:str) -> str:
    """
    Use this function to read local image file, it return the image content in base64 encoding
    Args:
        file_path: the local file path to the image file
    """
    print(f"read image file:{file_path}")
    with open(file_path, "rb") as image:
        image_base64 = base64.b64encode(image.read()).decode()

    return image_base64

WORKDIR = Path.cwd()
SKILLS_DIR = WORKDIR / "skills"

async def local_shell_executor(request:ShellCommandRequest) -> ShellResult|str:
    """
    Execute command in my local environment
    """
    action = request.data.action
    timeout = (action.timeout_ms or 0) / 1000 or None
    outputs: list[ShellCommandOutput] = []

    for command in action.commands:
        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=WORKDIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout)
            outcome = ShellCallOutcome(type="exit", exit_code=proc.returncode)
        except asyncio.TimeoutError:
            proc.kill()
            stdout_b, stderr_b = await proc.communicate()
            outcome = ShellCallOutcome(type="timeout")

        outputs.append(
            ShellCommandOutput(
                stdout=stdout_b.decode("utf-8", errors="ignore"),
                stderr=stderr_b.decode("utf-8", errors="ignore"),
                outcome=outcome,
            )
        )

    return ShellResult(output=outputs)

localShellTool = ShellTool(
    executor=local_shell_executor,
    environment=ShellToolLocalEnvironment(
        skills=[
            ShellToolLocalSkill(
                name="test-product-page",
                description="this skill to test a product page following the test instruction",
                path="skills/test-product-page",
            )
        ]
    ),
)

#
# When server blocked the access from playwright in headless mode, such as 403 error 
# you can try to use chrome remote debug mode instead.
#
# 1. First, start the chrome with command below:
#    google-chrome --remote-debugging-port=9222 --remote-allow-origins="*" --user-data-dir="/tmp/chrome-dev-profile" 
#
# 2. Then open the URL in Chrome, enable remote-debugging => chrome://inspect/#remote-debugging
#
# 3. Set the browser.cdpEndpoint=http://localhost:9222 property in the PlayWright config file playwright-config.json.
#

playwright_mcp = MCPServerStdio(
    name="playwright-mcp",
    params=MCPServerStdioParams(
        command="npx",
        args=[
            "@playwright/mcp@latest",
            "--browser=chrome",
            "--config=playwright-config.json"
        ],
        cwd=Path.cwd()
    )
)

agent = Agent(
    name="Web Extract Agent",
    instructions=load_system_prompt,
    model=DEFAULT_MODEL,
    tools=[
        localShellTool,
        read_local_image,
    ],
    mcp_servers=[
        playwright_mcp
    ]
)

async def main() -> None:
    with trace("shelltool-and-skill"):
        await playwright_mcp.connect()
        result = await Runner.run(
            starting_agent=agent,
            max_turns=15,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": """
                            # Instruction
                            - Given the Dell UK 4K Monitor page below, please test it with PlayWright.
                            - You expected find total 17 models in 2 pages.
                            - Report the model list in the final result.

                            ## The Product Page 
                            https://www.dell.com/en-gb/shop/computer-monitors/ar/computer-monitors/appref=4k-uhd-3840-x-2160-screen-resolution 
                            """,
                        }
                    ]
                }
            ],
            context=AgentContent(
                agentId="shelltool-and-skill",
                CWD=Path.cwd(),
            ),
        )

        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())