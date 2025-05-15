from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import asyncio
import os
import sys
import argparse
from typing import Dict, List, Any
import logging
from datetime import datetime

# Custom JSON encoder to handle non-serializable objects
class MCPEncoder(json.JSONEncoder):
    def default(self, obj):
        # Convert objects to their dict representation if possible
        try:
            return obj.__dict__
        except AttributeError:
            # If the object doesn't have __dict__, convert to string
            return str(obj)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("mcp-analyser")

# Path to the config file
CONFIG_PATH = "../mcp-claude-config-analyser/config.json"
# Output file path
OUTPUT_PATH = "config.json"
# Connection timeout in seconds
CONNECTION_TIMEOUT = 30

async def extract_tools_from_server(server_name: str, server_config: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
    """
    Connect to an MCP server and extract its tool list
    
    Args:
        server_name: Name of the MCP server
        server_config: Configuration for the MCP server
        dry_run: If True, don't actually connect to the server
        
    Returns:
        Dictionary containing server name and its tools
    """
    logger.info(f"Processing server: {server_name}")
    
    command = server_config.get("command")
    args = server_config.get("args", [])
    env = server_config.get("env", {})
    
    # Create base result with server config
    result = {
        "server_name": server_name,
        "command": command,
        "args": args,
        "env": env,
        "tools": []
    }
    
    if dry_run:
        logger.info(f"Dry run mode - skipping connection to {server_name}")
        return result
    
    # Set environment variables
    original_env = {}
    for key, value in env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        logger.info(f"Connecting to server: {server_name}")
        server_params = StdioServerParameters(
            command=command,
            args=args
        )
        
        try:
            # Create a timeout for the connection
            async with asyncio.timeout(CONNECTION_TIMEOUT):
                async with stdio_client(server_params) as (read, write):
                    logger.info(f"Connected to {server_name}, initializing session")
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        logger.info(f"Session initialized for {server_name}, listing tools")
                        tools = await session.list_tools()
                        
                        for tool in tools.tools:
                            result["tools"].append({
                                "name": tool.name,
                                "description": tool.description,
                                "inputSchema": tool.inputSchema,
                                "annotations": tool.annotations,
                            })
                        
                        logger.info(f"Successfully extracted {len(result['tools'])} tools from {server_name}")
        except asyncio.TimeoutError:
            logger.error(f"Connection to {server_name} timed out after {CONNECTION_TIMEOUT} seconds")
        except Exception as e:
            logger.error(f"Error connecting to {server_name}: {str(e)}")
        
        return result
    
    finally:
        # Restore original environment variables
        for key, value in original_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value

async def main():
    global CONFIG_PATH, OUTPUT_PATH, CONNECTION_TIMEOUT
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MCP Server Tool Analyser')
    parser.add_argument('--dry-run', action='store_true', help='Only parse config, do not connect to servers')
    parser.add_argument('--config', type=str, default=CONFIG_PATH, help='Path to config file')
    parser.add_argument('--output', type=str, default=OUTPUT_PATH, help='Path to output file')
    parser.add_argument('--timeout', type=int, default=CONNECTION_TIMEOUT, help='Connection timeout in seconds')
    parser.add_argument('--server', type=str, help='Process only a specific server')
    args = parser.parse_args()
    
    CONFIG_PATH = args.config
    OUTPUT_PATH = args.output
    CONNECTION_TIMEOUT = args.timeout
    
    # Load the config file
    try:
        logger.info(f"Loading config file from {CONFIG_PATH}")
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading config file: {str(e)}")
        return
    
    # Extract MCP server configurations
    mcp_servers = config.get("mcpServers", {})
    logger.info(f"Found {len(mcp_servers)} MCP servers in config")
    
    # Filter servers if --server argument is provided
    if args.server:
        if args.server in mcp_servers:
            mcp_servers = {args.server: mcp_servers[args.server]}
            logger.info(f"Processing only server: {args.server}")
        else:
            logger.error(f"Server {args.server} not found in config")
            return
    
    # Process each server
    tasks = []
    for server_name, server_config in mcp_servers.items():
        task = extract_tools_from_server(server_name, server_config, args.dry_run)
        tasks.append(task)
    
    # Wait for all tasks to complete
    logger.info(f"Starting processing of {len(tasks)} servers")
    start_time = datetime.now()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    end_time = datetime.now()
    
    # Filter out exceptions
    server_results = []
    for result in results:
        if isinstance(result, Exception):
            logger.error(f"Error processing server: {str(result)}")
        else:
            server_results.append(result)
    
    # Save results to output file
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "servers_processed": len(mcp_servers),
            "servers_successful": len(server_results),
            "processing_time_seconds": (end_time - start_time).total_seconds()
        },
        "servers": server_results
    }
    
    logger.info(f"Writing results to {OUTPUT_PATH}")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2, cls=MCPEncoder)
    
    logger.info(f"Successfully saved tool lists to {OUTPUT_PATH}")
    logger.info(f"Processed {len(server_results)}/{len(mcp_servers)} servers successfully")

if __name__ == "__main__":
    asyncio.run(main())