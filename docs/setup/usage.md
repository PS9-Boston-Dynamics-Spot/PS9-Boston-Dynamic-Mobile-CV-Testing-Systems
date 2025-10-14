# Quick Start

## Start Docker Container

```bash
docker compose up -d

docker compose exec app bash
```

## Option 1: One-Command Setup (Recommended)

``` bash
make run
```

This single command will:
- Create virtual environment (if needed)
- Install all dependencies
- Start a shell with activated virtual environment

## Option 2: Step-by-Step Setup
```bash
# 1. Create virtual environment
make create-venv

# 2. Install dependencies
make install

# 3. Enter development environment
make use-venv
```

---

## Development Commands

### Environment Management

| Command                                  | Description                               |
|------------------------------------------|-------------------------------------------|
| ```make create-venv```                   | Create Python virtual environment         |
| ```make use-venv```                      | Activate virtual environment in new shell |
| ```make check-venv-using```              | Check if virtual environment is active    |
| ```make install```                       | Install project dependencies              |

### Code Quality & Testing
| Command                                  | Description                                    |
|------------------------------------------|------------------------------------------------|
| ```make test```                          | Run all tests with pytest                      |
| ```make lint```                          | Run code quality checks (flake8)               |
| ```make format```                        | Auto-format code with black                    |
| ```make qa-check```                      | Run format + lint + tests (full quality check) |

### Maintenance
| Command                                  | Description                                    |
|------------------------------------------|------------------------------------------------|
| ```make clean```                         | Remove cache and temporary files               |
| ```make help```                          | Show all available commands                    |

---

## Daily Development Workflow

**Starting work**
```bash
make use-venv
```

or 

```bash
make run
```

**Before committing code**
```bash
make qa-check
```

**Installing new dependencies**
1. Add package to requirements.txt
2. Run:
```bash
make install
```

**Running tests only**
```bash
make test
```

---

## Verify Everything Works

```bash
# Check which Python is being used
which python # Expected output: /app/.venv/bin/python

# OR check if the virtual environment is active
make check-venv-using # Expected output: Virtual environment is active.

# Run a test script
python test.py # Expected output: Hello World!
```
---

## Troubleshooting

### Virtual Environment Issues
+ **Not activated:** Run `make use-venv`
+ **Check status:** Run `make check-venv-using`
+ **Recreate:** Delet `.venv` folder and run `make create-venv`

### Dependency Issues
```bash
make clean
make install
```

### Test Failures
+ Run `make test` to see detailed failure information
+ Check test files in `tests/` directory
--- 

## Best Practices
+ Always work in the virtual environment (your prompt should show)
+ Run `make qa-check` before committing
+ Add new dependencies to `requirements.txt`
+ Use `make format` to maintain consistent code style