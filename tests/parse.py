"""Script which parses text and prints the object. Used for debugging purposes.
"""

import sys

from classical_logic.parsing import prop


def main() -> None:
    """Main entry point function."""

    if len(sys.argv) == 1:
        print()
        print(f"Usage: {sys.argv[0]} TEXT")
        print("    Prints out the object parsed by `prop()`")
        print()
        return

    text = sys.argv[1]

    p = prop(text)
    print(f"{repr(p) = }")
    print(f"{str(p)  = }")


if __name__ == "__main__":
    main()
