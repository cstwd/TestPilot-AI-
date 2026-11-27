
"""Declarative catalog authoring helpers."""
from dataclasses import dataclass
from textwrap import indent

MODULES = []
TIERS = {"g": "good", "b": "buggy", "c": "challenge"}


@dataclass(frozen=True)
class E:
    """An expected built-in exception type."""

    type_name: str


def f(signature, doc, body, second_signature, second_doc, second_body):
    """Format two public functions into a standalone source body."""
    functions = [(signature, doc, body), (second_signature, second_doc, second_body)]
    return "\n\n".join(
        f'def {signature}:\n    """{doc}"""\n' + indent(body.rstrip(), "    ")
        for signature, doc, body in functions
    )


def group(domain):
    """Register explicitly authored modules in one business domain."""
    def register(tier, name, source, cases):
        MODULES.append((TIERS[tier], domain, name, source.strip() + "\n", cases))
    return register
