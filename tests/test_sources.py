"""
Test Checkpoint 03: Source Definitions

Validates source configuration in models/schema.yml.
Tests run in challenge directory, checking jaffle_shop_dbt/models/schema.yml.

Tests check:
- models/schema.yml exists
- Valid YAML syntax
- Contains 'jaffle_shop' source with 3 tables
- Source references correct schema (raw)
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def project_dir():
    """Get jaffle_shop_dbt directory within challenge repo."""
    challenge_dir = Path(__file__).parent.parent
    dbt_project_dir = challenge_dir / "jaffle_shop_dbt"

    assert dbt_project_dir.exists(), (
        f"❌ jaffle_shop_dbt/ directory not found in {challenge_dir}\n"
        f"   Did you create your dbt project? (Section 2.1)\n"
        f"   Run: dbt init jaffle_shop_dbt"
    )

    return dbt_project_dir


@pytest.fixture
def schema_file(project_dir):
    """Get schema.yml file (could be schema.yml or sources.yml)."""
    possible_locations = [
        project_dir / "models" / "schema.yml",
        project_dir / "models" / "sources.yml",
    ]

    for location in possible_locations:
        if location.exists():
            return location

    return None


class TestSourceDefinitions:
    """Test source configuration (Section 3.2)."""

    def test_schema_file_exists(self, schema_file):
        """models/schema.yml must exist."""
        assert schema_file is not None, (
            "❌ No schema file found in jaffle_shop_dbt/models/\n"
            "   Expected: jaffle_shop_dbt/models/schema.yml\n"
            "   Did you create the file? (Section 3.2)\n"
            "   This file defines your raw data sources"
        )

    def test_schema_file_valid_yaml(self, schema_file):
        """schema.yml must have valid YAML syntax."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        try:
            with open(schema_file, 'r') as f:
                content = yaml.safe_load(f)
                assert content is not None, "YAML file is empty"
        except yaml.YAMLError as e:
            pytest.fail(
                f"❌ schema.yml has invalid YAML syntax\n"
                f"   Error: {str(e)}\n"
                f"   Common issues:\n"
                f"   - Inconsistent indentation (use 2 spaces, not tabs)\n"
                f"   - Missing spaces after colons: 'name: value' not 'name:value'\n"
                f"   - Misaligned list items (dashes must align)"
            )

    def test_has_version_2(self, schema_file):
        """schema.yml must specify version: 2."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        with open(schema_file, 'r') as f:
            content = yaml.safe_load(f)

        assert 'version' in content, (
            "❌ Missing 'version: 2' in schema.yml\n"
            "   dbt requires version specification at top of file"
        )

        assert content['version'] == 2, (
            f"❌ version should be 2, found {content['version']}"
        )

    def test_has_sources_section(self, schema_file):
        """schema.yml must have sources section."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        with open(schema_file, 'r') as f:
            content = yaml.safe_load(f)

        assert 'sources' in content, (
            "❌ Missing 'sources' key in schema.yml\n"
            "   File should contain source definitions\n"
            "   Example:\n"
            "   sources:\n"
            "     - name: jaffle_shop"
        )

        assert len(content['sources']) > 0, (
            "❌ No sources defined\n"
            "   Expected: jaffle_shop source with 3 tables"
        )

    def test_jaffle_shop_source_exists(self, schema_file):
        """Source named 'jaffle_shop' must exist."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        with open(schema_file, 'r') as f:
            content = yaml.safe_load(f)

        sources = content.get('sources', [])
        jaffle_source = next((s for s in sources if s.get('name') == 'jaffle_shop'), None)

        assert jaffle_source is not None, (
            "❌ Source 'jaffle_shop' not found\n"
            "   Expected in schema.yml (Section 3.2)\n"
            "   Add:\n"
            "   - name: jaffle_shop\n"
            "     schema: raw"
        )

    def test_source_has_schema_raw(self, schema_file):
        """jaffle_shop source must reference 'raw' schema."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        with open(schema_file, 'r') as f:
            content = yaml.safe_load(f)

        sources = content.get('sources', [])
        jaffle_source = next((s for s in sources if s.get('name') == 'jaffle_shop'), None)

        if jaffle_source is None:
            pytest.skip("jaffle_shop source not found")

        assert 'schema' in jaffle_source, (
            "❌ Missing 'schema' field in jaffle_shop source\n"
            "   Section 3.2 requires: schema: raw\n"
            "   This tells dbt where to find the raw tables in DuckDB"
        )

        assert jaffle_source['schema'] == 'raw', (
            f"❌ schema should be 'raw', found '{jaffle_source['schema']}'\n"
            "   Your raw data tables are in the 'raw' schema"
        )

    def test_source_has_three_tables(self, schema_file):
        """jaffle_shop source must have 3 tables."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        with open(schema_file, 'r') as f:
            content = yaml.safe_load(f)

        sources = content.get('sources', [])
        jaffle_source = next((s for s in sources if s.get('name') == 'jaffle_shop'), None)

        if jaffle_source is None:
            pytest.skip("jaffle_shop source not found")

        tables = jaffle_source.get('tables', [])
        assert len(tables) >= 3, (
            f"❌ Expected at least 3 tables, found {len(tables)}\n"
            "   Required tables: raw_customers, raw_orders, raw_payments\n"
            "   Add them to the 'tables' section in schema.yml"
        )

    def test_has_required_table_names(self, schema_file):
        """Source must include required table names."""
        if schema_file is None:
            pytest.skip("schema.yml not found")

        with open(schema_file, 'r') as f:
            content = yaml.safe_load(f)

        sources = content.get('sources', [])
        jaffle_source = next((s for s in sources if s.get('name') == 'jaffle_shop'), None)

        if jaffle_source is None:
            pytest.skip("jaffle_shop source not found")

        tables = jaffle_source.get('tables', [])
        table_names = [t.get('name') for t in tables]

        required_tables = ['raw_customers', 'raw_orders', 'raw_payments']
        missing_tables = [t for t in required_tables if t not in table_names]

        assert len(missing_tables) == 0, (
            f"❌ Missing required tables: {', '.join(missing_tables)}\n"
            "   Add these tables to your jaffle_shop source in schema.yml"
        )


class TestDbtProjectModelConfig:
    """Test dbt_project.yml model layer configuration (Section 3.1)."""

    def test_dbt_project_yml_has_model_layers_config(self, project_dir):
        """dbt_project.yml must have staging model config."""
        dbt_project_file = project_dir / "dbt_project.yml"

        if not dbt_project_file.exists():
            pytest.skip("dbt_project.yml not found")

        try:
            with open(dbt_project_file, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError:
            pytest.skip("dbt_project.yml has YAML error")

        models = config.get('models', {})
        project_models = models.get('jaffle_shop_dbt', {}) or {}

        required_layers = ['staging']
        missing = [layer for layer in required_layers if layer not in project_models]

        assert not missing, (
            f"❌ Missing model layer config in dbt_project.yml: {missing}\n"
            "   Did you update dbt_project.yml? (Section 3.1)\n"
            "   Add the staging section under 'models: jaffle_shop_dbt:'"
        )
