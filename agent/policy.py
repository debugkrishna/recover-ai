READ_ONLY_TOOLS = {
    "get_customer",
    "get_payment",
    "predict_customer_recovery",
}


ACTION_TOOLS = {
    "schedule_retry",
    "send_notification",
    "escalate_case",
    "log_action",
}


def validate_tool(tool_name: str) -> bool:
    """
    Check whether the tool exists in our approved tool set.
    """

    return (
        tool_name in READ_ONLY_TOOLS
        or tool_name in ACTION_TOOLS
    )


def is_action_tool(tool_name: str) -> bool:
    """
    Check whether a tool performs an external action.
    """

    return tool_name in ACTION_TOOLS