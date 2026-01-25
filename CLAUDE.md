# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**pynovelspider** is a Python web scraping tool for downloading novels from Japanese websites (Syosetu and Syosetu18). It features an event-driven architecture for progress tracking, supports proxy connections, and generates multiple output formats (JSON, translatable JSON, Markdown).

## Development Environment

- **Package Manager**: Uses `uv` (modern Python package manager)
- **Python Version**: >=3.11 (specified in `.python-version`)
- **Virtual Environment**: `.venv` directory
- **Type Checking**: Configured with Pyright (`pyrightconfig.json`)

## Common Commands

### Running the Application
```bash
# Download a novel (supports both Syosetu18 R18 content and Syosetu all-ages)
python main.py <novel_code>  # e.g., python main.py n0566gs (R18) or python main.py n3828fz (all-ages)

# Run the NiceGUI-based web interface
python ui/ui.py

# Run tests (see test.py for usage)
python test.py syosetu [optional_novel_code]
```

### Package Management
```bash
# Install dependencies (uses uv)
uv sync

# Add a new dependency
uv add <package_name>

# Update dependencies
uv sync --upgrade
```

### Testing
```bash
# Run specific test module
python test.py syosetu

# Run test with specific novel code
python test.py syosetu n3828fz

# Test files are in tests/ directory and follow pattern test_<name>.py
# Each test module must have a test_main() function
```

## Architecture Overview

### Core Components

1. **Data Models** (`novel_spiders/entities/novel.py`):
   - `Novel`: Main novel entity with title, description, author, chapters
   - `Chapter`: Chapter entity with index, title, episode title, content sections
   - `ChapterContent`: Individual content blocks with keys and content
   - All models use Pydantic for validation

2. **Spider Interface** (`novel_spiders/interfaces/INovelSpider.py`):
   - Abstract base class `INovelSpider` with event system integration
   - Properties: `resource_name`, `headless`, `asset_dir`, `data_root`
   - Abstract method `get_novel()` for concrete implementations
   - Event system for progress tracking (see `docs/progress_event_design.md`)

3. **Concrete Spiders**:
   - `Syosetu18Spider` (`novel_spiders/spiders/syosetu_18_spider.py`): Base implementation for R18 novels with proxy support
   - `SyosetuSpider` (`novel_spiders/spiders/syosetu_spider.py`): Inherits from `Syosetu18Spider`, changes URLs for regular novels

4. **Event System** (`novel_spiders/events/spider_events.py`):
   - Event types: `INFO_PAGE_START`, `INFO_PAGE_COMPLETE`, `CHAPTERS_START`, `CHAPTER_COMPLETE`, `COMPLETE`, `ERROR`
   - Event dispatcher pattern with listener registration
   - `ConsoleProgressListener` provides console output for progress tracking

5. **Utilities**:
   - `novel_save_load.py`: Serialization between Novel objects, JSON, and Markdown
   - `progress_listener.py`: Console-based progress listener implementation
   - `requests_helper.py`: HTTP request utilities

### Data Flow

1. **Download**: Spider downloads novel information and chapters asynchronously
2. **Storage**: Novel saved as JSON in `data/<code>/<code>.json` (Syosetu18) or `data/syosetu/<code>/<code>.json` (Syosetu all-ages)
3. **Translation**: Generates translatable JSON (`<code>_untrans.json`) for external translation tools. Compatible with AITranslator's default filename `合并结果.json`
4. **Generation**: After translation, loads translated JSON and converts to Markdown with translation mapping. Supports character count-based splitting for large novels
5. **Output**: Markdown files can be split by character count (configurable, typically 700,000 characters in main.py)

### File Structure

```
data/                    # Downloaded novel data
  <novel_code>/         # Syosetu18 novels (R18 content)
  syosetu/              # Syosetu novels (all-ages content)
    <novel_code>/       # Each novel gets its own directory
      assets/           # Downloaded images and other assets
        imgs/           # Image files
      <code>.json         # Original novel data
      <code>_untrans.json # Translatable JSON format
      <code>_trans.json   # Translated content (or 合并结果.json for AITranslator compatibility)
      <code>(range).md    # Generated Markdown files (split by character count when configured)
```

## Key Design Patterns

1. **Abstract Factory**: `INovelSpider` interface with concrete implementations
2. **Observer Pattern**: Event system with listeners for progress tracking
3. **Strategy Pattern**: Different spiders for different novel sources
4. **Repository Pattern**: Data serialization utilities in `novel_save_load.py`

## Adding New Features

### New Novel Source
1. Implement `INovelSpider` interface
2. Create new spider in `novel_spiders/spiders/`
3. Implement `get_novel()` method with site-specific parsing logic
4. Follow existing patterns for event dispatching

### Extending Data Models
1. Modify Pydantic models in `novel_spiders/entities/novel.py`
2. Update serialization in `novel_save_load.py`
3. Update spider implementations to populate new fields

### New Output Format
1. Add new methods to `novel_save_load.py`
2. Follow existing patterns for JSON/Markdown serialization
3. Update main entry points to support new format

## Configuration

- **Proxy Settings**: Hardcoded in `Syosetu18Spider.PROXY_URL` (currently `socks5://127.0.0.1:8866`)
- **Data Directory**: Configured via `spider.data_root` property
- **Asset Directory**: Configured via `spider.asset_dir` property
- **Markdown Split Size**: Configurable in `novel_to_markdown()` function (default -1 for no split). Main entry points use different defaults: `main.py` uses 700,000 characters, `test_syosetu.py` uses 500,000 characters for split testing.

## Important Notes

- The project uses asynchronous operations (`asyncio`) for concurrent chapter downloads
- Event listeners should be added to spiders for progress tracking (event system is fully implemented per design docs)
- Data is saved in UTF-8 encoding
- The UI (`ui/ui.py`) is a basic NiceGUI implementation that provides minimal functionality
- Tests require internet connection to download novels (caches results in `data/` directory)

## Development Workflow

1. **Setup**: `uv sync` to install dependencies
2. **Testing**: `python test.py syosetu` to verify functionality
3. **Running**: `python main.py <novel_code>` to download a novel
4. **UI Development**: `python ui/ui.py` to test the web interface

## Dependencies

Key dependencies (see `pyproject.toml` for complete list):
- `beautifulsoup4`: HTML parsing
- `nicegui`: Web UI framework
- `pydantic`: Data validation
- `pywebview`: Desktop web view
- `requests[socks]`: HTTP requests with SOCKS proxy support