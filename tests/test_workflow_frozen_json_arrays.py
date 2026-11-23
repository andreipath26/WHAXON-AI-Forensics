"""JSON-shaped plan arrays stay immutable and digest-stable."""
import json

import pytest

from whaxon.core.workflow import WorkflowPlan, WorkflowTask


def test_workflow_plan_metadata_arrays_keep_json_shape_and_immutability():
    plan = WorkflowPlan(
        mission_id="mission-1",
        tasks=(WorkflowTask(
            id="task-1",
            capability_id="tool.verify_sqli",
            target="http://192.0.2.10/search",
            impact="moderate",
        ),),
        metadata={
            "coverage_contract": {
                "schema_version": 1,
                "checklist": ["sqli"],
                "requested": ["sqli"],
                "included": [],
                "dispositions": [],
            },
        },
    )

    exported = plan.to_dict()["metadata"]["coverage_contract"]
    assert isinstance(exported["checklist"], list)
    assert isinstance(exported["dispositions"], list)
    assert exported["checklist"] == ["sqli"]
    with pytest.raises(TypeError, match="immutable"):
        exported["checklist"].append("xss")

    round_trip = WorkflowPlan.from_dict(json.loads(json.dumps(plan.to_dict())))
    assert round_trip.digest == plan.digest
    assert round_trip.to_dict()["metadata"]["coverage_contract"]["checklist"] == ["sqli"]
