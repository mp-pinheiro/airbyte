#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import filecmp
import os

import pytest
import yaml
from octavia_cli.create.renderer import SpecRenderer

pytestmark = pytest.mark.integration
SOURCE_SPECS = "../airbyte-config/init/src/main/resources/seed/source_specs.yaml"
DESTINATION_SPECS = "../airbyte-config/init/src/main/resources/seed/destination_specs.yaml"


@pytest.mark.parametrize("spec_type, spec_file_path", [("source", SOURCE_SPECS), ("destination", DESTINATION_SPECS)])
def test_rendering_all_specs(spec_type, spec_file_path, octavia_project_directory):
    with open(spec_file_path, "r") as f:
        specs = yaml.load(f, yaml.FullLoader)
    rendered_specs = []
    for i, spec in enumerate(specs):
        renderer = SpecRenderer(
            f"{spec['dockerImage'].split(':')[0].split('/')[-1]}.yaml",
            spec_type,
            f"id-{i}",
            spec["dockerImage"].split(":")[0],
            spec["dockerImage"].split(":")[-1],
            spec["spec"]["documentationUrl"],
            spec["spec"]["connectionSpecification"],
        )
        output_path = renderer.write_yaml(octavia_project_directory)
        rendered_specs.append(output_path)
    assert len(rendered_specs) == len(specs)
    for rendered_spec in rendered_specs:
        with open(rendered_spec, "r") as f:
            parsed_yaml = yaml.load(f, yaml.FullLoader)
            assert all(
                [
                    expected_field in parsed_yaml
                    for expected_field in ["definition_type", "definition_id", "definition_image", "definition_version", "configuration"]
                ]
            )


EXPECTED_RENDERED_YAML_PATH = "tests/integration/test_create/expected_rendered_yaml"


@pytest.mark.parametrize(
    "definition_name, spec_type, input_spec_path, expected_yaml_path",
    [
        ("my_postgres_source", "source", "source_postgres/input_spec.yaml", "source_postgres/expected.yaml"),
        ("my_postgres_destination", "destination", "destination_postgres/input_spec.yaml", "destination_postgres/expected.yaml"),
    ],
)
def test_expected_output(definition_name, spec_type, input_spec_path, expected_yaml_path, octavia_project_directory):
    with open(os.path.join(EXPECTED_RENDERED_YAML_PATH, input_spec_path), "r") as f:
        input_spec = yaml.load(f, yaml.FullLoader)
    renderer = SpecRenderer(
        definition_name,
        spec_type,
        "foobar",
        input_spec["dockerImage"].split(":")[0],
        input_spec["dockerImage"].split(":")[-1],
        input_spec["spec"]["documentationUrl"],
        input_spec["spec"]["connectionSpecification"],
    )
    output_path = renderer.write_yaml("/users/augustin/Desktop")
    expect_output_path = os.path.join(EXPECTED_RENDERED_YAML_PATH, expected_yaml_path)
    assert filecmp.cmp(output_path, expect_output_path)
