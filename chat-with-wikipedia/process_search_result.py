from instrumentation.instrumentation import get_azure_monitor_logger
from promptflow.core import tool

az_mon_logger = get_azure_monitor_logger()


@tool
def process_search_result(search_result):
    def format(doc: dict):
        return f"Content: {doc['Content']}\nSource: {doc['Source']}"

    try:
        context = []
        for url, content in search_result:
            context.append({"Content": content, "Source": url})
        context_str = "\n\n".join([format(c) for c in context])
        return context_str
    except Exception as e:
        az_mon_logger.exception(f"Failed to process search result: {e}")
        return ""
