"""Tests for configuration loading and validation."""

import tempfile
from pathlib import Path

import pytest

from mdtoken.config import Config, ConfigError


class TestConfigDefaults:
    """Test Config default values and initialization."""

    def test_default_initialization(self) -> None:
        """Test Config initializes with sensible defaults."""
        config = Config()
        assert config.default_limit == 4000
        assert config.limits == {}
        assert ".git/**" in config.exclude
        assert "node_modules/**" in config.exclude
        assert config.total_limit is None
        assert config.fail_on_exceed is True

    def test_custom_initialization(self) -> None:
        """Test Config can be initialized with custom values."""
        config = Config(
            default_limit=5000,
            limits={"README.md": 8000},
            exclude=["test/**"],
            total_limit=50000,
            fail_on_exceed=False,
        )
        assert config.default_limit == 5000
        assert config.limits == {"README.md": 8000}
        assert config.exclude == ["test/**"]
        assert config.total_limit == 50000
        assert config.fail_on_exceed is False

    def test_repr(self) -> None:
        """Test string representation of Config."""
        config = Config(default_limit=3000)
        repr_str = repr(config)
        assert "Config(" in repr_str
        assert "default_limit=3000" in repr_str


class TestConfigValidation:
    """Test Config validation logic."""

    def test_invalid_default_limit_negative(self) -> None:
        """Test Config raises error for negative default_limit."""
        with pytest.raises(ConfigError, match="default_limit must be a positive integer"):
            Config(default_limit=-1000)

    def test_invalid_default_limit_zero(self) -> None:
        """Test Config raises error for zero default_limit."""
        with pytest.raises(ConfigError, match="default_limit must be a positive integer"):
            Config(default_limit=0)

    def test_invalid_default_limit_type(self) -> None:
        """Test Config raises error for non-integer default_limit."""
        with pytest.raises(ConfigError, match="default_limit must be a positive integer"):
            Config(default_limit="5000")  # type: ignore

    def test_invalid_limits_type(self) -> None:
        """Test Config raises error for non-dict limits."""
        with pytest.raises(ConfigError, match="limits must be a dictionary"):
            Config(limits=["README.md", 5000])  # type: ignore

    def test_invalid_limit_value(self) -> None:
        """Test Config raises error for invalid limit value."""
        with pytest.raises(ConfigError, match="must be a positive integer"):
            Config(limits={"README.md": -1000})

    def test_invalid_exclude_type(self) -> None:
        """Test Config raises error for non-list exclude."""
        with pytest.raises(ConfigError, match="exclude must be a list"):
            Config(exclude="test/**")  # type: ignore

    def test_invalid_total_limit(self) -> None:
        """Test Config raises error for invalid total_limit."""
        with pytest.raises(ConfigError, match="total_limit must be a positive integer"):
            Config(total_limit=-5000)

    def test_invalid_fail_on_exceed_type(self) -> None:
        """Test Config raises error for non-boolean fail_on_exceed."""
        with pytest.raises(ConfigError, match="fail_on_exceed must be a boolean"):
            Config(fail_on_exceed="yes")  # type: ignore


class TestConfigFromFile:
    """Test loading configuration from YAML files."""

    def test_load_valid_config(self) -> None:
        """Test loading a valid configuration file."""
        config_path = Path("tests/fixtures/valid_config.yaml")
        config = Config.from_file(config_path)

        assert config.default_limit == 5000
        assert config.limits["docs/README.md"] == 8000
        assert config.limits["docs/api.md"] == 6000
        assert "archived/**/*.md" in config.exclude
        assert config.total_limit == 50000
        assert config.fail_on_exceed is True

    def test_load_minimal_config(self) -> None:
        """Test loading minimal configuration file."""
        config_path = Path("tests/fixtures/minimal_config.yaml")
        config = Config.from_file(config_path)

        assert config.default_limit == 3000
        assert config.limits == {}
        # Should still have default excludes
        assert ".git/**" in config.exclude
        assert config.total_limit is None

    def test_load_empty_config(self) -> None:
        """Test loading empty configuration file uses defaults."""
        config_path = Path("tests/fixtures/empty_config.yaml")
        config = Config.from_file(config_path)

        assert config.default_limit == 4000
        assert config.limits == {}
        assert ".git/**" in config.exclude
        assert config.total_limit is None

    def test_load_nonexistent_config(self) -> None:
        """Test loading nonexistent config file uses defaults."""
        config_path = Path("tests/fixtures/does_not_exist.yaml")
        config = Config.from_file(config_path)

        # Should use all defaults
        assert config.default_limit == 4000
        assert config.limits == {}

    def test_load_no_config_path(self) -> None:
        """Test from_file with no path searches for .mdtokenrc.yaml."""
        # This will not find a config in the current test directory
        config = Config.from_file(None)
        assert config.default_limit == 4000  # Uses defaults

    def test_load_invalid_yaml(self) -> None:
        """Test loading file with invalid YAML syntax."""
        config_path = Path("tests/fixtures/invalid_yaml.yaml")
        with pytest.raises(ConfigError, match="Invalid YAML"):
            Config.from_file(config_path)

    def test_load_invalid_config_values(self) -> None:
        """Test loading file with invalid configuration values."""
        config_path = Path("tests/fixtures/invalid_config.yaml")
        with pytest.raises(ConfigError, match="default_limit must be a positive integer"):
            Config.from_file(config_path)

    def test_load_non_dict_yaml(self) -> None:
        """Test loading YAML file that doesn't contain a dictionary."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("- list item 1\n- list item 2")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ConfigError, match="must contain a YAML dictionary"):
                Config.from_file(temp_path)
        finally:
            temp_path.unlink()

    def test_load_with_string_path(self) -> None:
        """Test from_file accepts string path."""
        config = Config.from_file(Path("tests/fixtures/minimal_config.yaml"))
        assert config.default_limit == 3000


class TestConfigGetLimit:
    """Test getting limits for specific files."""

    def test_get_limit_default(self) -> None:
        """Test get_limit returns default when no specific limit exists."""
        config = Config(default_limit=5000)
        assert config.get_limit("any/file.md") == 5000

    def test_get_limit_exact_match(self) -> None:
        """Test get_limit returns exact match for file path."""
        config = Config(
            default_limit=4000,
            limits={"docs/README.md": 8000, "api.md": 6000},
        )
        assert config.get_limit("docs/README.md") == 8000
        assert config.get_limit("api.md") == 6000

    def test_get_limit_pattern_match(self) -> None:
        """Test get_limit matches patterns in file path."""
        config = Config(
            default_limit=4000,
            limits={"README.md": 8000},
        )
        # Should match if pattern is in path
        assert config.get_limit("docs/README.md") == 8000
        assert config.get_limit("README.md") == 8000

    def test_get_limit_suffix_match(self) -> None:
        """Test get_limit matches file suffixes."""
        config = Config(
            default_limit=4000,
            limits={".md": 5000},
        )
        assert config.get_limit("any/file.md") == 5000
        assert config.get_limit("test.md") == 5000

    def test_get_limit_no_match(self) -> None:
        """Test get_limit returns default when no pattern matches."""
        config = Config(
            default_limit=4000,
            limits={"README.md": 8000},
        )
        assert config.get_limit("docs/CHANGELOG.md") == 4000


class TestConfigToDict:
    """Test converting Config to dictionary."""

    def test_to_dict_default(self) -> None:
        """Test to_dict with default config."""
        config = Config()
        data = config.to_dict()

        assert data["default_limit"] == 4000
        assert data["limits"] == {}
        assert ".git/**" in data["exclude"]
        assert data["total_limit"] is None
        assert data["fail_on_exceed"] is True

    def test_to_dict_custom(self) -> None:
        """Test to_dict with custom config."""
        config = Config(
            default_limit=5000,
            limits={"README.md": 8000},
            exclude=["test/**"],
            total_limit=50000,
            fail_on_exceed=False,
        )
        data = config.to_dict()

        assert data["default_limit"] == 5000
        assert data["limits"] == {"README.md": 8000}
        assert data["exclude"] == ["test/**"]
        assert data["total_limit"] == 50000
        assert data["fail_on_exceed"] is False

    def test_to_dict_roundtrip(self) -> None:
        """Test that to_dict can be used to recreate Config."""
        original = Config(
            default_limit=5000,
            limits={"README.md": 8000},
            total_limit=50000,
        )
        data = original.to_dict()
        recreated = Config(**data)

        assert recreated.default_limit == original.default_limit
        assert recreated.limits == original.limits
        assert recreated.total_limit == original.total_limit


class TestConfigIntegration:
    """Integration tests for Config."""

    def test_full_workflow(self) -> None:
        """Test complete workflow: create, save, load, use."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
default_limit: 3500
limits:
  "docs/README.md": 7000
exclude:
  - "archived/**"
total_limit: 40000
fail_on_exceed: false
"""
            )
            temp_path = Path(f.name)

        try:
            # Load config
            config = Config.from_file(temp_path)

            # Verify loaded correctly
            assert config.default_limit == 3500
            assert config.get_limit("docs/README.md") == 7000
            assert config.get_limit("other.md") == 3500
            assert "archived/**" in config.exclude
            assert config.total_limit == 40000
            assert config.fail_on_exceed is False

            # Convert to dict
            data = config.to_dict()
            assert data["default_limit"] == 3500
        finally:
            temp_path.unlink()
