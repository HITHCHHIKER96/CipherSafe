# Command-line interface

"""Command-line interface using argparse."""

import argparse
import getpass
import os
from vault import auth, file_manager, db


def create_parser() -> argparse.ArgumentParser:
    """Create CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog='vault',
        description='Secure File Vault CLI - Encrypt and manage sensitive files'
    )
    
    sub = parser.add_subparsers(dest='command', help='Available commands')
    
    # init
    init = sub.add_parser('init', help='Initialize a new vault')
    
    # open (alias for authentication)
    open = sub.add_parser('open', help='Open vault (authenticate)')
    
    # add
    add = sub.add_parser('add', help='Encrypt and add a file to vault')
    add.add_argument('path', help='Path to file to encrypt')
    
    # list
    listp = sub.add_parser('list', help='List all files in vault')
    
    # search
    search = sub.add_parser('search', help='Search files by name')
    search.add_argument('keyword', help='Search keyword')
    
    # extract (decrypt)
    extract = sub.add_parser('extract', help='Decrypt a file from vault')
    extract.add_argument('filename', help='Filename to decrypt')
    extract.add_argument('-o', '--output', help='Output directory (default: current)')
    
    # remove
    remove = sub.add_parser('remove', help='Remove a file from vault')
    remove.add_argument('filename', help='Filename to remove')
    
    # logs
    logs = sub.add_parser('logs', help='Show recent activity logs')
    logs.add_argument('-n', '--limit', type=int, default=20, help='Number of logs to show')
    
    return parser


def main() -> None:
    """CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    # Authenticate for commands that need it
    key = None
    if args.command != 'init':
        try:
            key = auth.open_vault()
        except ValueError as e:
            print(f"\n✗ {e}\n")
            return
    
    # Execute command
    try:
        if args.command == 'init':
            auth.init_vault()
        
        elif args.command == 'add':
            file_id = file_manager.add_file(args.path, key)
            print(f"\n✓ File encrypted and added (ID: {file_id})")
        
        elif args.command == 'list':
            files = file_manager.list_files()
            if not files:
                print("\nVault is empty.")
            else:
                print("\n" + "="*60)
                print("FILES IN VAULT")
                print("="*60)
                for f in files:
                    size_kb = f['filesize'] / 1024 if f['filesize'] else 0
                    print(f"ID: {f['id']}")
                    print(f"  Filename: {f['filename']}")
                    print(f"  Size: {size_kb:.1f} KB")
                    print(f"  Created: {f['created_at']}")
                    print()
                print("="*60)
        
        elif args.command == 'search':
            files = file_manager.search_files(args.keyword)
            if not files:
                print(f"\nNo files found matching '{args.keyword}'")
            else:
                print(f"\nFound {len(files)} file(s):")
                for f in files:
                    print(f"  ID: {f['id']} - {f['filename']}")
        
        elif args.command == 'extract':
            output_dir = args.output if args.output else os.getcwd()
            output_path = file_manager.decrypt_file(args.filename, key, output_dir)
            print(f"\n✓ File decrypted to: {output_path}")
        
        elif args.command == 'remove':
            file_manager.remove_file(args.filename, key)
            print(f"\n✓ File '{args.filename}' removed from vault")
        
        elif args.command == 'logs':
            logs = db.get_logs(args.limit)
            if not logs:
                print("\nNo activity logs.")
            else:
                print("\n" + "="*70)
                print("RECENT ACTIVITY")
                print("="*70)
                for log in logs:
                    print(f"[{log['timestamp']}] {log['action']} (ID: {log['file_id'] or '-'})")
                print("="*70)
    
    except FileNotFoundError as e:
        print(f"\n✗ {e}")
    except ValueError as e:
        print(f"\n✗ {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    main()
