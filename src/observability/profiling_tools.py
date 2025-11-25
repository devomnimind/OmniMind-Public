"""Performance Profiling Tools Module.

Implements continuous profiling with flame graph generation for production environments.
Provides real-time performance insights and bottleneck identification.

Reference: docs/OMNIMIND_COMPREHENSIVE_PENDENCIES_REPORT_20251119.md, Section 8.4
"""

import json
import time
import cProfile
import pstats
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar

import structlog

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class ProfileSample:
    """Single profiling sample.

    Attributes:
        timestamp: When the sample was taken
        function_name: Name of the profiled function
        filename: File containing the function
        line_number: Line number where function is defined
        call_count: Number of times function was called
        total_time_ms: Total time spent in function (ms)
        cumulative_time_ms: Cumulative time including sub-calls (ms)
        per_call_time_ms: Average time per call (ms)
    """

    timestamp: float
    function_name: str
    filename: str
    line_number: int
    call_count: int
    total_time_ms: float
    cumulative_time_ms: float
    per_call_time_ms: float = 0.0

    def __post_init__(self) -> None:
        """Calculate per-call time."""
        if self.call_count > 0:
            self.per_call_time_ms = self.total_time_ms / self.call_count

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "function": self.function_name,
            "file": self.filename,
            "line": self.line_number,
            "calls": self.call_count,
            "total_time_ms": self.total_time_ms,
            "cumulative_time_ms": self.cumulative_time_ms,
            "per_call_time_ms": self.per_call_time_ms,
        }


@dataclass
class FlameGraphNode:
    """Node in a flame graph.

    Attributes:
        name: Function name
        value: Time spent in this function (ms)
        children: Child nodes (functions called by this function)
        metadata: Additional metadata
    """

    name: str
    value: float
    children: List["FlameGraphNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: "FlameGraphNode") -> None:
        """Add a child node.

        Args:
            child: Child node to add
        """
        self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for visualization.

        Returns:
            Dictionary representation suitable for flame graph libraries
        """
        result: Dict[str, Any] = {
            "name": self.name,
            "value": self.value,
        }

        if self.metadata:
            result["metadata"] = self.metadata

        if self.children:
            result["children"] = [child.to_dict() for child in self.children]

        return result


@dataclass
class ProfilingConfig:
    """Configuration for continuous profiling.

    Attributes:
        enabled: Whether profiling is enabled
        sample_interval_seconds: Interval between profiling samples
        max_samples: Maximum number of samples to keep
        retention_hours: How long to keep samples
        include_builtins: Include Python built-in functions
        profile_memory: Also profile memory usage
        auto_generate_flamegraph: Automatically generate flame graphs
    """

    enabled: bool = True
    sample_interval_seconds: int = 60
    max_samples: int = 1000
    retention_hours: int = 24
    include_builtins: bool = False
    profile_memory: bool = True
    auto_generate_flamegraph: bool = True


class ContinuousProfiler:
    """Continuous performance profiler.

    Provides production-ready continuous profiling with minimal overhead.
    Collects performance samples and generates insights.

    Example:
        >>> config = ProfilingConfig()
        >>> profiler = ContinuousProfiler(config)
        >>>
        >>> @profiler.profile
        ... def my_function():
        ...     # Function code
        ...     pass
        >>>
        >>> profiler.start()
        >>> # Application runs...
        >>> profiler.stop()
        >>> samples = profiler.get_samples()
    """

    def __init__(self, config: ProfilingConfig):
        """Initialize the continuous profiler.

        Args:
            config: Profiling configuration
        """
        self.config = config
        self._samples: List[ProfileSample] = []
        self._profiler: Optional[cProfile.Profile] = None
        self._is_running = False
        self._profiles_dir = Path.home() / ".omnimind" / "profiles"
        self._profiles_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            "continuous_profiler_initialized",
            sample_interval=config.sample_interval_seconds,
        )

    def start(self) -> None:
        """Start continuous profiling."""
        if not self.config.enabled:
            logger.info("profiling_disabled")
            return

        if self._is_running:
            logger.warning("profiler_already_running")
            return

        self._profiler = cProfile.Profile()
        self._profiler.enable()
        self._is_running = True

        logger.info("profiling_started")

    def stop(self) -> None:
        """Stop continuous profiling and collect final sample."""
        if not self._is_running or self._profiler is None:
            logger.warning("profiler_not_running")
            return

        self._profiler.disable()
        self._is_running = False

        # Collect final sample
        self._collect_sample()

        logger.info("profiling_stopped", samples_collected=len(self._samples))

    def profile(self, func: F) -> F:
        """Decorator to profile a function.

        Args:
            func: Function to profile

        Returns:
            Wrapped function
        """

        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not self.config.enabled:
                return func(*args, **kwargs)

            profiler = cProfile.Profile()
            profiler.enable()

            try:
                result = func(*args, **kwargs)
                return result
            finally:
                profiler.disable()
                self._collect_sample_from_profiler(profiler, func.__name__)

        return wrapper  # type: ignore

    def _collect_sample(self) -> None:
        """Collect a profiling sample from the current profiler."""
        if self._profiler is None:
            return

        self._collect_sample_from_profiler(self._profiler)

    def _collect_sample_from_profiler(
        self,
        profiler: cProfile.Profile,
        function_filter: Optional[str] = None,
    ) -> None:
        """Collect sample from a profiler instance.

        Args:
            profiler: Profiler instance
            function_filter: Optional filter for function name
        """
        # Get statistics
        stats = pstats.Stats(profiler)

        # Parse stats
        for func_key, (
            cc,
            nc,
            tt,
            ct,
            callers,
        ) in stats.stats.items():  # type: ignore[attr-defined]
            filename, line_number, function_name = func_key

            # Filter builtins if configured
            if not self.config.include_builtins:
                if filename.startswith("<") or "built-in" in filename:
                    continue

            # Apply function filter if provided
            if function_filter and function_name != function_filter:
                continue

            # Create sample
            sample = ProfileSample(
                timestamp=time.time(),
                function_name=function_name,
                filename=filename,
                line_number=line_number,
                call_count=nc,
                total_time_ms=tt * 1000,  # Convert to ms
                cumulative_time_ms=ct * 1000,  # Convert to ms
            )

            self._samples.append(sample)

        # Cleanup old samples
        self._cleanup_old_samples()

    def get_samples(
        self,
        limit: Optional[int] = None,
        function_name: Optional[str] = None,
    ) -> List[ProfileSample]:
        """Get collected profiling samples.

        Args:
            limit: Maximum number of samples to return
            function_name: Filter by function name

        Returns:
            List of profiling samples
        """
        samples = self._samples

        if function_name:
            samples = [s for s in samples if s.function_name == function_name]

        if limit:
            samples = samples[-limit:]

        return samples

    def get_top_functions(self, limit: int = 10) -> List[ProfileSample]:
        """Get top functions by total time.

        Args:
            limit: Number of top functions to return

        Returns:
            List of top profiling samples
        """
        # Aggregate samples by function
        function_totals: Dict[str, ProfileSample] = {}

        for sample in self._samples:
            key = f"{sample.filename}:{sample.function_name}"
            if key not in function_totals:
                function_totals[key] = sample
            else:
                # Merge samples
                existing = function_totals[key]
                existing.call_count += sample.call_count
                existing.total_time_ms += sample.total_time_ms
                existing.cumulative_time_ms += sample.cumulative_time_ms

        # Sort by cumulative time
        sorted_functions = sorted(
            function_totals.values(),
            key=lambda s: s.cumulative_time_ms,
            reverse=True,
        )

        return sorted_functions[:limit]

    def export_samples(self) -> str:
        """Export samples as JSON.

        Returns:
            JSON string with all samples
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "sample_count": len(self._samples),
            "samples": [s.to_dict() for s in self._samples],
        }
        return json.dumps(data, indent=2)

    def save_samples(self) -> None:
        """Save profiling samples to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self._profiles_dir / f"profile_{timestamp}.json"

        with open(filename, "w") as f:
            f.write(self.export_samples())

        logger.info("samples_saved", filename=str(filename), count=len(self._samples))

    def _cleanup_old_samples(self) -> None:
        """Remove old samples based on retention settings."""
        if len(self._samples) > self.config.max_samples:
            self._samples = self._samples[-self.config.max_samples :]

        cutoff_time = time.time() - (self.config.retention_hours * 3600)
        self._samples = [s for s in self._samples if s.timestamp >= cutoff_time]

    def clear_samples(self) -> None:
        """Clear all collected samples."""
        self._samples.clear()
        logger.info("samples_cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get profiling statistics.

        Returns:
            Dictionary with statistics
        """
        if not self._samples:
            return {
                "total_samples": 0,
                "is_running": self._is_running,
            }

        return {
            "total_samples": len(self._samples),
            "is_running": self._is_running,
            "top_functions": [s.to_dict() for s in self.get_top_functions(5)],
        }


class FlameGraphGenerator:
    """Flame graph generator from profiling data.

    Generates interactive flame graphs for performance visualization.

    Example:
        >>> samples = profiler.get_samples()
        >>> generator = FlameGraphGenerator()
        >>> flame_graph = generator.generate(samples)
        >>> generator.save_svg(flame_graph, "profile.svg")
    """

    def __init__(self) -> None:
        """Initialize the flame graph generator."""
        self._flamegraphs_dir = Path.home() / ".omnimind" / "flamegraphs"
        self._flamegraphs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("flamegraph_generator_initialized")

    def generate(self, samples: List[ProfileSample]) -> FlameGraphNode:
        """Generate flame graph from profiling samples.

        Args:
            samples: List of profiling samples

        Returns:
            Root node of the flame graph
        """
        # Create root node
        root = FlameGraphNode(name="root", value=0.0)

        # Build call tree
        # Group by file and function
        for sample in samples:
            node = FlameGraphNode(
                name=f"{sample.function_name} ({sample.filename}:{sample.line_number})",
                value=sample.cumulative_time_ms,
                metadata={
                    "calls": sample.call_count,
                    "total_time_ms": sample.total_time_ms,
                    "per_call_time_ms": sample.per_call_time_ms,
                },
            )
            root.add_child(node)

        # Sort children by value (descending)
        root.children.sort(key=lambda n: n.value, reverse=True)

        # Update root value
        root.value = sum(child.value for child in root.children)

        return root

    def to_json(self, flame_graph: FlameGraphNode) -> str:
        """Convert flame graph to JSON.

        Args:
            flame_graph: Flame graph root node

        Returns:
            JSON representation
        """
        return json.dumps(flame_graph.to_dict(), indent=2)

    def save_json(
        self,
        flame_graph: FlameGraphNode,
        filename: Optional[str] = None,
    ) -> str:
        """Save flame graph as JSON.

        Args:
            flame_graph: Flame graph root node
            filename: Optional filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flamegraph_{timestamp}.json"

        filepath = self._flamegraphs_dir / filename

        with open(filepath, "w") as f:
            f.write(self.to_json(flame_graph))

        logger.info("flamegraph_saved", filename=str(filepath))
        return str(filepath)

    def to_svg(self, flame_graph: FlameGraphNode) -> str:
        """Convert flame graph to SVG format.

        This is a simplified SVG generation. In production, you would use
        a proper flame graph library like py-flame or speedscope.

        Args:
            flame_graph: Flame graph root node

        Returns:
            SVG representation
        """
        # Simplified SVG generation
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800">',
            "<style>",
            "  .func { font-family: monospace; font-size: 12px; }",
            "  .time { fill: #333; }",
            "</style>",
        ]

        # Render nodes
        y_offset = 20
        self._render_node_svg(flame_graph, 10, y_offset, 1180, svg_parts)

        svg_parts.append("</svg>")
        return "\n".join(svg_parts)

    def _render_node_svg(
        self,
        node: FlameGraphNode,
        x: float,
        y: float,
        width: float,
        svg_parts: List[str],
        depth: int = 0,
    ) -> None:
        """Recursively render flame graph node as SVG.

        Args:
            node: Node to render
            x: X position
            y: Y position
            width: Width of the box
            svg_parts: List to append SVG parts to
            depth: Current depth in the tree
        """
        height = 20
        color = self._get_color(depth)

        # Draw rectangle
        svg_parts.append(
            f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'fill="{color}" stroke="#000" />'
        )

        # Draw text
        text = f"{node.name} ({node.value:.2f}ms)"
        if len(text) * 7 > width:  # Rough estimation of text width
            text = node.name[: int(width / 7)] + "..."

        svg_parts.append(f'<text x="{x + 5}" y="{y + 15}" class="func time">{text}</text>')

        # Render children
        if node.children:
            child_y = y + height + 2
            child_x = x

            for child in node.children:
                # Calculate width based on proportion
                if node.value > 0:
                    child_width = width * (child.value / node.value)
                else:
                    child_width = width / len(node.children)

                self._render_node_svg(child, child_x, child_y, child_width, svg_parts, depth + 1)
                child_x += child_width

    def save_svg(
        self,
        flame_graph: FlameGraphNode,
        filename: Optional[str] = None,
    ) -> str:
        """Save flame graph as SVG.

        Args:
            flame_graph: Flame graph root node
            filename: Optional filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"flamegraph_{timestamp}.svg"

        filepath = self._flamegraphs_dir / filename

        with open(filepath, "w") as f:
            f.write(self.to_svg(flame_graph))

        logger.info("flamegraph_svg_saved", filename=str(filepath))
        return str(filepath)

    @staticmethod
    def _get_color(depth: int) -> str:
        """Get color for a depth level.

        Args:
            depth: Depth level

        Returns:
            Hex color code
        """
        # Simple color gradient from orange to yellow
        colors = [
            "#fb8c00",  # Orange
            "#ffa726",
            "#ffb74d",
            "#ffcc80",
            "#ffe0b2",
            "#fff3e0",
        ]
        return colors[min(depth, len(colors) - 1)]
