# phreeqcrm-flat: PhreeqcRM v3.9.0 in a Flat, Layered Layout

The same source code as the official PhreeqcRM v3.9.0 (`https://github.com/usgs-coupled/phreeqcrm`), with the same behaviour and the same installed library, **rearranged so that each software layer is one directory**. No source file is edited; every file's origin is listed in `UPSTREAM_MANIFEST.tsv`.

## Where Is What

```text
src/
├── phreeqc_common/   shared I/O, parser and number type (PHRQ_io, Parser, phrqtype.h)        layer 0
├── phreeqc/          the PHREEQC chemistry engine (Phreeqc.h, model.cpp, cl1.cpp, ...)          layer 1
│   ├── keywords/     PHREEQC keyword table
│   └── app/          class_main.cpp, the standalone phreeqc main() (not part of the library)
├── iphreeqc/         IPhreeqc: run PHREEQC input strings and read results from C, C++, Fortran  layer 2
├── iphreeqcphast/    IPhreeqcPhast: per-cell extensions used by reactive transport            layer 3
├── phreeqcrm/        PhreeqcRM C++ API: PhreeqcRM, BMIPhreeqcRM, YAMLPhreeqcRM, VarManager     layer 4
└── interfaces/
    ├── c/            C API (RM_interface_C, BMI_interface_C, YAML_interface_C)
    └── fortran/      Fortran API (*.F90 modules and their *_F.cpp glue)
tests/                PhreeqcRM's own test programs and inputs (TestRM, TestRMdtor, ...)
database/             thermodynamic databases (phreeqc.dat, llnl.dat, pitzer.dat, ...)
python/               Python bindings (SWIG) and packaging
docs/                 Doxygen configuration, upstream documentation
cmake/                build templates; cmake/upstream/ keeps upstream build files for reference
tools/                sync_upstream.py: imports a new official release into this layout
```

**Each layer depends only on the layers above it in the list.** To understand the code, read from the top down:
1. `src/phreeqc/Phreeqc.h` and `src/phreeqc/model.cpp`: one chemistry calculation;
2. `src/iphreeqc/IPhreeqc.hpp`: driving PHREEQC through input strings;
3. `src/iphreeqcphast/IPhreeqcPhast.h`: cells;
4. `src/phreeqcrm/PhreeqcRM.h`: the reaction module (workers, OpenMP and MPI, units, mapping between grid cells and chemistry cells).

## Build

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j 8
ctest --test-dir build
```

The upstream presets also work unchanged, for example `cmake --preset ninja-static-release` or
`ninja-shared-release`. `cmake --list-presets` shows them all.

The options are the same as upstream (`-DPHREEQCRM_BUILD_MPI=ON`, `-DPHREEQCRM_WITH_YAML_CPP=ON`,
`-DPHREEQCRM_FORTRAN_TESTING=ON`, and so on). Each layer's file list is in `src/<layer>/sources.cmake`.
The build is verified to be equivalent to upstream v3.9.0:
- every file is compiled with identical definitions and flags;
- the installed package is identical;
- the `TestRM` outputs are identical, under OpenMP and MPI.

The installed result (`cmake --install build`) is the same `PhreeqcRM::PhreeqcRM` package, so existing programs build against it unchanged.

## Updating to a New Official Release

```bash
git switch upstream
python3 tools/sync_upstream.py --upstream <clean checkout of the new release tag> --dest .
git add -A && git commit -m "Import PhreeqcRM <tag> (flat layout)"
git switch main && git merge upstream
```

The script fails, without writing anything, if the new release contains a file its mapping rules do not cover. Extend the rules in `tools/sync_upstream.py`, never skip a file.

## Licence

PhreeqcRM is USGS software; see `LICENSE`. The layout, build files and tools added here are under the same terms unless stated otherwise.
