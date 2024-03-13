import argparse
import json
import sys
from .catalog import connect, items, scan


def main():
    parser = argparse.ArgumentParser(description='Inspect a local media queue')
    parser.add_argument('--db', default='media.sqlite3')
    commands = parser.add_subparsers(dest='command', required=True)
    scan_parser = commands.add_parser('scan')
    scan_parser.add_argument('directory')
    list_parser = commands.add_parser('list')
    list_parser.add_argument('--status', choices=['new', 'reviewed', 'skipped'])
    args = parser.parse_args()
    try:
        with connect(args.db) as db:
            if args.command == 'scan':
                result = {'scanned': scan(db, args.directory)}
            else:
                result = items(db, args.status)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
