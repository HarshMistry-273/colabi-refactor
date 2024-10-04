from langchain_community.tools import TavilySearchResults
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.tools import Tool


class CustomTool:
    """
    A utility class that provides static methods to create custom search tools.

    This class contains methods to create tools for Tavily search and Google Serper API search.
    These tools can be used in conjunction with agent-based systems or other applications
    that require search functionality.
    """

    @staticmethod
    def tavily_search_results(
        tool_name: str = "tavily_search",
        description: str = "search results",
        max_results: int = 10,
        search_depth: str = "advanced",
        include_answer: bool = True,
    ):
        search = TavilySearchResults(
            max_results=max_results,
            search_depth=search_depth,
            include_answer=include_answer,
        )
        tool = Tool(
            name=tool_name,
            func=lambda query: search.invoke(query),
            description=description,
        )

        return tool

    @staticmethod
    def google_serper_api_wrapper(
        tool_name: str = "google_serper_search",
        description: str = "search results",
        serper_api_key: str = None,
    ):
        search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)

        tool = Tool(
            name=tool_name,
            func=lambda query: search.results(query),
            description=description,
        )

        return tool


mapping = {
    "tavily_search": CustomTool.tavily_search_results(),
    "google_serper_search": CustomTool.google_serper_api_wrapper(),
}
