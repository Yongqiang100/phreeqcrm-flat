# Flat PhreeqcRM: Design (supersedes the paused restructuring for PhreeqcRM alone)

| Field | Value |
|---|---|
| Status | Revision 1 (2026-10-15) |
| Basis | R0 audit (`docs/restructure/restructure_r0_audit_report.md`), decisions RS-D1 to RS-D5 |
| Scope | PhreeqcRM only. phreeqc3 stays upstream (its engine is byte-identical to PhreeqcRM's copy, RS-D2) |

## Decisions

**FL-D1. Repository and branches.**
- The repository is `~/phreeqcrm-flat`.
- Branch **`upstream`** holds only the output of `tools/sync_upstream.py` for an official release, plus the tool, the root README and this document.
- Branch **`main`** is `upstream` plus the flat build (F2). Upstream updates arrive by `git merge upstream`.

**FL-D2. Mapping: `tools/sync_upstream.py`,** with ordered rules and a manifest.
- Layer directories are as in the README.
- **IPhreeqc's own Fortran interface stays in `src/iphreeqc/`,** where its layer is. `src/interfaces/` holds only PhreeqcRM's C and Fortran APIs.
- **Dropped** (with reasons, in `UPSTREAM_DROPPED.tsv`): CI, VCS metadata, editor files, autotools, Visual Studio and Jenkins.
- **Upstream build files** are kept read-only under `cmake/upstream/`, so that their changes in a new release are visible in `git diff`.
- **The R0 AMBIGUOUS rows are resolved:**
  - `LICENSE` stays at the root;
  - `README.md` and `DEVELOPER.md` go to `docs/upstream/`;
  - `CMakePresets.json` goes to `cmake/upstream/` (the flat presets are new, F2);
  - `environment.yml`, `mamba.environment.yml` and `uv.lock` go to `python/`;
  - `src/phreeqcrm/__init__.py` goes to `python/phreeqcrm/`;
  - `test.xml` stays with the engine.
- **No source file is edited.** R0 U5 found that no include needs a path change, because all cross-layer includes go through `-I`.

**FL-D3. The build (F2).**
- **Libraries:** one CMake `OBJECT` library per layer (`phreeqc_common`, `phreeqc_engine`, `iphreeqc`, `iphreeqcphast`, `phreeqcrm_core`, `phreeqcrm_c`, `phreeqcrm_fortran`), all linked into the single library `PhreeqcRM`. The installed package stays exactly `PhreeqcRM::PhreeqcRM`.
- **Settings:** all common compile settings (definitions, include directories, language standard, OpenMP or MPI) come from one INTERFACE target, so that **every source file receives exactly the definitions it receives upstream**. RS-D2 and R0 U8: `IPhreeqc_EXPORTS SWIG_SHARED_OBJ USE_PHRQ_ALLOC`, plus `USE_OPENMP` or `USE_MPI`.
- **Parity:** the build parity is proven by comparing per-file compile commands with R0's `compile_flags_cc_phreeqcrm_{openmp,mpi}.tsv`.

**FL-D4. Acceptance (F2):**
1. **Compile flags:** identical per file (paths mapped through the manifest).
2. **Installed files:** the same installed file set and identical installed headers.
3. **Tests:** `ctest` passes in OpenMP and MPI.
4. **`TestRM` outputs:** identical to the v3.9.0 baselines (`openmp_run1`, `Tests_np2`, `Tests_np4`) under P2-D16.
5. **External program:** the benchmark driver builds against the flat installation, with identical concentrations.
6. **The overlay** attaches to the flat tree (F3, needs a third tree-detection branch in `attach.cmake`).
