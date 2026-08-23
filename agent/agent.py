import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from agent.policy import validate_tool

from agent.prompts import SYSTEM_PROMPT
from agent.tools import (
    get_customer,
    get_payment,
    predict_customer_recovery,
    schedule_retry,
    send_notification,
    escalate_case,
    log_action,
)


load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in .env"
    )


client = OpenAI(
    api_key=api_key
)


tools = [
    {
        "type": "function",
        "name": "get_customer",
        "description": "Retrieve customer information using the customer ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The unique customer ID."
                }
            },
            "required": ["customer_id"]
        }
    },

    {
        "type": "function",
        "name": "get_payment",
        "description": "Retrieve payment information using the payment ID.",
        "parameters": {
            "type": "object",
            "properties": {
                "payment_id": {
                    "type": "string",
                    "description": "The unique payment ID."
                }
            },
            "required": ["payment_id"]
        }
    },

    {
        "type": "function",
        "name": "predict_customer_recovery",
        "description": (
            "Predict the probability that a failed payment "
            "can be recovered. Requires payment and customer data."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "payment_data": {
                    "type": "object",
                    "description": "Payment information returned by get_payment."
                },
                "customer_data": {
                    "type": "object",
                    "description": "Customer information returned by get_customer."
                }
            },
            "required": [
                "payment_data",
                "customer_data"
            ]
        }
    },

    {
        "type": "function",
        "name": "schedule_retry",
        "description": "Schedule a future retry for a failed payment.",
        "parameters": {
            "type": "object",
            "properties": {
                "payment_id": {
                    "type": "string",
                    "description": "Payment ID to retry."
                },
                "hours": {
                    "type": "integer",
                    "description": "Number of hours before retry."
                }
            },
            "required": [
                "payment_id",
                "hours"
            ]
        }
    },
{
    "type": "function",
    "name": "send_notification",
    "description": "Send a recovery notification to the customer.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer receiving the notification."
            },
            "message": {
                "type": "string",
                "description": "Notification message."
            },
            "payment_id": {
                "type": "string",
                "description": "Payment associated with the notification."
            }
        },
        "required": [
            "customer_id",
            "message",
            "payment_id"
        ]
    }
},

    {
        "type": "function",
        "name": "escalate_case",
        "description": "Escalate a difficult payment recovery case.",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer whose case should be escalated."
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for escalation."
                }
            },
            "required": [
                "customer_id",
                "reason"
            ]
        }
    },

{
    "type": "function",
    "name": "log_action",
    "description": "Record the recovery action taken by the agent.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "Customer associated with the action."
            },
            "action": {
                "type": "string",
                "description": "Action performed."
            },
            "reason": {
                "type": "string",
                "description": "Reason for the action."
            },
            "payment_id": {
                "type": "string",
                "description": "Payment associated with the action."
            }
        },
        "required": [
            "customer_id",
            "action",
            "reason",
            "payment_id"
        ]
    }
}
]

def execute_tool(name, args):

    if not validate_tool(name):

        print(
            f" BLOCKED TOOL: {name}"
        )

        return {
            "success": False,
            "error": (
                f"Tool '{name}' is not "
                "approved by RecoverAI policy."
            ),
        }

    if name == "get_customer":
        return get_customer(**args)

    if name == "get_payment":
        return get_payment(**args)

    if name == "predict_customer_recovery":
        return predict_customer_recovery(**args)

    if name == "schedule_retry":
        return schedule_retry(**args)

    if name == "send_notification":
        return send_notification(**args)

    if name == "escalate_case":
        return escalate_case(**args)

    if name == "log_action":
        return log_action(**args)

    return {
        "success": False,
        "error": f"Unknown tool: {name}",
    }

def test_tool_call():

    response = client.responses.create(
        model="gpt-5-mini",
        instructions=SYSTEM_PROMPT,
        input="Analyze customer CUST_001. Use the get_customer tool.",
        tools=tools,
    )

    print(response)


def run_agent(user_request: str):

    conversation = [
        {
            "role": "user",
            "content": user_request,
        }
    ]

    while True:

        response = client.responses.create(
            model="gpt-5-mini",
            instructions=SYSTEM_PROMPT,
            input=conversation,
            tools=tools,
        )

        # Add model output to the conversation
        conversation.extend(response.output)

        # ------------------------------------------
        # Find function calls
        # ------------------------------------------

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        # ------------------------------------------
        # No function call = final answer
        # ------------------------------------------

        if not function_calls:

            return response.output_text

        # ------------------------------------------
        # Execute requested tools
        # ------------------------------------------

        for function_call in function_calls:

            tool_name = function_call.name

            tool_args = json.loads(
                function_call.arguments
            )

            print(
                f"\n🔧 Tool call: {tool_name}"
            )

            print(
                f"Arguments: {tool_args}"
            )

            result = execute_tool(
                tool_name,
                tool_args,
            )

            print(
                f"Tool result: {result}"
            )

            # --------------------------------------
            # Send tool result back to OpenAI
            # --------------------------------------

            conversation.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(result),
                }
            )

if __name__ == "__main__":

    result = run_agent(
        """
        Analyze the failed payment PAY_001.

        Investigate the customer and payment information,
        determine the recovery likelihood, and choose an
        appropriate recovery action.
        """
    )

    print("\n==============================")
    print("FINAL AGENT RESPONSE")
    print("==============================")
    print(result)