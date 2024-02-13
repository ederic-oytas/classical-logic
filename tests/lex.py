"""Script which lexes text and prints the tokens. Used for debugging purposes.
"""

import sys

from classical_logic.parsing import _lex as lex


def main() -> None:
    """Main entry point function."""

    if len(sys.argv) == 1:
        print()
        print(f"Usage: {sys.argv[0]} TEXT")
        print("    Prints out the tokens lexed by `prop()`")
        print()
        return

    text = sys.argv[1]

    tokens = lex(text)
    for token in tokens:
        print(token)


if __name__ == "__main__":
    main()
