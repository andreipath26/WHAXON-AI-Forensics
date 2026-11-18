import pytest
from pydantic import ValidationError

from whaxon.interfaces.web.api_contracts import (
    WorkflowRunAccepted,
    WorkflowRunRequest,
    openapi_document,
)


def test_workflow_run_request_defaults_and_bounds():
    assert WorkflowRunRequest.model_validate({}).model_dump() == {
        "max_tasks": 100,
        "max_attempts": 2,
        "max_concurrency": 4,
    }
    request = WorkflowRunRequest.model_validate(
        {"max_tasks": 1, "max_attempts": 1000, "max_concurrency": 4},
    )
    assert request.max_tasks == 1
    assert request.max_attempts == 1000


@pytest.mark.parametrize(
    "payload",
    [
        {"max_tasks": True},
        {"max_tasks": 0},
        {"max_tasks": 1001},
        {"max_attempts": 1.0},
    ],
)
def test_workflow_run_request_rejects_invalid_fields(payload):
    with pytest.raises(ValidationError):
        WorkflowRunRequest.model_validate(payload)


def test_workflow_run_request_ignores_unknown_fields_for_compatibility():
    request = WorkflowRunRequest.model_validate({"future_option": "ignored"})
    assert request.max_tasks == 100


def test_openapi_publishes_run_request_and_acknowledgement_schemas():
    document = openapi_document()
    operation = document["paths"]["/api/v2/workflows/{plan_id}/run"]["post"]
    schemas = document["components"]["schemas"]

    assert document["openapi"] == "3.1.0"
    assert operation["security"] == [{"BasicAuth": []}]
    assert document["components"]["securitySchemes"]["BasicAuth"]["scheme"] == "basic"
    assert operation["requestBody"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/WorkflowRunRequest",
    }
    assert operation["responses"]["202"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/WorkflowRunAccepted",
    }
    assert schemas["WorkflowRunRequest"]["properties"]["max_tasks"]["minimum"] == 1
    assert schemas["WorkflowRunRequest"]["properties"]["max_tasks"]["maximum"] == 1000
    assert schemas["WorkflowRunAccepted"]["properties"]["execution_completed"]["type"] == "boolean"
    assert "not execution completion" in document["info"]["description"]


def test_run_acknowledgement_requires_durable_request_identity():
    with pytest.raises(ValidationError):
        WorkflowRunAccepted.model_validate({"plan_id": "plan"})
