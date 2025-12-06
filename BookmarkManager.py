
import argparse
import json
import os
import sys
from pathlib import Path
from bookmark_storage import BookmarkStorage
from rich.console import Console
from rich.table import Table

def print_header(console, config):
    console.clear()
    for line in config['header']:
        console.print(f"[cyan]{line}[/cyan]")

def main():
    script_dir = Path(__file__).parent
    config_path = script_dir / 'config.json'

    with open(config_path, 'r') as f:
        config = json.load(f)
    
    console = Console()
    storage = BookmarkStorage()

    print_header(console, config)

    parser = argparse.ArgumentParser(description="NAVI (Networked Administrative Visual Interface)", add_help=False)
    subparsers = parser.add_subparsers(dest="command", help="Available commands.")

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Fabricate a new connection.", add_help=False)
    add_parser.add_argument("url", help="The destination URI.")
    add_parser.add_argument("--title", "-t", help="A descriptor for the link.")
    add_parser.add_argument("--topic", "-c", default="general", help="The classification layer.")
    add_parser.add_argument("--tags", "-g", nargs='+', help="Additional tags for the bookmark.")
    add_parser.add_argument("--related", "-r", nargs='+', type=int, help="Link to existing connections by ID.")

    # 'search' command
    search_parser = subparsers.add_parser("search", help="Traverse the layers for a pattern.", add_help=False)
    search_parser.add_argument("query", help="The pattern to find.")
    search_parser.add_argument("--in-title", action="store_true", help="Search in title.")
    search_parser.add_argument("--in-url", action="store_true", help="Search in URL.")
    search_parser.add_argument("--in-topic", action="store_true", help="Search in topic.")
    search_parser.add_argument("--in-tags", action="store_true", help="Search in tags.")

    # 'list' command
    list_parser = subparsers.add_parser("list", help="Reveal all established connections.", add_help=False)
    list_parser.add_argument("topic", nargs='?', default=None, help="Filter connections by classification.")

    # 'topics' command
    subparsers.add_parser("topics", help="List all classification layers.", add_help=False)

    # 'delete' command
    delete_parser = subparsers.add_parser("delete", help="Sever a connection.", add_help=False)
    delete_parser.add_argument("id", type=int, help="The identifier of the connection to sever.")

    # 'edit' command
    edit_parser = subparsers.add_parser("edit", help="Modify an existing connection.", add_help=False)
    edit_parser.add_argument("id", type=int, help="The identifier of the connection to modify.")
    edit_parser.add_argument("--url", help="The new destination URI.")
    edit_parser.add_argument("--title", help="The new descriptor.")
    edit_parser.add_argument("--topic", help="The new classification layer.")
    edit_parser.add_argument("--tags", nargs='+', help="The new tags.")

    # 'relate' command
    relate_parser = subparsers.add_parser("relate", help="Create a relationship between two connections.", add_help=False)
    relate_parser.add_argument("id1", type=int, help="The first connection ID.")
    relate_parser.add_argument("id2", type=int, help="The second connection ID.")

    # 'backup' command
    subparsers.add_parser("backup", help="Create a data shadow.", add_help=False)

    # 'erase-all' command
    subparsers.add_parser("erase-all", help="Delete all bookmarks.", add_help=False)

    # 'find-duplicates' command
    subparsers.add_parser("find-duplicates", help="Find duplicate bookmarks.", add_help=False)

    # 'export' command
    export_parser = subparsers.add_parser("export", help="Translate data to a different protocol.", add_help=False)
    export_parser.add_argument("format", choices=["csv", "html"], help="The target protocol.")
    export_parser.add_argument("filename", help="The name for the translated data.")
    
    # 'help' command
    subparsers.add_parser("help", help="Display this help message.", add_help=False)

    # 'exit' command
    subparsers.add_parser("exit", help="Close the connection to the Wired.", add_help=False)
    
    # 'clear' command
    subparsers.add_parser("clear", help="Refresh the NAVI interface.", add_help=False)

    while True:
        try:
            num_bookmarks = len(storage.list_bookmarks())
            prompt = f"[dim][{num_bookmarks} connections][/dim] > "
            
            user_input = console.input(prompt)
            if not user_input:
                continue

            input_parts = user_input.split()
            command = input_parts[0]
            args_list = input_parts[1:]

            if command == "exit":
                console.print("[bold red]Closing connection to the Wired.[/bold red]")
                break
            
            if command == "clear":
                print_header(console, config)
                continue

            if command == "add":
                url = None
                title = None
                topic = "general"
                tags = []
                related = []

                if args_list:
                    url = args_list[0]
                    args_list = args_list[1:]

                title_words = []
                
                i = 0
                while i < len(args_list):
                    if args_list[i] == "--title" or args_list[i] == "-t":
                        i += 1
                        while i < len(args_list) and not args_list[i].startswith("--"):
                            title_words.append(args_list[i])
                            i += 1
                        continue
                    elif args_list[i] == "--topic" or args_list[i] == "-c":
                        i += 1
                        if i < len(args_list):
                            topic = args_list[i]
                            i += 1
                        continue
                    elif args_list[i] == "--tags" or args_list[i] == "-g":
                        i += 1
                        while i < len(args_list) and not args_list[i].startswith("--"):
                            tags.append(args_list[i])
                            i += 1
                        continue
                    elif args_list[i] == "--related" or args_list[i] == "-r":
                        i += 1
                        while i < len(args_list) and not args_list[i].startswith("--"):
                            related.append(int(args_list[i]))
                            i += 1
                        continue
                    i += 1

                if title_words:
                    title = " ".join(title_words)

                if url:
                    bookmark_id = storage.add_bookmark(url, title, topic, related, tags)
                    console.print(f"[green]Connection established. Record created with ID: {bookmark_id}[/green]")
                else:
                    console.print("[yellow]URL is required for the add command.[/yellow]")
                continue

            try:
                args = parser.parse_args([command] + args_list)
            except SystemExit:
                continue
            
            if args.command == "search":
                results = storage.search_bookmarks(args.query, args.in_title, args.in_url, args.in_topic, args.in_tags)
                if results:
                    table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
                    table.add_column("ID", style="dim", width=6)
                    table.add_column("Title")
                    table.add_column("URL", style="cyan")
                    table.add_column("Topic", style="green")
                    table.add_column("Manual Tags", style="blue")
                    table.add_column("Auto Tags", style="bright_blue")
                    table.add_column("Related", style="yellow")
                    for r in results:
                        related_str = ', '.join(map(str, r.get('related_bookmarks', [])))
                        tags = r.get('tags', {})
                        if isinstance(tags, dict):
                            manual_tags_str = ', '.join(tags.get('manual', []))
                            auto_tags_str = ', '.join(tags.get('auto', []))
                        else:
                            manual_tags_str = ', '.join(tags)
                            auto_tags_str = ""
                        table.add_row(str(r['id']), r['title'], r['url'], r.get('topic', 'N/A'), manual_tags_str, auto_tags_str, related_str)
                    console.print(table)
                else:
                    console.print("[yellow]No signal found.[/yellow]")
            elif args.command == "list":
                bookmarks = storage.list_bookmarks(args.topic)
                if bookmarks:
                    table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
                    table.add_column("ID", style="dim", width=6)
                    table.add_column("Title")
                    table.add_column("URL", style="cyan")
                    if not args.topic:
                        table.add_column("Topic", style="green")
                    table.add_column("Manual Tags", style="blue")
                    table.add_column("Auto Tags", style="bright_blue")
                    table.add_column("Related", style="yellow")
                    for b in bookmarks:
                        related_str = ', '.join(map(str, b.get('related_bookmarks', [])))
                        tags = b.get('tags', {})
                        if isinstance(tags, dict):
                            manual_tags_str = ', '.join(tags.get('manual', []))
                            auto_tags_str = ', '.join(tags.get('auto', []))
                        else:
                            manual_tags_str = ', '.join(tags)
                            auto_tags_str = ""
                        if args.topic:
                            table.add_row(str(b['id']), b['title'], b['url'], manual_tags_str, auto_tags_str, related_str)
                        else:
                            table.add_row(str(b['id']), b['title'], b['url'], b.get('topic', 'N/A'), manual_tags_str, auto_tags_str, related_str)
                    console.print(table)
                else:
                    console.print("[yellow]The Wired is silent.[/yellow]")
            elif args.command == "topics":
                topics = storage.list_topics()
                if topics:
                    table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
                    table.add_column("Classification Layer")
                    for t in topics:
                        table.add_row(t)
                    console.print(table)
                else:
                    console.print("[yellow]No classification layers found.[/yellow]")
            elif args.command == "delete":
                if storage.delete_bookmark(args.id):
                    console.print(f"[red]Connection with ID {args.id} severed.[/red]")
                else:
                    console.print(f"[yellow]Signal lost. Connection with ID {args.id} not found.[/yellow]")
            elif args.command == "edit":
                if storage.edit_bookmark(args.id, args.url, args.title, args.topic, new_tags=args.tags):
                    console.print(f"[green]Connection with ID {args.id} re-routed.[/green]")
                else:
                    console.print(f"[yellow]Signal lost. Connection with ID {args.id} not found.[/yellow]")
            elif args.command == "relate":
                if storage.relate_bookmarks(args.id1, args.id2):
                    console.print(f"[green]Relationship between {args.id1} and {args.id2} established.[/green]")
                else:
                    console.print(f"[yellow]Could not establish relationship. One or both IDs not found.[/yellow]")
            elif args.command == "backup":
                backup_file = storage.backup_bookmarks()
                console.print(f"[green]Data shadow created at: {backup_file}[/green]")
            elif args.command == "erase-all":
                console.print("[bold red]This will delete all your bookmarks. Are you sure? (y/n)[/bold red]")
                confirmation = console.input("> ")
                if confirmation.lower() == 'y':
                    storage.delete_all_bookmarks()
                    console.print("[green]All bookmarks have been deleted.[/green]")
                else:
                    console.print("[yellow]Operation cancelled.[/yellow]")
            elif args.command == "find-duplicates":
                duplicates = storage.find_duplicate_bookmarks()
                if duplicates:
                    table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
                    table.add_column("Duplicate IDs")
                    for d in duplicates:
                        table.add_row(', '.join(map(str, d)))
                    console.print(table)
                else:
                    console.print("[green]No duplicate bookmarks found.[/green]")
            elif args.command == "export":
                if storage.export_bookmarks(args.format, args.filename):
                    console.print(f"[green]Data translated to {args.format} and stored at {args.filename}[/green]")
                else:
                    console.print("[red]Translation failed.[/red]")
            elif args.command == "help":
                console.print("\n[bold cyan]NAVI (Networked Administrative Visual Interface)[/bold cyan]\n")
                console.print("A gateway to the Wired. All information is a connection.\n")
                
                table = Table(show_header=True, header_style="bold magenta", border_style="cyan", show_lines=True)
                table.add_column("Command", style="dim", width=12)
                table.add_column("Description")

                table.add_row("add", "Fabricate a new connection. Use --related to link to other connections by ID.")
                table.add_row("search", "Traverse the layers for a pattern. Use --in-title, --in-url, or --in-topic to specify scope.")
                table.add_row("list", "Reveal all established connections, or list connections in a specific topic.")
                table.add_row("topics", "List all classification layers.")
                table.add_row("delete", "Sever a connection.")
                table.add_row("edit", "Modify an existing connection.")
                table.add_row("relate", "Create a relationship between two connections.")
                table.add_row("backup", "Create a data shadow.")
                table.add_row("export", "Translate data to a different protocol.")
                table.add_row("help", "Display this help message.")
                table.add_row("clear", "Refresh the NAVI interface.")
                table.ad_row("exit", "Close the connection to the Wired.")
                
                console.print(table)

        except Exception as e:
            console.print(f"[bold red]System Error:[/bold red] Anomaly detected in the NAVI system.")
            console.print(f"[red]Error details: {e}[/red]")
            console.print(f"[yellow]Re-calibrating the connection... please try again.[/yellow]")

if __name__ == "__main__":
    main()
