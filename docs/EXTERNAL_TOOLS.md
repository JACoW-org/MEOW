# External Tools & Binary Dependencies

This document lists the external command-line tools, bundled binaries (`bin/`), shared libraries (`lib/`) and runtime requirements used by MEOW, distinguishing what the **active code path executes** from what is merely **present or legacy**.

---

## 1. Overview

Most PDF and data processing is done in-process with Python libraries (`PyMuPDF`, `pikepdf`, `odfpy`, `lxml`). A few tasks (static site generation, archive compression, PDF concatenation) execute external programs. All paths are relative, so MEOW must be started from the repository root. The bundled binaries are Linux x86_64 ELF executables.

---

## 2. Tools executed by the active code path

### 1. PDFtk (`bin/pdftk.sh` + `lib/pdftk-all.jar`)
- **Purpose**: concatenation of PDF files (`pdftk <files> cat output <out>`) when building the `brief` and `volume` proceedings PDFs.
- **Location**: `bin/pdftk.sh`, a shell script running `java -jar lib/pdftk-all.jar "$@"`.
- **Used by**: `pdf_unite_pdftk` in `meow/services/local/event/final_proceedings/event_pdf_utils.py`, called from `concat_contribution_papers.py`.
- **System requirements**: a **Java runtime** (`java`) available in the `PATH`. The minimum Java version has not been verified.

### 2. Hugo (`bin/hugo`)
- **Purpose**: static site generator that builds the final proceedings website from the generated content.
- **Used by**: `ssg_cmd` / `generate` in `meow/services/local/event/final_proceedings/hugo_plugin/hugo_final_proceedings_plugin.py`.

### 3. 7-Zip (`bin/7zzs`)
- **Purpose**: compression of the generated proceedings site into a `.7z` archive.
- **Used by**: `meow/services/local/event/final_proceedings/compress_final_proceedings.py`.
- **Invocation**: `bin/7zzs a -t7z -m0=Deflate -ms=16m -mmt=4 -bd -mx=1 -- <event_id>.7z <event_id>`

---

## 3. Optional alternatives (defined in code, not used by the active flow)

`event_pdf_utils.py` also defines helpers based on other CLI tools, but no code outside that module calls them:

| Helper | Executable | Resolved as |
|---|---|---|
| `pdf_unite_qpdf`, `pdf_clean_qpdf` | `qpdf` | `PATH` (the `bin/qpdf` path is commented out in `get_qpdf_cmd`) |
| `pdf_unite_mutool`, `pdf_clean_mutool` | `mutool` | `PATH` (the `bin/mutool` path is commented out in `get_mutool_cmd`) |
| `pdf_unite_poppler` | `pdfunite` | `PATH` (the `bin/pdfunite` path is commented out in `get_pdfunite_cmd`) |

They only work if the corresponding tool is installed on the system. Note that `pdf_linearize_qpdf` does **not** run the `qpdf` CLI: despite its name it uses `pikepdf`.

---

## 4. Files present in the repository but not referenced by the code

The following files exist under `bin/` but nothing in `meow/` invokes them. Their purpose is not documented anywhere in the repository; do not assume they are required, and do not rely on them without checking:

- `bin/gs`, `bin/pdfcpu`, `bin/fix-qdf`, `bin/zlib-flate`
- `bin/qpdf`, `bin/mutool`, `bin/pdfunite` (see section 3: the code looks for these tools in the `PATH`, not in `bin/`)

---

## 5. Bundled Shared Libraries (`lib/`)

| Library File | Notes |
|---|---|
| `lib/pdftk-all.jar` | Java archive run by `bin/pdftk.sh` (active). |
| `lib/libqpdf.so.29`, `lib/libqpdf.so.30` | Shared objects used by the bundled qpdf-family binaries, which the active flow does not use. |
| `lib/libgnutls`, `libnettle`, `libhogweed`, `libp11-kit`, `libtasn1`, `libidn2`, `libunistring`, `libffi`, `libjpeg` | Dependencies of the bundled binaries above (not standalone tools). |

---

## 6. Process helpers

`meow/utils/process.py` provides `execute_process(args, cwd)` (streaming `stdout`/`stderr` with `anyio.open_process`) and `run_cmd(command)` (`anyio.run_process` with error logging). Note that the Hugo and 7-Zip calls above use `anyio` directly rather than these helpers.
