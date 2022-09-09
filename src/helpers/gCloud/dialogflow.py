"""
Dialog flow handler
"""
from google.cloud.dialogflowcx_v3.services.agents.client import AgentsClient
from google.cloud.dialogflowcx_v3.types.agent import Agent
from google.cloud.dialogflowcx_v3.services.pages.client import PagesClient
from google.cloud.dialogflowcx_v3.types.page import ListPagesRequest


def create_agent(project_id, display_name):
    """
    Creates Dialog flow agent
    """
    parent = "projects/" + project_id + "/locations/global"
    agents_client = AgentsClient()
    agent = Agent(
        display_name=display_name,
        default_language_code="en",
        time_zone="America/Los_Angeles",
    )
    response = agents_client.create_agent(request={"agent": agent, "parent": parent})
    return response

def get_all_pages(flow_path):
    """
    Gets all pages for the agent
    """
    request = ListPagesRequest(
        parent=flow_path,
    )
    page_client = PagesClient()
    return page_client.list_pages(request=request)
