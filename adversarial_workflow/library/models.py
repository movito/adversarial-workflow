"""Data models for the evaluator library client."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class EvaluatorEntry:
    """An evaluator entry from the library index."""

    name: str
    provider: str
    path: str
    model: str
    category: str
    description: str

    @classmethod
    def from_dict(cls, data: Dict) -> "EvaluatorEntry":
        """Create an EvaluatorEntry from a dictionary."""
        return cls(
            name=data["name"],
            provider=data["provider"],
            path=data["path"],
            model=data["model"],
            category=data["category"],
            description=data["description"],
        )

    @property
    def full_name(self) -> str:
        """Return provider/name format."""
        return f"{self.provider}/{self.name}"


@dataclass
class IndexData:
    """Parsed library index data."""

    version: str
    evaluators: List[EvaluatorEntry]
    categories: Dict[str, str]
    fetched_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "IndexData":
        """Create an IndexData from a dictionary."""
        evaluators = [EvaluatorEntry.from_dict(e) for e in data.get("evaluators", [])]
        return cls(
            version=data.get("version", "unknown"),
            evaluators=evaluators,
            categories=data.get("categories", {}),
            fetched_at=datetime.now(timezone.utc),
        )

    def get_evaluator(self, provider: str, name: str) -> Optional[EvaluatorEntry]:
        """Find an evaluator by provider and name."""
        for e in self.evaluators:
            if e.provider == provider and e.name == name:
                return e
        return None

    def filter_by_provider(self, provider: str) -> List[EvaluatorEntry]:
        """Filter evaluators by provider."""
        return [e for e in self.evaluators if e.provider == provider]

    def filter_by_category(self, category: str) -> List[EvaluatorEntry]:
        """Filter evaluators by category."""
        return [e for e in self.evaluators if e.category == category]


@dataclass
class InstalledEvaluatorMeta:
    """Metadata for an installed evaluator (from _meta block)."""

    source: str
    source_path: str
    version: str
    installed: str
    file_path: Optional[str] = None  # Path to the installed file

    @classmethod
    def from_dict(cls, data: Dict) -> Optional["InstalledEvaluatorMeta"]:
        """Create from _meta dictionary, returns None if invalid."""
        if not data:
            return None
        try:
            return cls(
                source=data.get("source", ""),
                source_path=data.get("source_path", ""),
                version=data.get("version", ""),
                installed=data.get("installed", ""),
            )
        except (KeyError, TypeError):
            return None

    @property
    def provider(self) -> str:
        """Extract provider from source_path."""
        parts = self.source_path.split("/")
        return parts[0] if parts else ""

    @property
    def name(self) -> str:
        """Extract name from source_path."""
        parts = self.source_path.split("/")
        return parts[1] if len(parts) > 1 else ""


@dataclass
class UpdateInfo:
    """Information about an available update."""

    name: str
    installed_version: str
    available_version: str
    is_outdated: bool
    is_local_only: bool = False

    @property
    def status(self) -> str:
        """Human-readable status."""
        if self.is_local_only:
            return "Local only"
        elif self.is_outdated:
            return "Update available"
        else:
            return "Up to date"
