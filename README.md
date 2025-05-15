# Claude Anthropic MCP Servers Tool Analyzer

This project provides tools for extracting, formatting, and analyzing MCP (Model Context Protocol) server tools. It consists of three main components:

1. **analyser.py**: Extracts tool information from MCP servers
2. **extract_tools.py**: Formats the extracted tool data in various formats
3. **reporter.py**: Analyzes tool descriptions for potential issues

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/kubiosec-ai/mcp-claude-config-analyser-v2.git
   cd mcp-claude-config-analyser-v2
   ```
2. Create a python environment
   ```
   python3 -m venv .venv
   ```
   ```
   source .venv/bin/activate
   ```
3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
4. Set OpenAI API key
   ```
   export OPENAI_API_KEY=xxxxxxxxxxx
   ```
5. Make a backup of your Claude Desktop Config file
   ```
   cp /Users/xxradar/Library/Application\ Support/Claude/claude_desktop_config.json ./claude_desktop_config.json
   ```
## Usage

### 1. Extract Tool Information from MCP Servers

Use `analyser.py` to connect to MCP servers and extract their tool lists:

```bash
python analyser.py [options]
```

#### Options:

- `--dry-run`: Parse config without connecting to servers
- `--server SERVER`: Process only a specific server
- `--timeout TIMEOUT`: Connection timeout in seconds (default: 30)
- `--config CONFIG`: Path to Anthropic Claude config file
- `--output OUTPUT`: Path to output file (default: config.json)

#### Example:

```bash
# Extract tools from all servers with a 20-second timeout
python analyser.py --timeout 20

# Extract tools from a specific server
python analyser.py --server MCP_DOCKER

# Dry run to test configuration parsing
python analyser.py --dry-run
```

### 2. Format Tool Data

Use `extract_tools.py` to format the extracted tool data in various formats:

```bash
python extract_tools.py [options]
```

#### Options:

- `--config CONFIG`: Path to the config file (default: config.json)
- `--output OUTPUT`: Path to the output file (default: tool_list.json)
- `--format FORMAT`: Output format (default: json)
  - `json`: Standard JSON format with server_name, tool_name, and description fields
  - `csv`: CSV format with server_name, tool_name, and description columns
  - `reporter`: Special format compatible with reporter.py

#### Example:

```bash
# Generate a standard JSON file
python extract_tools.py --output tool_list.json

# Generate a CSV file
python extract_tools.py --format csv --output tool_list.csv

# Generate a reporter-compatible JSON file
python extract_tools.py --format reporter --output reporter_tools.json
```

### 3. Analyze Tool Descriptions

Use `reporter.py` to analyze tool descriptions for potential issues:

```bash
python reporter.py <json-file>
```

#### Example:

```bash
python reporter.py tool_list.json
```

## Output Formats

### 1. Standard JSON Format

```json
[
  {
    "server_name": "playwright",
    "tool_name": "browser_close",
    "description": "Close the page"
  },
  ...
]
```

### 2. CSV Format

```
server_name,tool_name,description
playwright,browser_close,Close the page
...
```

### 3. Reporter Format

```json
{
  "tools": [
    {
      "name": "browser_close",
      "description": "Close the page"
    },
    ...
  ]
}
```

## Common Workflows
### Default 
```
# Extract tools from all servers
python analyser.py --timeout 30

# Format tools 
python extract_tools.py --output tool_list.json

# Analyze tool descriptions
python reporter.py tool_list.json
```
### Extract and Analyze All Tools

```bash
# Extract tools from all servers
python analyser.py --timeout 30

# Format tools for reporter
python extract_tools.py --format reporter --output reporter_tools.json

# Analyze tool descriptions
python reporter.py reporter_tools.json
```

### Extract Tools from a Specific Server

```bash
# Extract tools from a specific server
python analyser.py --server MCP_DOCKER

# Format tools as CSV
python extract_tools.py --format csv --output mcp_docker_tools.csv
```

## Troubleshooting

### Connection Issues

If you encounter connection issues with MCP servers:

1. Increase the timeout value: `--timeout 60`
2. Try connecting to servers individually: `--server SERVER_NAME`
3. Check if the server is running and accessible

### Parsing Errors

If you encounter JSON parsing errors:

1. Use the `--dry-run` option to test configuration parsing
2. Check the format of your config.json file
3. Ensure the MCP server is returning valid JSON responses

## License

[MIT License](LICENSE)
