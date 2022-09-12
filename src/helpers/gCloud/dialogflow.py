"""
Dialog flow handler
"""
import os
from google.cloud.dialogflowcx_v3.services.agents.client import AgentsClient
from google.cloud.dialogflowcx_v3.types.agent import Agent
from google.cloud.dialogflowcx_v3.services.pages.client import PagesClient
from google.cloud.dialogflowcx_v3.types.page import Form, Page, ListPagesRequest, UpdatePageRequest, GetPageRequest
from google.cloud.dialogflowcx_v3.services.flows.client import FlowsClient
from google.cloud.dialogflowcx_v3.types.flow import UpdateFlowRequest, GetFlowRequest
from google.cloud.dialogflowcx_v3.types import ResponseMessage, Fulfillment, TransitionRoute
from google.protobuf.field_mask_pb2 import FieldMask
from src.helpers import constant


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

def get_product_page(page_name):
    """
    Gets the page for the provided page name
    """
    page_client = PagesClient()
    request = GetPageRequest(
        name=page_name,
    )
    return page_client.get_page(request=request)

def add_route_for_product_name_page(agent_id, anchor_product_page_id, new_product_page):
    """
    Adds product page to anchor/default page
    """
    pages_client = PagesClient()

    project_id = os.getenv(constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)
    page_name = f'projects/{project_id}/locations/{constant.LOCATION_ID}/agents/{agent_id}/flows/{constant.DEFAULT_FLOW_ID}/pages/{anchor_product_page_id}'
    page = get_product_page(page_name)

    condition = f'$session.params.{constant.PRODUCT_NAME}="{new_product_page.display_name}"'
    new_route = TransitionRoute(condition=condition, target_page=new_product_page.name)
    routes = page.transition_routes
    routes.append(new_route)
    page.transition_routes = routes

    mask = FieldMask()
    mask.FromJsonString("transitionRoutes")
    request = UpdatePageRequest(
        page=page,
        update_mask=mask,
    )
    response = pages_client.update_page(request=request)
    return response

def create_default_product_page(project_id, agent_id):
    """
    Creates the default page in the agent to capture product name
    """
    pages_client = PagesClient()
    page = Page()
    page.display_name = constant.DEFAULT_PRODUCT_PAGE_NAME

    #Adding default form parameter to the page
    res_text = ResponseMessage.Text(text=[constant.DEFAULT_PRODUCT_PAGE_FULFILLMENT])
    resp_message = ResponseMessage(text=res_text)
    fulfillment = Fulfillment(messages=[resp_message])
    fill_behavior = Form.Parameter.FillBehavior(initial_prompt_fulfillment=fulfillment)
    parameter = Form.Parameter(display_name=constant.PRODUCT_NAME, required=True, entity_type=constant.ENTITY_TYPE, fill_behavior=fill_behavior)
    param = {"parameters":[parameter]}
    form = Form(param)
    page.form = form

    parent = f'projects/{project_id}/locations/{constant.LOCATION_ID}/agents/{agent_id}/flows/{constant.DEFAULT_FLOW_ID}'
    response = pages_client.create_page(parent=parent, page=page)
    return response

def create_product_page(agent_id, product_name):
    """
    Creates a new page for a new product
    """
    pages_client = PagesClient()
    page = Page()
    page.display_name = product_name

    project_id = os.getenv(constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)
    parent = f'projects/{project_id}/locations/{constant.LOCATION_ID}/agents/{agent_id}/flows/{constant.DEFAULT_FLOW_ID}'

    resp = pages_client.create_page(parent=parent, page=page)
    return resp

def update_default_flow(project_id, agent_id, new_page):
    """
    Updates the default flow to link the new anchor product page.
    """
    flows_client = FlowsClient()
    flow_path = f'projects/{project_id}/locations/{constant.LOCATION_ID}/agents/{agent_id}/flows/{constant.DEFAULT_FLOW_ID}'
    flow_request = GetFlowRequest(name=flow_path)
    flow = flows_client.get_flow(flow_request)

    updated_routes = []
    for route in flow.transition_routes:
        if constant.DEFAULT_INTENT_ID in route.intent:
            route.target_page = f'{flow_path}/pages/{new_page}'
        updated_routes.append(route)
    flow.transition_routes = updated_routes
    update_mask = FieldMask(paths=["transition_routes"])
    flow_request = UpdateFlowRequest(flow=flow, update_mask=update_mask)
    resp = flows_client.update_flow(request=flow_request)
    return resp

def update_product_page(agent_id, product_page_id, intents, intent_ids_to_delete):
    """
    Updates the product page with all the intent routes
    """
    pages_client = PagesClient()

    project_id = os.getenv(constant.PROJECT_ID, constant.DEFAULT_PROJECT_NAME)
    page_name = f'projects/{project_id}/locations/{constant.LOCATION_ID}/agents/{agent_id}/flows/{constant.DEFAULT_FLOW_ID}/pages/{product_page_id}'
    request = GetPageRequest(
        name=page_name,
    )
    page = pages_client.get_page(request=request)

    routes = [route for route in page.transition_routes if route.intent not in intent_ids_to_delete and route.intent not in intents.keys()]
    for intent in intents:
        res_text = ResponseMessage.Text(text=[intents[intent]])
        resp_message = ResponseMessage(text=res_text)
        fulfillment = Fulfillment(messages=[resp_message])
        route = TransitionRoute(intent=intent, trigger_fulfillment=fulfillment)
        routes.append(route)
    page.transition_routes = routes

    mask = FieldMask()
    mask.FromJsonString("transitionRoutes")
    request = UpdatePageRequest(
        page=page,
        update_mask=mask,
    )
    response = pages_client.update_page(request=request)
    return response
