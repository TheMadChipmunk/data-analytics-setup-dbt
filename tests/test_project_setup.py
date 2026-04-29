"""
Test Checkpoint 01: Project Initialization and Profile Configuration

Validates dbt project creation, .gitignore setup, and profile configuration.
Tests run in challenge directory, checking for jaffle_shop_dbt/ subdirectory.

Tests check:
- jaffle_shop_dbt/ directory exists
- jaffle_shop_dbt/dbt_project.yml exists and is configured correctly
- jaffle_shop_dbt/.gitignore exists and excludes database files
- ~/.dbt/profiles.yml configured correctly (local only, skipped on glovebox)
"""

import pytest
import yaml
from pathlib import Path


@pytest.fixture
def project_dir():
    """Get jaffle_shop_dbt directory within challenge repo."""
    # Test file location: tests/test_01_project_setup.py
    # Challenge repo structure:
    #   /challenge-directory/
    #   ├── tests/test_01_project_setup.py
    #   ├── Makefile
    #   └── jaffle_shop_dbt/  ← dbt project here
    challenge_dir = Path(__file__).parent.parent
    dbt_project_dir = challenge_dir / "jaffle_shop_dbt"

    assert dbt_project_dir.exists(), (
        f"❌ jaffle_shop_dbt/ directory not found in {challenge_dir}\n"
        f"   Did you create your dbt project? (Section 2.1)\n"
        f"   Run: dbt init jaffle_shop_dbt"
    )

    return dbt_project_dir


class TestProjectInitialization:
    """Test dbt project initialization (Section 2.1)."""

    def test_dbt_project_yml_exists(self, project_dir):
        """dbt_project.yml must exist."""
        dbt_project_file = project_dir / "dbt_project.yml"
        assert dbt_project_file.exists(), (
            "❌ dbt_project.yml not found in jaffle_shop_dbt/\n"
            "   Did you initialize dbt project?\n"
            "   Required: dbt init jaffle_shop_dbt"
        )

    def test_dbt_project_yml_valid(self, project_dir):
        """dbt_project.yml must have correct name and profile."""
        dbt_project_file = project_dir / "dbt_project.yml"

        if not dbt_project_file.exists():
            pytest.skip("dbt_project.yml not found")

        try:
            with open(dbt_project_file, 'r') as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(
                f"❌ dbt_project.yml has YAML syntax error:\n"
                f"   {str(e)}\n"
                f"   Common issues:\n"
                f"   - Use spaces (not tabs) for indentation\n"
                f"   - Check colons after keys\n"
                f"   - Ensure consistent indentation (2 or 4 spaces)"
            )

        assert config.get('name') == 'jaffle_shop_dbt', (
            f"❌ Project name should be 'jaffle_shop_dbt', found '{config.get('name')}'\n"
            "   Did you name your project correctly during dbt init?"
        )

        assert config.get('profile') == 'jaffle_shop_dbt', (
            f"❌ Profile should be 'jaffle_shop_dbt', found '{config.get('profile')}'\n"
            "   Check the profile setting in dbt_project.yml"
        )


class TestGitignoreSetup:
    """Test .gitignore configuration (Section 2.2)."""

    def test_gitignore_exists(self, project_dir):
        """jaffle_shop_dbt/.gitignore must exist."""
        gitignore_file = project_dir / ".gitignore"
        assert gitignore_file.exists(), (
            "❌ .gitignore not found in jaffle_shop_dbt/\n"
            "   Did you create .gitignore? (Section 2.2)\n"
            "   This prevents pushing large database files to GitHub"
        )

    def test_gitignore_excludes_database_files(self, project_dir):
        """gitignore must exclude *.duckdb files."""
        gitignore_file = project_dir / ".gitignore"

        if not gitignore_file.exists():
            pytest.skip(".gitignore not found")

        with open(gitignore_file, 'r') as f:
            content = f.read()

        assert '*.duckdb' in content, (
            "❌ .gitignore doesn't exclude *.duckdb files\n"
            "   Add this line to jaffle_shop_dbt/.gitignore:\n"
            "   *.duckdb"
        )

    def test_gitignore_excludes_target_directory(self, project_dir):
        """gitignore must exclude target/ directory."""
        gitignore_file = project_dir / ".gitignore"

        if not gitignore_file.exists():
            pytest.skip(".gitignore not found")

        with open(gitignore_file, 'r') as f:
            content = f.read()

        assert 'target/' in content, (
            "❌ .gitignore doesn't exclude target/ directory\n"
            "   Add this line to jaffle_shop_dbt/.gitignore:\n"
            "   target/"
        )


class TestProfileConfiguration:
    """Test dbt profile configuration (Section 2.3, local only)."""

    @pytest.fixture
    def is_local_environment(self):
        """Check if running in local environment (not CI/glovebox)."""
        # ~/.dbt/ exists on local machines but not in CI environments
        return (Path.home() / ".dbt").exists()

    def test_profiles_yml_exists(self, is_local_environment):
        """profiles.yml should exist in ~/.dbt/ (local only)."""
        if not is_local_environment:
            pytest.skip("profiles.yml test only runs in local environment")

        profiles_path = Path.home() / ".dbt" / "profiles.yml"
        assert profiles_path.exists(), (
            "❌ profiles.yml not found at ~/.dbt/profiles.yml\n"
            "   Did you configure dbt profiles? (Section 2.3)\n"
            "   Required: Create ~/.dbt/profiles.yml with connection details"
        )

    def test_profiles_yml_has_jaffle_shop(self, is_local_environment):
        """profiles.yml should have jaffle_shop_dbt profile (local only)."""
        if not is_local_environment:
            pytest.skip("profiles.yml test only runs in local environment")

        profiles_path = Path.home() / ".dbt" / "profiles.yml"
        if not profiles_path.exists():
            pytest.skip("profiles.yml not found")

        try:
            with open(profiles_path, 'r') as f:
                profiles = yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(
                f"❌ profiles.yml has YAML syntax error:\n"
                f"   {str(e)}\n"
                f"   Common issues:\n"
                f"   - Use spaces (not tabs) for indentation\n"
                f"   - Check colons after keys\n"
                f"   - Ensure consistent indentation (2 or 4 spaces)"
            )

        assert 'jaffle_shop_dbt' in profiles, (
            "❌ 'jaffle_shop_dbt' profile not found in profiles.yml\n"
            "   Did you set up your dbt profile? (Section 2.3)\n"
            "   Check: dbt debug"
        )

        profile = profiles.get('jaffle_shop_dbt', {})
        assert 'target' in profile, (
            "❌ 'target' key missing in jaffle_shop_dbt profile\n"
            "   Your profile should specify a target environment\n"
            "   Example: target: dev"
        )

        assert 'outputs' in profile, (
            "❌ 'outputs' key missing in jaffle_shop_dbt profile\n"
            "   Your profile should define output configurations\n"
            "   Must include connection details for DuckDB"
        )

        # Check for dev output specifically
        outputs = profile.get('outputs', {})
        assert 'dev' in outputs, (
            "❌ 'dev' output not found in jaffle_shop_dbt profile\n"
            "   Your profile should have a 'dev' output configuration"
        )

        dev_output = outputs.get('dev', {})
        assert dev_output.get('type') == 'duckdb', (
            f"❌ Output type should be 'duckdb', found '{dev_output.get('type')}'\n"
            "   Check your profiles.yml configuration"
        )

        assert 'path' in dev_output, (
            "❌ 'path' key missing in dev output\n"
            "   Must specify path to DuckDB database file\n"
            "   Example: path: dev.duckdb (uses symlink to shared database)"
        )
