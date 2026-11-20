"""Generate a config file per participant.

Participants come from:
  - the command line (-c alice,bob  and/or  -C roster.txt), given the same way
    as to the shell script that prepares the training repository
  - participants_default, which is always added unless --no-defaults is passed

Examples:
    python3 generate_package.py
    python3 generate_package.py -c ivalaginja,pablordrrbl
    python3 generate_package.py -C roster.txt
    cat roster.txt | python3 generate_package.py -C -
"""

import argparse
import configparser
from pathlib import Path
import random
import sys


participants_default = [
    "ivalaginja",
    "pablordrrbl",
]

# Add user000 till nusers as backup
# in case somebody not in the form
nusers = 5
for i in range(nusers):
    username = f"user{i:03d}"
    participants_default.append(username)

animals_list = [
    "cat",
    "dog",
    "goat",
    "leopard",
    "lion",
    "bear",
    "camel",
    "cow",
    "coyote",
    "deer",
    "dolphin",
    "hyena",
    "horse",
    "bull",
    "cock",
    "raven",
]


def split_handles(raw):
    """Split a '-c' value: commas or whitespace, '#' starts a comment."""
    raw = raw.split("#", 1)[0]
    return [handle for handle in raw.replace(",", " ").split() if handle]


def read_handles(path):
    """Read a roster file with one GitHub handle per line; '-' is stdin."""
    if path == "-":
        lines = sys.stdin.read().splitlines()
    else:
        lines = Path(path).read_text().splitlines()

    handles = []
    for line in lines:
        handles.extend(split_handles(line))
    return handles


def collect_participants(args):
    """The handles given on the command line, then the defaults, no repeats."""
    participants = []
    for raw in args.handles:
        participants.extend(split_handles(raw))
    for path in args.files:
        participants.extend(read_handles(path))
    if not args.no_defaults:
        participants.extend(participants_default)

    seen = set()
    unique = []
    for participant in participants:
        if participant not in seen:
            seen.add(participant)
            unique.append(participant)
    return unique


def generate_file(participant, pkg_dir):
    fname = participant + ".ini"
    fpath = pkg_dir / fname

    config = configparser.ConfigParser()
    config.read(fpath)
    section = "pet"
    if not config.has_section(section):
        config.add_section(section)
        k = 3  # Write all
    else:
        k = 2  # Write 2/3

    options = ["animal", "age", "weight"]
    choices = random.sample(options, k=k)
    if "animal" in choices:
        config.set(section, "animal", random.choice(animals_list))
    if "age" in choices:
        config.set(section, "age", str(random.randint(1, 100)))
    if "weight" in choices:
        config.set(section, "weight", "{:.3f}".format(abs(random.gauss(10, 10))))

    with open(fpath, "w") as f:
        config.write(f)


def main():
    parser = argparse.ArgumentParser(
        description="Generate one config file per participant.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-c",
        dest="handles",
        action="append",
        default=[],
        metavar="LIST",
        help="participants, comma or space separated; repeatable",
    )
    parser.add_argument(
        "-C",
        dest="files",
        action="append",
        default=[],
        metavar="FILE",
        help="file with one GitHub handle per line ('-' reads stdin); repeatable",
    )
    parser.add_argument(
        "--no-defaults",
        action="store_true",
        help="use only the handles given, without participants_default",
    )
    parser.add_argument(
        "-o",
        dest="outdir",
        default=None,
        metavar="DIR",
        help="where the .ini files go (default: mypackage beside this script)",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).parent
    pkg_dir = Path(args.outdir) if args.outdir else base_dir / "mypackage"
    pkg_dir.mkdir(parents=True, exist_ok=True)

    participants = collect_participants(args)
    if not participants:
        parser.error("no participants - pass -c or -C, or drop --no-defaults")

    for participant in participants:
        print(participant)
        generate_file(participant, pkg_dir)


if __name__ == "__main__":
    main()
