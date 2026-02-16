"""Agent tool definitions and dispatch logic."""

import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# OpenAI function-calling format tool definitions
TOOL_DEFINITIONS: list[dict] = []

# Registry: tool_name -> async callable(args_dict, db) -> str
_TOOL_HANDLERS: dict[str, object] = {}


def register_tool(name: str, definition: dict, handler):
    """Register a tool with its OpenAI definition and handler function."""
    TOOL_DEFINITIONS.append(definition)
    _TOOL_HANDLERS[name] = handler


async def execute_tool(name: str, arguments: dict, db: AsyncSession, user=None) -> str:
    """Execute a registered tool and return the result as a JSON string."""
    handler = _TOOL_HANDLERS.get(name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = await handler(arguments, db, user)
        return json.dumps(result, default=str, ensure_ascii=False)
    except Exception as e:
        logger.error("Tool '%s' failed: %s", name, e)
        return json.dumps({"error": str(e)})
