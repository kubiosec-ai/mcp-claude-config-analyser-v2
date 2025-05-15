#!/usr/bin/env python3
"""
Extract tool names from MCP server config and create a flattened list.
"""
# Copyright (c) 2025 kubiosec-ai
#
# This file is part of MCP Server Tool Analyzer.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import argparse
import csv
import os
from typing import List, Dict, Any, Tuple, NamedTuple, Optional


class ToolInfo(NamedTuple):
    """Information about a tool."""
    server_name: str
    tool_name: str
    description: str


def extract_server_tools(config_path: str, set_env_vars: bool = True) -> List[ToolInfo]:
    """
    Extract server names, tool names, and descriptions from the config file.
    
    Args:
        config_path: Path to the config.json file
        set_env_vars: If True, set environment variables from the config
        
    Returns:
        List of ToolInfo objects containing server_name, tool_name, and description
    """
    # Read the config file
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Extract server and tool information
    server_tools = []
    
    # Store original environment variables to restore later
    original_env = {}
    
    try:
        # Check if this is the original config file or our processed file
        if "mcpServers" in config:
            # Original config file format
            for server_name, server_config in config.get("mcpServers", {}).items():
                # Set environment variables if requested
                if set_env_vars and "env" in server_config:
                    for key, value in server_config.get("env", {}).items():
                        original_env[key] = os.environ.get(key)
                        os.environ[key] = value
                        print(f"Set environment variable: {key}={value}")
                
                # We don't have tool information in the original config
                # Just add the server name with an empty tool name and description
                server_tools.append(ToolInfo(server_name, "", ""))
        else:
            # Our processed config file format
            for server in config.get("servers", []):
                server_name = server.get("server_name", "unknown")
                
                # Set environment variables if requested
                if set_env_vars and "env" in server:
                    for key, value in server.get("env", {}).items():
                        original_env[key] = os.environ.get(key)
                        os.environ[key] = value
                        print(f"Set environment variable: {key}={value}")
                
                for tool in server.get("tools", []):
                    tool_name = tool.get("name", "unknown")
                    description = tool.get("description", "")
                    server_tools.append(ToolInfo(server_name, tool_name, description))
        
        return server_tools
    
    finally:
        # Restore original environment variables
        if set_env_vars:
            for key, value in original_env.items():
                if value is None:
                    if key in os.environ:
                        del os.environ[key]
                else:
                    os.environ[key] = value


def save_as_csv(server_tools: List[ToolInfo], output_path: str) -> None:
    """
    Save the server names, tool names, and descriptions as a CSV file.
    
    Args:
        server_tools: List of ToolInfo objects
        output_path: Path to save the CSV file
    """
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["server_name", "tool_name", "description"])
        writer.writerows([(tool.server_name, tool.tool_name, tool.description) for tool in server_tools])


def save_as_json(server_tools: List[ToolInfo], output_path: str, reporter_format: bool = False) -> None:
    """
    Save the server names, tool names, and descriptions as a JSON file.
    
    Args:
        server_tools: List of ToolInfo objects
        output_path: Path to save the JSON file
        reporter_format: If True, format the output for the reporter.py script
    """
    if reporter_format:
        # Format for reporter.py: {"tools": [{"name": "tool_name", "description": "actual description"}, ...]}
        tools = [{"name": tool.tool_name, "description": tool.description or f"Server: {tool.server_name}"} for tool in server_tools]
        output = {"tools": tools}
    else:
        # Original format: [{"server_name": "server", "tool_name": "tool", "description": "desc"}, ...]
        output = [{"server_name": tool.server_name, "tool_name": tool.tool_name, "description": tool.description} for tool in server_tools]
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract tool names from MCP server config')
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to the config file (default: config.json)')
    parser.add_argument('--output', type=str, default='tool_list.json',
                        help='Path to the output file (default: tool_list.json)')
    parser.add_argument('--format', type=str, choices=['json', 'csv', 'reporter'], default='json',
                        help='Output format (default: json, reporter for reporter.py compatibility)')
    parser.add_argument('--no-env', action='store_true',
                        help='Do not set environment variables from the config')
    args = parser.parse_args()
    
    # Extract server and tool names
    server_tools = extract_server_tools(args.config, not args.no_env)
    
    # Save to the specified format
    if args.format == 'csv':
        save_as_csv(server_tools, args.output)
    elif args.format == 'reporter':
        save_as_json(server_tools, args.output, reporter_format=True)
    else:
        save_as_json(server_tools, args.output)
    
    print(f"Extracted {len(server_tools)} server-tool pairs to {args.output}")


if __name__ == "__main__":
    main()