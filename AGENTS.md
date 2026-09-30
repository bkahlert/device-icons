# device-icons

Python 3.13 with uv, standard library only at runtime, macOS only.

## README.md is the specification

A change to the tool's commands, options, output layout, or terms updates [README.md](README.md) in the same change.
When README and code disagree, the README is the spec: fix the code, unless the change was intended, then fix the
README.

## One vocabulary, Apple's

The [Glossary](README.md#glossary) is the only source of terms. Code, JSON keys, file names, command-line options,
tests, and commit messages use the glossary term or its documented short form, as snake_case where the language wants
it: `model_identifier`, not `code` or `model`; `type_identifier` or `type`, not `uti`; `sidebar_icon` or `sidebar` for
the icon Finder's sidebar draws, and `template` only for how an image is rendered, never for that icon. A concept gets
its glossary entry before it gets a name in code.

Why: Apple's own names overlap (`model`, `code`, `identifier`, `type`), so a bare one is ambiguous.
