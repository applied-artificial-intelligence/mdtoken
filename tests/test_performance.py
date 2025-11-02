"""Performance benchmarks for mdtoken."""

import time
from pathlib import Path

import pytest

from mdtoken.config import Config
from mdtoken.enforcer import LimitEnforcer


class TestPerformanceBenchmarks:
    """Performance benchmark tests to ensure mdtoken meets speed requirements."""

    @pytest.fixture
    def perf_fixtures_dir(self) -> Path:
        """Get path to performance fixtures directory."""
        return Path(__file__).parent / "fixtures" / "performance"

    @pytest.fixture
    def config(self) -> Config:
        """Create config for performance testing."""
        return Config(default_limit=10000)  # High limit to avoid violations

    def test_benchmark_5_files_under_500ms(
        self, perf_fixtures_dir: Path, config: Config
    ) -> None:
        """Benchmark: 5 files should complete in < 500ms.

        Acceptance criterion: Process 5 markdown files in under 500ms.
        """
        # Select 5 small files
        files = sorted(perf_fixtures_dir.glob("small_*.md"))[:5]
        assert len(files) == 5, "Need 5 small fixture files"

        enforcer = LimitEnforcer(config)

        # Measure execution time
        start = time.perf_counter()
        result = enforcer.check_files(check_files=files)
        duration_ms = (time.perf_counter() - start) * 1000

        # Verify results
        assert result.passed, "All files should pass"
        assert result.total_files == 5

        # Performance assertion
        assert (
            duration_ms < 500
        ), f"Processing 5 files took {duration_ms:.1f}ms (target: < 500ms)"

        print(f"\n✅ 5 files processed in {duration_ms:.1f}ms (target: < 500ms)")

    def test_benchmark_10_files_under_1000ms(
        self, perf_fixtures_dir: Path, config: Config
    ) -> None:
        """Benchmark: 10 files should complete in < 1000ms.

        Acceptance criterion: Process 10 markdown files in under 1 second.
        """
        # Select 10 files (5 small + 5 medium for variety)
        small_files = sorted(perf_fixtures_dir.glob("small_*.md"))[:5]
        medium_files = sorted(perf_fixtures_dir.glob("medium_*.md"))[:5]
        files = small_files + medium_files
        assert len(files) == 10, "Need 10 fixture files"

        enforcer = LimitEnforcer(config)

        # Measure execution time
        start = time.perf_counter()
        result = enforcer.check_files(check_files=files)
        duration_ms = (time.perf_counter() - start) * 1000

        # Verify results
        assert result.passed, "All files should pass"
        assert result.total_files == 10

        # Performance assertion
        assert (
            duration_ms < 1000
        ), f"Processing 10 files took {duration_ms:.1f}ms (target: < 1000ms)"

        print(f"\n✅ 10 files processed in {duration_ms:.1f}ms (target: < 1000ms)")

    def test_benchmark_100_files_under_5000ms(
        self, perf_fixtures_dir: Path, config: Config
    ) -> None:
        """Benchmark: 100 files should complete in < 5000ms.

        Acceptance criterion: Process 100 markdown files in under 5 seconds.
        """
        # Select 100 files (all small + all medium + 80 large)
        small_files = sorted(perf_fixtures_dir.glob("small_*.md"))
        medium_files = sorted(perf_fixtures_dir.glob("medium_*.md"))
        large_files = sorted(perf_fixtures_dir.glob("large_*.md"))
        files = small_files + medium_files + large_files
        assert len(files) == 100, f"Need 100 fixture files, found {len(files)}"

        enforcer = LimitEnforcer(config)

        # Measure execution time
        start = time.perf_counter()
        result = enforcer.check_files(check_files=files)
        duration_ms = (time.perf_counter() - start) * 1000

        # Verify results
        assert result.passed, "All files should pass"
        assert result.total_files == 100

        # Performance assertion
        assert (
            duration_ms < 5000
        ), f"Processing 100 files took {duration_ms:.1f}ms (target: < 5000ms)"

        print(f"\n✅ 100 files processed in {duration_ms:.1f}ms (target: < 5000ms)")

    def test_token_counting_performance(
        self, perf_fixtures_dir: Path, config: Config
    ) -> None:
        """Verify token counting performance on individual files."""
        from mdtoken.counter import TokenCounter

        counter = TokenCounter()

        # Test on a large file
        large_file = sorted(perf_fixtures_dir.glob("large_*.md"))[0]
        text = large_file.read_text(encoding="utf-8")

        # Measure token counting speed
        iterations = 100
        start = time.perf_counter()
        for _ in range(iterations):
            token_count = counter.count_tokens(text)
        duration_ms = (time.perf_counter() - start) * 1000 / iterations

        # Should be very fast (< 10ms per file for ~2000 token file)
        assert (
            duration_ms < 10
        ), f"Token counting took {duration_ms:.2f}ms per file (target: < 10ms)"

        print(
            f"\n✅ Token counting: {duration_ms:.2f}ms per file "
            f"(~{token_count} tokens, target: < 10ms)"
        )

    def test_performance_scaling(
        self, perf_fixtures_dir: Path, config: Config
    ) -> None:
        """Verify performance scales linearly with file count."""
        enforcer = LimitEnforcer(config)

        # Get all fixture files
        all_files = sorted(perf_fixtures_dir.glob("*.md"))

        # Test different file counts
        test_sizes = [5, 10, 20, 50, 100]
        times = []

        for size in test_sizes:
            files = all_files[:size]
            start = time.perf_counter()
            result = enforcer.check_files(check_files=files)
            duration_ms = (time.perf_counter() - start) * 1000
            times.append(duration_ms)

            assert result.passed, f"Files should pass for size {size}"
            print(
                f"  {size:3d} files: {duration_ms:6.1f}ms "
                f"({duration_ms/size:.2f}ms per file)"
            )

        # Verify roughly linear scaling (time per file should be consistent)
        time_per_file = [t / s for t, s in zip(times, test_sizes)]
        avg_time_per_file = sum(time_per_file) / len(time_per_file)
        max_deviation = max(abs(t - avg_time_per_file) / avg_time_per_file for t in time_per_file)

        # Allow up to 50% deviation (accounts for startup overhead and variability)
        assert (
            max_deviation < 0.5
        ), f"Performance scaling should be linear (max deviation: {max_deviation:.1%})"

        print(
            f"\n✅ Performance scales linearly: "
            f"avg {avg_time_per_file:.2f}ms per file, "
            f"max deviation {max_deviation:.1%}"
        )


class TestPerformanceRegression:
    """Tests to detect performance regressions over time."""

    @pytest.fixture
    def perf_fixtures_dir(self) -> Path:
        """Get path to performance fixtures directory."""
        return Path(__file__).parent / "fixtures" / "performance"

    def test_no_regression_typical_workload(self, perf_fixtures_dir: Path) -> None:
        """Ensure typical workload (10 files) meets performance baseline.

        This test establishes a baseline for regression detection.
        If this test starts failing, it indicates a performance regression.
        """
        config = Config(default_limit=10000)
        enforcer = LimitEnforcer(config)

        # Typical workload: 10 mixed files
        files = (
            sorted(perf_fixtures_dir.glob("small_*.md"))[:5]
            + sorted(perf_fixtures_dir.glob("medium_*.md"))[:5]
        )

        # Run multiple times to get stable measurement
        timings = []
        for _ in range(5):
            start = time.perf_counter()
            result = enforcer.check_files(check_files=files)
            duration_ms = (time.perf_counter() - start) * 1000
            timings.append(duration_ms)
            assert result.passed

        # Use median to avoid outliers
        median_time = sorted(timings)[len(timings) // 2]

        # Baseline: 10 files should take < 200ms (much stricter than 1000ms acceptance)
        # This catches gradual performance degradation
        assert (
            median_time < 200
        ), f"Performance regression detected: {median_time:.1f}ms (baseline: < 200ms)"

        print(
            f"\n✅ No performance regression: {median_time:.1f}ms median "
            f"(baseline: < 200ms, timings: {[f'{t:.1f}' for t in timings]})"
        )
