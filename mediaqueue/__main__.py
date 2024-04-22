import argparse
import json
import sys
from .catalog import connect, items, scan, duplicates, mark
from .inspect import inspect_file
from .organize import plan, apply


def main():
    parser = argparse.ArgumentParser(description='Inspect a local media queue')
    parser.add_argument('--db', default='media.sqlite3')
    commands = parser.add_subparsers(dest='command', required=True)
    scan_parser = commands.add_parser('scan')
    scan_parser.add_argument('directory')
    list_parser = commands.add_parser('list')
    list_parser.add_argument('--status', choices=['new', 'reviewed', 'skipped'])
    inspect_parser = commands.add_parser('inspect')
    inspect_parser.add_argument('path')
    commands.add_parser('duplicates')
    mark_parser = commands.add_parser('mark')
    mark_parser.add_argument('id', type=int)
    mark_parser.add_argument('status', choices=['new', 'reviewed', 'skipped'])
    mark_parser.add_argument('--tag', default='')
    organize_parser = commands.add_parser('organize')
    organize_parser.add_argument('destination')
    organize_parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        with connect(args.db) as db:
            if args.command == 'scan':
                result = {'scanned': scan(db, args.directory)}
            elif args.command == 'inspect':
                result = inspect_file(args.path)
            elif args.command == 'duplicates':
                result = duplicates(db)
            elif args.command == 'organize':
                result = plan(items(db), args.destination)
                if args.apply:
                    result = {'copied': apply(result)}
            elif args.command == 'mark':
                mark(db, args.id, args.status, args.tag)
                result = {'updated': args.id}
            else:
                result = items(db, args.status)
        print(json.dumps(result, indent=2))
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
