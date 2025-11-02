"""Generate markdown fixtures for performance testing."""

from pathlib import Path


def generate_markdown_file(path: Path, target_tokens: int) -> None:
    """Generate a markdown file with approximately target_tokens tokens.

    Each word is roughly 1.3 tokens on average with cl100k_base encoding.
    """
    words_needed = int(target_tokens / 1.3)

    # Create varied content to be realistic
    content_parts = [
        "# Performance Test Document\n\n",
        "This is a test document for performance benchmarking.\n\n",
    ]

    # Add sections with varied content
    word_count = 0
    section = 1
    while word_count < words_needed:
        content_parts.append(f"## Section {section}\n\n")
        # Add realistic prose
        prose = (
            "This section contains detailed information about various topics. "
            "We include technical documentation, code examples, and explanations. "
            "The content is designed to simulate real-world markdown files used in "
            "software development projects. "
        )
        # Repeat prose to reach target size
        words_in_prose = len(prose.split())
        repeats = min(10, (words_needed - word_count) // words_in_prose + 1)
        content_parts.append(prose * repeats + "\n\n")
        word_count += words_in_prose * repeats
        section += 1

    path.write_text("".join(content_parts), encoding="utf-8")


def main() -> None:
    """Generate performance test fixtures."""
    fixture_dir = Path(__file__).parent

    # Small files (500 tokens each) for 5-file and 10-file tests
    for i in range(10):
        generate_markdown_file(fixture_dir / f"small_{i:02d}.md", 500)

    # Medium files (1000 tokens each) for additional variety
    for i in range(10):
        generate_markdown_file(fixture_dir / f"medium_{i:02d}.md", 1000)

    # Large files (2000 tokens each) for 100-file test
    for i in range(80):
        generate_markdown_file(fixture_dir / f"large_{i:02d}.md", 2000)

    print(f"Generated fixtures in {fixture_dir}")
    print(f"  - 10 small files (~500 tokens each)")
    print(f"  - 10 medium files (~1000 tokens each)")
    print(f"  - 80 large files (~2000 tokens each)")


if __name__ == "__main__":
    main()
