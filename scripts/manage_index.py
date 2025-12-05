#!/usr/bin/env python3
"""CLI to manage FAISS indexes for multiple courses.

Commands:
  build   - build (or rebuild) index for a course from notes folder
  load    - attempt to load an existing index and print stats
  status  - check whether index files exist
  list    - list all available courses

Examples:
  python scripts/manage_index.py build --course COMP2123
  python scripts/manage_index.py build --course CS101 --notes data/notes/CS101
  python scripts/manage_index.py load --course COMP2123
  python scripts/manage_index.py list
  python scripts/manage_index.py status --course COMP2123
"""
import argparse
import os
import sys

from rag.qa import build_knowledge_base_from_dir
from rag.course_manager import (
    get_course_notes_path,
    get_course_index_path,
    is_course_indexed,
    list_available_courses,
    get_course_info,
    DEFAULT_COURSE,
)
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
    course_code = args.course or DEFAULT_COURSE
    notes = args.notes or get_course_notes_path(course_code)
    index_path = args.index_path or get_course_index_path(course_code)
    
    if not os.path.exists(notes):
        print(f"Error: Notes folder not found: {notes}")
        sys.exit(1)
    
    if args.force:
        removed = remove_index_files(index_path)
        if removed:
            print("Removed existing files:", ", ".join(removed))

    print(f"Building index for course: {course_code}")
    print(f"  Notes folder: {notes}")
    print(f"  Index path: {index_path}")
    
    try:
        build_knowledge_base_from_dir(notes, index_path, course_code)
        print(f"✓ Build completed. Index saved at: {index_path}")
    except Exception as e:
        print(f"✗ Build failed: {e}")
        sys.exit(2)


def cmd_load(args):
    course_code = args.course or DEFAULT_COURSE
    index_path = args.index_path or get_course_index_path(course_code)
    
    try:
        vs = VectorStore.load(index_path)
        try:
            ntotal = int(vs.index.ntotal)
        except Exception:
            ntotal = None
        print(f"✓ Loaded index for course: {course_code}")
        print(f"  Path: {index_path}")
        print(f"  Chunks: {len(vs.texts)}")
        print(f"  Vectors (ntotal): {ntotal}")
    except FileNotFoundError:
        print(f"✗ No index found for course {course_code}")
        print(f"  Expected path: {index_path}")
        print(f"  Run: python scripts/manage_index.py build --course {course_code}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Failed to load index: {e}")
        sys.exit(2)


def cmd_status(args):
    course_code = args.course or DEFAULT_COURSE
    index_path = args.index_path or get_course_index_path(course_code)
    
    info = get_course_info(course_code)
    print(f"Course: {course_code}")
    print(f"  Indexed: {'Yes' if info['indexed'] else 'No'}")
    print(f"  Loaded: {'Yes' if info['loaded'] else 'No'}")
    if info['loaded']:
        print(f"  Chunks: {info['chunk_count']}")
    print(f"  Notes exist: {'Yes' if info['notes_exist'] else 'No'}")
    if info['notes_exist']:
        print(f"  Notes path: {info['notes_path']}")


def cmd_list(args):
    courses = list_available_courses()
    print(f"Available courses ({len(courses)}):")
    if not courses:
        print("  (no courses found in data/notes/)")
    else:
        for course in courses:
            indexed = "✓" if is_course_indexed(course) else " "
            default = " (default)" if course == DEFAULT_COURSE else ""
            print(f"  [{indexed}] {course}{default}")


def build_parser():
    p = argparse.ArgumentParser(description="Manage FAISS indexes for AI Study Assistant")
    sub = p.add_subparsers(dest="cmd")

    b = sub.add_parser("build", help="Build or rebuild the index from notes folder")
    b.add_argument("--course", default=None, help=f"Course code (default: {DEFAULT_COURSE})")
    b.add_argument("--notes", default=None, help="Folder with notes (default: data/notes/<course>)")
    b.add_argument("--index-path", default=None, help="Path prefix for index files (default: data/index/<course>)")
    b.add_argument("--force", action="store_true", help="Remove existing index files before building")
    b.set_defaults(func=cmd_build)

    l = sub.add_parser("load", help="Attempt to load existing index and print stats")
    l.add_argument("--course", default=None, help=f"Course code (default: {DEFAULT_COURSE})")
    l.add_argument("--index-path", default=None, help="Path prefix for index files")
    l.set_defaults(func=cmd_load)

    s = sub.add_parser("status", help="Check if index files exist")
    s.add_argument("--course", default=None, help=f"Course code (default: {DEFAULT_COURSE})")
    s.add_argument("--index-path", default=None, help="Path prefix for index files")
    s.set_defaults(func=cmd_status)

    ls = sub.add_parser("list", help="List all available courses")
    ls.set_defaults(func=cmd_list)

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
