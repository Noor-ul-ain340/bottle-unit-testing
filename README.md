# Bottle – Unit Test Automation (Assignment 3, Project Phase 2)

**Group members:** Laiba Tabassum · Noor ul Ain
**Project under test:** [Bottle](https://github.com/bottlepy/bottle) – a fast, single-file Python web framework (`bottle.py`, version 0.14-dev)
**Language / tools:** Python 3.10+, pytest, pytest-xdist (parallel), pytest-order (ordering), openpyxl (Excel sheets)

---

## 1. Setup (Task 1)

```bash
git clone <this-repo-url>
cd bottle-unit-testing

python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
pytest            # all tests should pass
```

`bottle.py` (original, unmodified file from https://github.com/bottlepy/bottle) is kept in the repo root so that `import bottle` works directly.
Setup video: `docs/setup_video.mp4` (link/file added by the group).

## 2. Project structure

```
bottle.py                      # open-source project under test (unchanged)
pytest.ini                     # markers, config (Task 4)
requirements.txt
ECP_BVA_Notes.md               # ECP / BVA design notes (Task 2)
tests/
  conftest.py                  # CSV reader helper
  test_laiba_response.py       # Laiba – BaseResponse
  test_laiba_router.py         # Laiba – Router
  test_noor_headers.py         # Noor  – HeaderDict
  test_noor_template.py        # Noor  – SimpleTemplate
test_data/
  test_data_laiba.csv          # HTTP status data (Task 3)
  test_data_noor.csv           # header data (Task 3)
docs/
  Test_Cases_Laiba.xlsx        # Excel test cases (Task 3)
  Test_Cases_Noor.xlsx
tools/make_excel.py            # script that generated the Excel files
```

## 3. Who tested what

| Member | Module (class) | File | Test functions | Test cases (with parametrize) |
|---|---|---|---|---|
| Laiba Tabassum | `BaseResponse` | `tests/test_laiba_response.py` | 14 | 43 |
| Laiba Tabassum | `Router` | `tests/test_laiba_router.py` | 14 | 22 |
| Noor ul Ain | `HeaderDict` | `tests/test_noor_headers.py` | 12 | 30 |
| Noor ul Ain | `SimpleTemplate` | `tests/test_noor_template.py` | 12 | 21 |
| | | **Total** | **52** | **116** |

Techniques: **ECP** and **BVA** (details in `ECP_BVA_Notes.md`).
Data-driven tests: `@pytest.mark.parametrize` everywhere, plus CSV-driven tests (`test_status_codes_from_csv`, `test_headers_from_csv`).

## 4. Running the tests (Task 4)

```bash
pytest                          # everything, in the configured order
pytest -v                       # verbose
pytest -n auto                  # PARALLEL (uses all CPU cores, pytest-xdist)
pytest -n 4                     # parallel with 4 workers
```

### Suites / groups (markers defined in `pytest.ini`)

| Command | Suite |
|---|---|
| `pytest -m laiba_tests` | Laiba's tests only |
| `pytest -m noor_tests` | Noor's tests only |
| `pytest -m smoke` | Smoke / sanity tests |
| `pytest -m bva` | Boundary Value Analysis tests |
| `pytest -m ecp` | Equivalence Class tests |
| `pytest -m csv_driven` | Tests that read CSV files |
| `pytest -m "response or router"` | Laiba's modules |
| `pytest -m "headers or template"` | Noor's modules |
| `pytest -m "laiba_tests and bva"` | Combination of markers |
| `pytest -m "smoke" -n auto` | A suite in parallel |

### Execution order
Order is set with `@pytest.mark.order(n)` (pytest-order). In every file the smoke test is `order(1)`, then ECP tests, then BVA tests, then the CSV-driven test last.
Check the order with: `pytest --collect-only -q`.

## 5. Test result summary

- Total collected test cases: **116**
- Passed: **116**, Failed: **0** (sequential and with `-n auto`)

### Observations about Bottle behaviour found while testing
- `BaseResponse(status=0)` silently keeps `200 OK` because `0` is falsy (no error raised).
- Valid-range status codes without a standard reason (e.g. 599) get the reason `Unknown`.
- `HeaderDict` accepts an empty header name `""`.
- `Router` treats `/hello/` and `/hello` as different paths (404).
- `SimpleTemplate("")` raises `TemplateError` (empty source is "no template").

## 6. Git workflow

Each member commits their own files from their own account, e.g.

```bash
git add tests/test_laiba_response.py tests/test_laiba_router.py test_data/test_data_laiba.csv docs/Test_Cases_Laiba.xlsx
git commit -m "Laiba: Added ECP/BVA tests for BaseResponse and Router"
git push
```
