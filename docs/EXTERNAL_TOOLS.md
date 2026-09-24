# External Tools & Binary Dependencies

This document provides a comprehensive guide to the external command-line tools, bundled binaries (`bin/`), shared libraries (`lib/`), and runtime requirements executed by the MEOW system.

---

## 1. Overview

While MEOW performs many PDF and data processing operations natively via Python libraries (e.g. `PyMuPDF`, `pikepdf`, `odfpy`, `lxml`), several compute-intensive or specialized tasks (static site generation, archive compression, PDF linearization, and page splitting/merging) invoke external CLI tools and bundled binaries.

---

## 2. Core External Tools

### 1. 7-Zip (`bin/7zzs`)
- **Purpose**: High-ratio archive compression for final conference proceedings.
- **Location**: `bin/7zzs` (standalone binary)
- **Used by**: `meow/services/local/event/final_proceedings/compress_final_proceedings.py`
- **Typical Invocations**:
  - `bin/7zzs a -t7z -m0=Deflate -ms=16m -mmt=4 -mx=1 -- <event_id>.7z <event_id>`
- **System Requirements**: Linux x86_64 ELF execution support.

### 2. PDFtk (`bin/pdftk.sh` & `lib/pdftk-all.jar`)
- **Purpose**: PDF page extraction, multi-document concatenation, and page labeling.
- **Location**: `bin/pdftk.sh` (shell script executing `java -jar lib/pdftk-all.jar`)
- **Used by**: `meow/services/local/event/final_proceedings/event_pdf_utils.py` (`pdf_unite_pdftk`, `pdf_separate`)
- **System Requirements**: **Java Runtime Environment (JRE / OpenJDK 8+)** installed and available in the system `PATH` (`java`).

### 3. QPDF (`bin/qpdf`, `bin/fix-qdf`, `bin/zlib-flate`)
- **Purpose**: Structural PDF inspection, web-optimization (linearization), page label removal, and stream decompression.
- **Location**: `bin/qpdf` or system `qpdf` binary, backed by dynamic libraries in `lib/` (`libqpdf.so.29`, `libqpdf.so.30`).
- **Used by**: `meow/services/local/event/final_proceedings/event_pdf_utils.py` (`pdf_unite_qpdf`, `pdf_clean_qpdf`)
- **Typical Invocations**:
  - `qpdf --linearize --remove-page-labels input.pdf -- output.pdf`
  - `qpdf --empty --pages file1.pdf 1-1 file2.pdf 1-1 -- output.pdf`

### 4. MuPDF (`bin/mutool` / `mutool`)
- **Purpose**: Fast PDF cleaning, garbage collection, linearization, and multi-file merging.
- **Location**: `bin/mutool` or system `mutool` executable.
- **Used by**: `meow/services/local/event/final_proceedings/event_pdf_utils.py` (`pdf_unite_mutool`, `pdf_clean_mutool`)
- **Typical Invocations**:
  - `mutool merge -o output.pdf file1.pdf 1-N file2.pdf 1-N`
  - `mutool clean -l input.pdf output.pdf 1-N`

### 5. Hugo (`bin/hugo`)
- **Purpose**: Fast static site generator used to build the static conference proceedings website from HTML/Jinja-generated content.
- **Location**: `bin/hugo`
- **Used by**: `meow/services/local/event/final_proceedings/hugo_plugin/hugo_final_proceedings_plugin.py` (`generate`)
- **Typical Invocations**:
  - `bin/hugo --source <src_dir> --destination out`

### 6. Poppler Utilities (`bin/pdfunite` / `pdfunite`)
- **Purpose**: PDF page concatenation.
- **Location**: `bin/pdfunite` or system `pdfunite`.
- **Used by**: `meow/services/local/event/final_proceedings/event_pdf_utils.py` (`pdf_unite_poppler`)

### 7. Ghostscript (`bin/gs` / `gs`)
- **Purpose**: PostScript and PDF conversion and rasterization fallback.
- **Location**: `bin/gs` or system `gs`.

### 8. pdfcpu (`bin/pdfcpu`)
- **Purpose**: Go-based PDF processing tool for validation, optimization, and stamp/watermark operations.
- **Location**: `bin/pdfcpu`

---

## 3. Bundled Shared Libraries (`lib/`)

The repository includes pre-compiled shared libraries (`lib/`) to ensure binary compatibility across diverse Linux execution environments:

| Library File | Purpose |
|---|---|
| `lib/pdftk-all.jar` | Complete Java archive for PDFtk operations. |
| `lib/libqpdf.so.29`, `lib/libqpdf.so.30` | QPDF engine shared object. |
| `lib/libgnutls.so.30`, `lib/libnettle.so.*`, `lib/libhogweed.so.*` | Cryptographic and TLS libraries required by network/crypto tools. |
| `lib/libffi.so.7`, `lib/libffi.so.8` | Foreign function interface runtime library. |
| `lib/libidn2.so.0`, `lib/libunistring.so.2`, `lib/libtasn1.so.6` | String manipulation, ASN.1, and internationalized domain name handling. |
| `lib/libjpeg.so.8` | JPEG image decoding and compression support. |
| `lib/libp11-kit.so.0` | PKCS#11 module loading and certificate handling. |

---

## 4. Execution Flow & Process Wrapper

External commands are executed asynchronously via structured process helpers located in `meow/utils/process.py`:
- **`execute_process(args, cwd)`**: Runs a subprocess with streaming `stdout` and `stderr` using `anyio.open_process`.
- **`run_cmd(command)`**: Runs a command using `anyio.run_process` with error logging and exit code validation.
