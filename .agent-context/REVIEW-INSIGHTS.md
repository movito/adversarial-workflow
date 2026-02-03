# Review Insights Index

Knowledge extracted from code reviews for future reference (KIT-ADR-0019).

---

## Evaluators (`adversarial_workflow/evaluators/`)

### ADV-0029: YAML field validation should check for bool coercion
- YAML parses `yes`/`no`/`true`/`false` as booleans, not strings
- When validating integer fields, explicitly check `isinstance(value, bool)` before `isinstance(value, int)` (since bool is a subclass of int in Python)
- Pattern used in `discovery.py:126-152`

### ADV-0029: Precedence logging pattern for config overrides
- When multiple sources can provide a value (CLI > config > default), log which source is active
- Pattern: `print(f"Using {setting}: {value} ({source})")`
- Helps users understand where their configuration comes from

---

## Testing (`tests/`)

### ADV-0029: Integration testing subprocess timeouts with mock scripts
- Create lightweight mock scripts that sleep for configurable durations
- Test timeout success: mock sleeps less than timeout
- Test timeout failure: mock sleeps longer than timeout
- Verify timeout values flow through entire stack
- See `tests/test_timeout_integration.py` for pattern

### ADV-0029: Use raw strings for regex in pytest.raises match
- Style preference: `match=r"pattern.*here"` not `match="pattern.*here"`
- Prevents escape sequence issues

---

## CLI (`adversarial_workflow/cli.py`)

### ADV-0029: Validation at execution time for CLI overrides
- CLI flag validation (e.g., max values) should happen at execution time, not argument parsing
- Allows config defaults to be used if CLI flag not provided
- Pattern: Check `args.flag is not None` before applying validation

---

---

## Library Module (`adversarial_workflow/library/`)

### ADV-0013: YAML document separator stripping for concatenation
- When concatenating YAML content (e.g., adding provenance headers), strip leading `---` document separator
- Without stripping, results in multi-document YAML that some parsers reject
- Pattern: `if yaml_content.startswith("---"): yaml_content = yaml_content[3:].lstrip("\n")`

### ADV-0013: Cross-provider file collision prevention
- Use `{provider}-{name}.yml` naming instead of just `{name}.yml`
- Example: `google-gemini-flash.yml` vs `openai-gpt-4o.yml`
- Prevents collisions when different providers have evaluators with same name

### ADV-0013: HTTPError must be caught before URLError
- `urllib.error.HTTPError` is a subclass of `urllib.error.URLError`
- Catch HTTPError first to get proper HTTP status codes
- Pattern: `except HTTPError as e: ... except URLError as e: ...`

### ADV-0013: Timezone-aware UTC timestamps
- Use `datetime.now(timezone.utc)` not `datetime.now()` with appended "Z"
- Proper format: `.isoformat(timespec="seconds").replace("+00:00", "Z")`
- Prevents naive datetime + fake "Z" suffix

### ADV-0013: Cache with stale fallback for offline resilience
- Implement TTL-based cache with `get_stale()` method for expired-but-usable data
- On network error, fall back to stale cache before raising exception
- Pattern in `CacheManager` with separate `get()` and `get_stale()` methods

### ADV-0013: Provenance tracking via `_meta` block
- Installed library items should include machine-readable provenance
- Structure: `_meta: { source, source_path, version, installed }`
- Enables update checking and audit trails

---

## Testing (`tests/`)

### ADV-0013: pytest fixtures cannot be renamed with underscore
- Built-in fixtures like `capsys` cannot be renamed to `_capsys`
- Either use the fixture or remove the parameter entirely
- Don't try to suppress "unused" warnings by renaming fixtures

### ADV-0013: Integration tests should be marked for selective execution
- Use `pytest.mark.network` or similar for tests requiring network
- Allows `pytest -m "not network"` for offline CI runs
- Pattern: `pytestmark = pytest.mark.network` at module level

*Last updated: 2026-02-03*
