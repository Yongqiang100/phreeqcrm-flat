#!/usr/bin/env python3
"""Import an official PhreeqcRM release into the flat layout (phreeqcrm-flat, task F1).

Usage:
  sync_upstream.py --upstream <PhreeqcRM git checkout at a release tag> --dest <flat worktree> [--dry-run]

Every file tracked by git in the upstream checkout is mapped by the ordered RULES below (first match
wins) to a destination path in the flat layout, or dropped with a stated reason. The script FAILS
(exit 2) and writes nothing if
  * any tracked upstream file matches no rule, or
  * two upstream files map to the same destination.

On success it copies the mapped files and writes, in --dest:
  UPSTREAM_VERSION        tag (git describe) and commit of the imported release
  UPSTREAM_MANIFEST.tsv   destination, upstream path, sha256 for every imported file
  UPSTREAM_DROPPED.tsv    upstream path and reason for every dropped file
Files listed in a previous UPSTREAM_MANIFEST.tsv but absent from the new import are deleted, so a
re-import of a newer release removes files upstream removed. Files never listed in the manifest
(our own work on other branches) are never touched.

Running it twice on the same release is a no-op (same manifest, no file changes).
"""
import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys

# (regex on the upstream path, destination template or None to drop, reason). Order matters.
ENGINE = r"src/IPhreeqcPhast/IPhreeqc/phreeqcpp/"
IPHREEQC = r"src/IPhreeqcPhast/IPhreeqc/"
RULES = [
    # --- dropped: CI, VCS metadata, editor files, non-CMake build systems -----------------------
    (r"(.*/)?\.github/.*", None, "CI configuration (GitHub), incl. subtree CI of the layers"),
    (r"(.*/)?\.gitlab-ci\.yml", None, "CI configuration (GitLab)"),
    (r"(.*/)?\.git(ignore|attributes|modules)", None, "VCS metadata"),
    (r"\.vscode/.*", None, "editor settings"),
    (r"\.pre-commit-config\.yaml", None, "developer tooling (pre-commit)"),
    (r"(.*/)?Makefile\.am", None, "autotools"),
    (r"configure\.ac|bootstrap|m4/.*|phreeqcrm\.pc\.in", None, "autotools"),
    (r"jenkins-.*", None, "CI (Jenkins)"),
    (r"setup-fortran/.*", None, "CI helper (GitHub action for Fortran)"),
    (r"(.*/)?vs20\d\d/.*|.*\.(sln|vcxproj|vcxproj\.filters|vcproj|vsprops|props)", None, "Visual Studio"),
    # --- PHREEQC engine (layer 1) --------------------------------------------------------------
    (ENGINE + r"common/(.+)", r"src/phreeqc_common/\1", ""),
    (ENGINE + r"PhreeqcKeywords/(.+)", r"src/phreeqc/keywords/\1", ""),
    (ENGINE + r"class_main\.cpp", r"src/phreeqc/app/class_main.cpp", "standalone phreeqc main(); not compiled into PhreeqcRM"),
    (ENGINE + r"(.+)", r"src/phreeqc/\1", ""),
    # --- IPhreeqc (layer 2) and IPhreeqcPhast (layer 3) ---------------------------------------
    (IPHREEQC + r"(.+)", r"src/iphreeqc/\1", ""),
    (r"src/IPhreeqcPhast/([^/]+)", r"src/iphreeqcphast/\1", ""),
    # --- PhreeqcRM (layer 4) and its language interfaces ---------------------------------------
    (r"src/((RM|BMI|YAML)_interface_C\.(cpp|h))", r"src/interfaces/c/\1", ""),
    (r"src/(.+_F\.(cpp|h)|.+\.F90|.+\.f90|BMI_not_implemented\.inc)", r"src/interfaces/fortran/\1", ""),
    (r"src/phreeqcrm/__init__\.py", r"python/phreeqcrm/__init__.py", ""),
    (r"src/([^/]+)", r"src/phreeqcrm/\1", ""),
    # --- Python, tests, data, docs ---------------------------------------------------------------
    (r"swig/(.+)", r"python/swig/\1", ""),
    (r"(pyproject\.toml|uv\.lock|environment\.yml|mamba\.environment\.yml)", r"python/\1", ""),
    (r"Tests/(.+)", r"tests/\1", ""),
    (r"database/(.+)", r"database/\1", ""),
    (r"Doxygen/(.+)", r"docs/doxygen/\1", ""),
    (r"doc/(.+)", r"docs/upstream/doc/\1", ""),
    (r"(README\.md|DEVELOPER\.md)", r"docs/upstream/\1", ""),
    (r"LICENSE", r"LICENSE", ""),
    # --- upstream build files: kept for reference (the flat build is new, task F2) ----------------
    (r"(irm_dll_export\.h\.in|PhreeqcRMConfig\.cmake\.in|phreeqcrm\.cmake\.in)", r"cmake/templates/\1", "configure templates used by the flat build"),
    (r"(CMakeLists\.txt|CMakePresets\.json|CTestConfig\.cmake|cmemcheck.*\.cmake|build-all-presets\.sh)", r"cmake/upstream/\1", "upstream build file, reference copy"),
]
COMPILED = [(re.compile(r"^(?:" + pattern + r")$"), destination, reason) for pattern, destination, reason in RULES]


def git(upstream, *arguments):
    return subprocess.run(["git", "-C", upstream, *arguments], check=True, capture_output=True,
                          text=True).stdout


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def plan(files):
    mapped, dropped, unmatched, owner = [], [], [], {}
    for path in files:
        for pattern, destination, reason in COMPILED:
            match = pattern.match(path)
            if match:
                if destination is None:
                    dropped.append((path, reason))
                else:
                    target = match.expand(destination)
                    if target in owner:
                        raise SystemExit(f"ERROR: {path} and {owner[target]} both map to {target}")
                    owner[target] = path
                    mapped.append((target, path))
                break
        else:
            unmatched.append(path)
    return mapped, dropped, unmatched


def read_manifest(dest):
    path = os.path.join(dest, "UPSTREAM_MANIFEST.tsv")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        rows = [line.rstrip("\n").split("\t") for line in handle if line.strip() and not line.startswith("#")]
    return {row[0]: row for row in rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--dest", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = git(args.upstream, "ls-files", "-z").split("\0")
    files = [f for f in files if f]
    describe = git(args.upstream, "describe", "--tags", "--always").strip()
    commit = git(args.upstream, "rev-parse", "HEAD").strip()
    mapped, dropped, unmatched = plan(files)
    if unmatched:
        print("ERROR: upstream files that match no rule (nothing was written):", file=sys.stderr)
        for path in unmatched:
            print("  " + path, file=sys.stderr)
        return 2

    previous = read_manifest(args.dest)
    new_targets = {target for target, _ in mapped}
    removed = sorted(t for t in previous if t not in new_targets)
    changed = added = 0
    for target, source in mapped:
        source_path = os.path.join(args.upstream, source)
        target_path = os.path.join(args.dest, target)
        if not os.path.exists(target_path):
            added += 1
        elif sha256(target_path) != sha256(source_path):
            changed += 1
    print(f"upstream {describe} ({commit}): {len(files)} tracked files -> {len(mapped)} imported, "
          f"{len(dropped)} dropped; vs previous import: {added} added, {changed} changed, {len(removed)} removed")
    counts = {}
    for target, _ in mapped:
        top = "/".join(target.split("/")[:2]) if target.startswith(("src/", "cmake/", "docs/", "python/")) else target.split("/")[0]
        counts[top] = counts.get(top, 0) + 1
    for top in sorted(counts):
        print(f"  {counts[top]:5d}  {top}")
    reasons = {}
    for _, reason in dropped:
        reasons[reason] = reasons.get(reason, 0) + 1
    for reason in sorted(reasons):
        print(f"  dropped {reasons[reason]:4d}  {reason}")
    if args.dry_run:
        return 0

    for target in removed:
        target_path = os.path.join(args.dest, target)
        if os.path.exists(target_path):
            os.remove(target_path)
    for target, source in mapped:
        target_path = os.path.join(args.dest, target)
        os.makedirs(os.path.dirname(target_path) or ".", exist_ok=True)
        shutil.copy2(os.path.join(args.upstream, source), target_path)
    with open(os.path.join(args.dest, "UPSTREAM_VERSION"), "w", encoding="utf-8") as handle:
        handle.write(f"PhreeqcRM {describe}\ncommit {commit}\n")
    with open(os.path.join(args.dest, "UPSTREAM_MANIFEST.tsv"), "w", encoding="utf-8") as handle:
        handle.write("# destination\tupstream_path\tsha256\n")
        for target, source in sorted(mapped):
            handle.write(f"{target}\t{source}\t{sha256(os.path.join(args.dest, target))}\n")
    with open(os.path.join(args.dest, "UPSTREAM_DROPPED.tsv"), "w", encoding="utf-8") as handle:
        handle.write("# upstream_path\treason\n")
        for path, reason in sorted(dropped):
            handle.write(f"{path}\t{reason}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
