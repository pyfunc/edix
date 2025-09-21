"""
CLI entry point for Edix
"""
import argparse
import sys
import asyncio
from pathlib import Path
from .app import run_server


def main():
    parser = argparse.ArgumentParser(description="Edix - Universal Data Structure Editor")
    parser.add_argument(
        "command",
        choices=["serve", "init", "migrate", "export", "import"],
        help="Command to execute"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--db", default="edix.db", help="Database file")
    parser.add_argument("--format", choices=["json", "yaml", "csv", "xml"], help="Export format")
    parser.add_argument("--file", help="Import/export file")
    parser.add_argument("--structure", help="Structure name")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        print(f"🚀 Starting Edix server on http://{args.host}:{args.port}")
        print(f"📁 Database: {args.db}")
        print("\nPress Ctrl+C to stop\n")
        run_server(host=args.host, port=args.port, reload=args.reload)
        
    elif args.command == "init":
        from .database import DatabaseManager
        
        async def init_db():
            db = DatabaseManager(args.db)
            await db.initialize()
            print(f"✅ Database initialized: {args.db}")
            await db.close()
        
        asyncio.run(init_db())
        
    elif args.command == "export":
        if not args.format or not args.file:
            print("Error: --format and --file are required for export")
            sys.exit(1)
            
        # Export logic here
        print(f"Exporting to {args.file} in {args.format} format...")
        
    elif args.command == "import":
        if not args.format or not args.file:
            print("Error: --format and --file are required for import")
            sys.exit(1)
            
        # Import logic here
        print(f"Importing from {args.file} ({args.format} format)...")
    
    elif args.command == "migrate":
        print("Running database migrations...")
        # Migration logic here


if __name__ == "__main__":
    main()
