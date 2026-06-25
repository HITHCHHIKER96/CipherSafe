import argparse
from vault import auth, file_manager, db

def main():
    parser = argparse.ArgumentParser(prog="vault")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init")
    addp = sub.add_parser("add")
    addp.add_argument("path")

    sub.add_parser("list")
    searchp = sub.add_parser("search")
    searchp.add_argument("keyword")

    decr = sub.add_parser("extract")
    decr.add_argument("filename")
    decr.add_argument("-o", "--output", default=".")

    rm = sub.add_parser("remove")
    rm.add_argument("filename")

    sub.add_parser("logs")

    args = parser.parse_args()

    if args.cmd == "init":
        auth.init_vault()

    elif args.cmd == "add":
        key = auth.open_vault()
        file_manager.add_file(args.path, key)
        print("File added successfully.")

    elif args.cmd == "list":
        rows = file_manager.list_files()
        if not rows:
            print("No files found.")
        for r in rows:
            print(r["id"], r["filename"], r["created_at"])

    elif args.cmd == "search":
        rows = file_manager.search_files(args.keyword)
        for r in rows:
            print(r["id"], r["filename"])

    elif args.cmd == "extract":
        key = auth.open_vault()
        out = file_manager.decrypt_file(args.filename, key, args.output)
        print(f"Decrypted to: {out}")

    elif args.cmd == "remove":
        file_manager.remove_file(args.filename)
        print("File removed.")

    elif args.cmd == "logs":
        rows = db.get_logs()
        for r in rows:
            print(r["id"], r["action"], r["filename"], r["timestamp"])

    else:
        parser.print_help()

if __name__ == "__main__":
    main()