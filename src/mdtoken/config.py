"""Configuration loading and validation for mdtoken."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""

    pass


class Config:
    """Configuration for markdown token limit enforcement.

    Attributes:
        default_limit: Default token limit for all markdown files
        limits: Per-file or per-pattern token limits (overrides default)
        exclude: Glob patterns for files to exclude from checking
        total_limit: Optional total token limit across all files
        fail_on_exceed: Whether to fail (exit 1) when limits are exceeded
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        "default_limit": 4000,
        "limits": {},
        "exclude": [
            ".git/**",
            "node_modules/**",
            "venv/**",
            ".venv/**",
            "build/**",
            "dist/**",
            "__pycache__/**",
        ],
        "total_limit": None,
        "fail_on_exceed": True,
    }

    def __init__(
        self,
        default_limit: int = 4000,
        limits: Optional[Dict[str, int]] = None,
        exclude: Optional[List[str]] = None,
        total_limit: Optional[int] = None,
        fail_on_exceed: bool = True,
    ) -> None:
        """Initialize configuration.

        Args:
            default_limit: Default token limit for all markdown files
            limits: Per-file or per-pattern token limits
            exclude: Glob patterns for files to exclude
            total_limit: Optional total token limit across all files
            fail_on_exceed: Whether to fail when limits are exceeded
        """
        self.default_limit = default_limit
        self.limits = limits or {}
        self.exclude = exclude or self.DEFAULT_CONFIG["exclude"].copy()  # type: ignore
        self.total_limit = total_limit
        self.fail_on_exceed = fail_on_exceed

        self._validate()

    def _validate(self) -> None:
        """Validate configuration values.

        Raises:
            ConfigError: If configuration values are invalid
        """
        if not isinstance(self.default_limit, int) or self.default_limit <= 0:
            raise ConfigError(f"default_limit must be a positive integer, got: {self.default_limit}")

        if not isinstance(self.limits, dict):
            raise ConfigError(f"limits must be a dictionary, got: {type(self.limits).__name__}")

        for pattern, limit in self.limits.items():
            if not isinstance(limit, int) or limit <= 0:
                raise ConfigError(
                    f"Limit for pattern '{pattern}' must be a positive integer, got: {limit}"
                )

        if not isinstance(self.exclude, list):
            raise ConfigError(f"exclude must be a list, got: {type(self.exclude).__name__}")

        if self.total_limit is not None:
            if not isinstance(self.total_limit, int) or self.total_limit <= 0:
                raise ConfigError(
                    f"total_limit must be a positive integer or null, got: {self.total_limit}"
                )

        if not isinstance(self.fail_on_exceed, bool):
            raise ConfigError(
                f"fail_on_exceed must be a boolean, got: {type(self.fail_on_exceed).__name__}"
            )

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from a YAML file.

        Args:
            config_path: Path to configuration file. If None, searches for
                        .mdtokenrc.yaml in current directory.

        Returns:
            Config instance with loaded configuration

        Raises:
            ConfigError: If file cannot be read or contains invalid YAML/config
        """
        # Determine config file path
        if config_path is None:
            config_path = Path.cwd() / ".mdtokenrc.yaml"
        else:
            config_path = Path(config_path)

        # If config file doesn't exist, use defaults
        if not config_path.exists():
            return cls()

        # Load and parse YAML
        try:
            with config_path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML in config file '{config_path}': {e}") from e
        except Exception as e:
            raise ConfigError(f"Failed to read config file '{config_path}': {e}") from e

        # Handle empty YAML file
        if data is None:
            return cls()

        if not isinstance(data, dict):
            raise ConfigError(
                f"Config file must contain a YAML dictionary, got: {type(data).__name__}"
            )

        # Merge with defaults
        config_dict = cls.DEFAULT_CONFIG.copy()
        config_dict.update(data)

        # Create Config instance
        try:
            return cls(
                default_limit=config_dict.get("default_limit", cls.DEFAULT_CONFIG["default_limit"]),
                limits=config_dict.get("limits", {}),
                exclude=config_dict.get("exclude", cls.DEFAULT_CONFIG["exclude"]),
                total_limit=config_dict.get("total_limit"),
                fail_on_exceed=config_dict.get("fail_on_exceed", True),
            )
        except ConfigError:
            raise
        except Exception as e:
            raise ConfigError(f"Failed to create config from file '{config_path}': {e}") from e

    def get_limit(self, file_path: str) -> int:
        """Get token limit for a specific file.

        Checks file-specific limits first, then falls back to default.

        Args:
            file_path: Path to file (can be relative or absolute)

        Returns:
            Token limit for the file
        """
        # Check if there's a specific limit for this exact path
        if file_path in self.limits:
            return self.limits[file_path]

        # Check if any pattern matches (simple string matching for now)
        # In the future, could use glob pattern matching here
        for pattern, limit in self.limits.items():
            if pattern in file_path or file_path.endswith(pattern):
                return limit

        # Fall back to default
        return self.default_limit

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "default_limit": self.default_limit,
            "limits": self.limits,
            "exclude": self.exclude,
            "total_limit": self.total_limit,
            "fail_on_exceed": self.fail_on_exceed,
        }

    def __repr__(self) -> str:
        """String representation of Config."""
        return (
            f"Config(default_limit={self.default_limit}, "
            f"limits={self.limits}, "
            f"exclude={self.exclude}, "
            f"total_limit={self.total_limit}, "
            f"fail_on_exceed={self.fail_on_exceed})"
        )
