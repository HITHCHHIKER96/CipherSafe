import sys

def main():
    if len(sys.argv) < 2:
        print("Secure File Vault")
        print("Usage:")
        print("  python main.py cli init")
        print("  python main.py cli add <file>")
        print("  python main.py gui")
        return

    mode = sys.argv[1].lower()

    if mode == "cli":
        from vault.cli import main as cli_main
        cli_main()
    elif mode == "gui":
        from vault.gui import main as gui_main
        gui_main()
    else:
        print("Unknown mode. Use cli or gui.")

if __name__ == "__main__":
    main()