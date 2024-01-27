"""
neatplan - nginx-like network configuration
Copyright (C) 2024 c0m4r

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import sys

# https://github.com/nginxinc/crossplane
import crossplane

from .neatplan import Neatplan

__VERSION = "0.3.0"


def read_args() -> argparse.Namespace:
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(
        prog="neatplan",
        description="nginx-style network configuration",
        epilog="https://github.com/c0m4r/neatplan",
    )

    parser.add_argument(
        "-c",
        "--config",
        help="Config file absolute path",
        default="/etc/neatplan/default.conf",
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Show version and exit",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--dry-run",
        help="Don't execute, only show what you've got",
        action="store_true",
        default=False,
    )

    return parser.parse_args()


def main() -> None:
    """
    neatplan main
    """

    print("neatplan by c0m4r", f"v{__VERSION}")

    # Read arguments
    args = read_args()

    if args.version:
        sys.exit(0)
    if args.dry_run:
        print("Running dry-run mode")

    # Initialize Neatplan
    neatplan = Neatplan(args)

    # Read config
    config_json = crossplane.parse(args.config)

    # Check for errors
    neatplan.check_errors(config_json)

    # Set lookpback device up
    neatplan.iface_up("lo")

    # Parse config
    for cfg in config_json["config"][0]["parsed"]:
        if cfg["directive"] == "network":
            neatplan.parse_network_configuration(cfg["block"])


if __name__ == "__main__":
    main()
