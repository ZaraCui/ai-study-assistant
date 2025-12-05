#!/usr/bin/env python3
"""Simple CLI to manage the FAISS index for the study assistant.

Commands:
  build   - build (or rebuild) index from notes folder
  load    - attempt to load an existing index and print stats
  status  - check whether index files exist

Examples:
  python scripts/manage_index.py build --notes data/notes/COMP2123
  python scripts/manage_index.py load
  python scripts/manage_index.py build --force
"""
import argparse
import os
import sys

from rag.qa import build_knowledge_base_from_dir, DEFAULT_INDEX_PATH
from rag.vectorstore import VectorStore


def remove_index_files(path_prefix: str):
    files = [f"{path_prefix}.index", f"{path_prefix}_texts.pkl"]
    removed = []
    for f in files:
        if os.path.exists(f):
            os.remove(f)
            removed.append(f)
    return removed


def cmd_build(args):
    notes = args.notes
    index_path = args.index_path
    if args.force:
        removed = remove_index_files(index_path)
        if removed:
            print("Removed existing files:", ", ".join(removed))

    print(f"Building index from: {notes} -> {index_path} ...")
    try:
        build_knowledge_base_from_dir(notes, index_path)
        print("Build completed. Index saved at:", index_path)
    except Exception as e:
        print("Build failed:", e)
        sys.exit(2)


def cmd_load(args):
    index_path = args.index_path
    try:
        vs = VectorStore.load(index_path)
        # try a small sanity check
        try:
            ntotal = int(vs.index.ntotal)
        except Exception:
            ntotal = None
        print(f"Loaded index from {index_path}")
        print(f"  texts: {len(vs.texts)}")
        print(f"  vectors (ntotal): {ntotal}")
    except FileNotFoundError:
        print("No index files found at:", index_path)
        sys.exit(1)
    except Exception as e:
        print("Failed to load index:", e)
        sys.exit(2)


def cmd_status(args):
    index_path = args.index_path
    files = [f"{index_path}.index", f"{index_path}_texts.pkl"]
    for f in files:
        print(f, "->", "exists" if os.path.exists(f) else "missing")


def build_parser():
    p = argparse.ArgumentParser(description="Manage FAISS index for AI Study Assistant")
    sub = p.add_subparsers(dest="cmd")

    b = sub.add_parser("build", help="Build or rebuild the index from notes folder")
    b.add_argument("--notes", default="data/notes/COMP2123", help="Folder with notes")
    b.add_argument("--index-path", default=DEFAULT_INDEX_PATH, help="Path prefix for index files")
    b.add_argument("--force", action="store_true", help="Remove existing index files before building")
    b.set_defaults(func=cmd_build)

    l = sub.add_parser("load", help="Attempt to load existing index and print stats")
    l.add_argument("--index-path", default=DEFAULT_INDEX_PATH, help="Path prefix for index files")
    l.set_defaults(func=cmd_load)

    s = sub.add_parser("status", help="Check if index files exist")
    s.add_argument("--index-path", default=DEFAULT_INDEX_PATH, help="Path prefix for index files")
    s.set_defaults(func=cmd_status)

    return p


def main():
    p = build_parser()
    args = p.parse_args()
    if not args.cmd:
        p.print_help()
        return
    args.func(args)


if __name__ == "__main__":
    main()
