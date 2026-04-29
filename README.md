## Context

Before you can write SQL transformations, you need a working local development environment — a dbt project connected to a local data warehouse. In this challenge you'll set that up from scratch using dbt Core with DuckDB: professional-grade tools that run entirely on your machine, with no cloud account required.

## Objective

Set up dbt Core locally with DuckDB as your data warehouse. This gives you full control over your transformation workflow and works entirely on your machine.

## 1. Install and Verify dbt

### 1.1. Install dbt

dbt is not part of the standard Le Wagon setup, so you need to install it now. The `dbt-duckdb` package installs both dbt Core and the DuckDB adapter in one step.

**📍 In your terminal**, install dbt with the DuckDB adapter:

```bash
pip install dbt-duckdb "googleapis-common-protos>=1.69.0"
```

<details>
<summary markdown="span">**What does this install?**</summary>

- `dbt-core` — the dbt transformation framework
- `dbt-duckdb` — the DuckDB adapter that lets dbt talk to a DuckDB database
- `duckdb` — the DuckDB database engine itself
- `googleapis-common-protos>=1.69.0` — fixes a protobuf version conflict between dbt and Google packages used later in the ML module

</details>

### 1.2. Verify Installation

**📍 In your terminal**, verify dbt installed correctly:

```bash
dbt --version
```

<details>
<summary markdown="span">**Expected output** (version numbers may differ — you need dbt Core 1.7.x or higher)</summary>

```bash
Core:
  - installed: 1.7.x or higher
  - latest:    1.7.x or higher

Plugins:
  - duckdb: 1.7.x or higher
```

</details>

## 2. Create dbt Project Structure

### 2.1. Initialize Project

Throughout this unit we'll use a fictional coffee shop called **Jaffle Shop** as our working dataset. A "jaffle" is an Australian toasted sandwich — the shop sells those and coffee. ☕🥪

Jaffle Shop is the official dbt tutorial dataset, used by data engineers all over the world when learning dbt. That means it's well documented, widely recognised in the industry, and genuinely worth being familiar with — you'll likely encounter references to it again once you're working in a data role.

**📍 In your terminal** create your dbt project:

```bash
# Check that you are in the challenge directory for this challenge
pwd

# Create dbt project in the current directory
dbt init jaffle_shop_dbt
```

You'll be prompted:

```bash
Which database would you like to use?
[1] duckdb
Enter a number: 1
```

This creates:

```bash
jaffle_shop_dbt/
├── analyses/                 # Ad-hoc queries
├── dbt_packages/             # dbt dependencies (gitignored)
├── dbt_project.yml           # Project configuration
├── logs/                     # dbt execution logs (gitignored)
│   └── dbt.log
├── macros/                   # Reusable SQL snippets
├── models/                   # SQL transformation files
│   └── example/
│       ├── my_first_dbt_model.sql
│       ├── my_second_dbt_model.sql
│       └── schema.yml
├── README.md                 # Project documentation
├── seeds/                    # CSV files to load
├── snapshots/                # Track data changes over time
├── target/                   # Compiled SQL and generated docs (created when you run dbt)
└── tests/                    # Custom data tests
```

You can view that structure we've just created with a terminal command. Can you remember which one?

<details>
<summary markdown="span">**Which terminal command?**</summary>

```bash
tree
```

This will show the directory structure in a tree format. If you don't have `tree` installed, you can use `ls -R` as an alternative.

</details>

**Note:** Depending on your version of dbt, you may also see a `logs/` directory appear in your challenge folder — not inside `jaffle_shop_dbt/`. That's normal.

### 2.2. Create .gitignore

Before we configure dbt, let's set up `.gitignore` to exclude files that shouldn't be pushed to GitHub.

**📍 In your terminal**, open or create the .gitignore file:

```bash
code jaffle_shop_dbt/.gitignore
```

**📝 In VS Code**, add these patterns (if the file already exists, just add any missing patterns):

```markdown
# dbt artifacts (compiled SQL, generated docs)
target/
dbt_packages/
logs/

# Database files (too large for GitHub, regenerable)
*.duckdb
*.duckdb.wal

# Python bytecode
*.pyc
__pycache__/

# OS files
.DS_Store
```

**💾 Save the file** (Cmd+S or Ctrl+S).

**📍 Back in your terminal**, verify the file was created and add `logs/` to the challenge root `.gitignore` just in case:

```bash
echo "logs/" >> .gitignore
cat jaffle_shop_dbt/.gitignore
```

<details>
<summary markdown="span">**Why these specific exclusions?**</summary>

**Files to exclude:**

- `target/` - Compiled SQL (regenerable with `dbt compile`)
- `dbt_packages/` - Downloaded dbt dependencies (reinstallable, like pip packages)
- `logs/` - Execution logs
- `*.duckdb` - Database files can grow large and are regenerable
- Python/OS files - Not project code

**What WILL be committed:**

- `dbt_project.yml` - Project configuration
- `models/*.sql` - Your transformation logic
- `models/schema.yml` - Source/model documentation
- `analyses/*.sql` - Ad-hoc analysis queries

</details>

### 🧪 Checkpoint 1: Push Initial dbt Project

**Before pushing, validate your setup:**

**📍 In your terminal**, run the checkpoint 1 tests:

```bash
# Run checkpoint 1 tests
pytest tests/test_project_setup.py -v
```

**If tests pass**, commit your dbt project setup:

```bash
# Stage the dbt project files
git add jaffle_shop_dbt/

# Commit with descriptive message
git commit -m "Initialize dbt project with gitignore"

# Push to GitHub (triggers automated tests)
git push origin master
```

**What gets pushed:**

- `jaffle_shop_dbt/dbt_project.yml` (project config)
- `jaffle_shop_dbt/.gitignore` (excludes database files)
- `jaffle_shop_dbt/models/` (empty models directory)
- All dbt starter project files

**What's excluded:**

- `dev.duckdb` (gitignored)
- `target/` (gitignored)
- `~/.dbt/profiles.yml` (local config, not in project)

Your dbt project structure is created and committed. The project folder is on GitHub, but it's not yet connected to any data — that's what the next two steps set up: a shared database location and a source configuration that tells dbt what raw tables exist.

### 2.3. Create Shared Database Location

**Why a shared database?** Instead of copying the database between challenges, we'll create it once in a shared location and use symlinks. This means:

- Our database is only created once, but used across all of this unit's challenges 🎉
- DBeaver only has to connect once (no path updates needed each challenge) 🎉
- There's no need to copy 1MB+ files between challenges 🎉
- Our data stays consistent across all challenges 🎉

**📍 In your terminal**, create the shared database directory:

```bash
# Create shared directory for dbt databases (two levels above this challenge, at 03-Data-Transformation/)
mkdir -p ../../dbt-shared

# Initialize the database file with DuckDB
python -c "import duckdb; duckdb.connect('../../dbt-shared/dev.duckdb').close()"

# Create symlink from your project to the shared database
# Note: Path is ../../../dbt-shared because symlink is evaluated from inside jaffle_shop_dbt/
ln -s ../../../dbt-shared/dev.duckdb jaffle_shop_dbt/dev.duckdb

# Verify the symlink was created and works
ls -l jaffle_shop_dbt/dev.duckdb
# Should show: jaffle_shop_dbt/dev.duckdb -> ../../../dbt-shared/dev.duckdb
```

<details>
<summary markdown="span">**💡 What is a symlink?**</summary>

A symlink (symbolic link) is like a shortcut that points to another file:

- **Original file**: `../../dbt-shared/dev.duckdb` (the actual database, in your `03-Data-Transformation/` directory)
- **Symlink**: `jaffle_shop_dbt/dev.duckdb` (points to the original)
- **Path**: `../../../dbt-shared/dev.duckdb` (three levels up from inside `jaffle_shop_dbt/`)

When dbt or DBeaver accesses `jaffle_shop_dbt/dev.duckdb`, it automatically uses the shared database.

**Benefits:**

- Multiple projects can use the same database
- Symlinks are gitignored (won't be pushed to GitHub)
- Only the actual database file takes up disk space

</details>

### 2.4. Configure Connection (profiles.yml)

dbt uses `~/.dbt/profiles.yml` to connect to your database. `dbt init` may have already created this file for you.

**📍 In your terminal**, check if it exists:

```bash
cat ~/.dbt/profiles.yml
```

If `dbt init` created it, you'll see something like this:

```yaml
jaffle_shop_dbt:
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb
      threads: 1
    prod:
      type: duckdb
      path: prod.duckdb
      threads: 4
  target: dev
```

If you can see `type: duckdb`, `path: dev.duckdb`, and `target: dev`, you're all set — skip ahead to [2.5. Test Connection](#25-test-connection).

If the file doesn't exist, or it was configured for a different database, create it now:

```bash
mkdir -p ~/.dbt

code ~/.dbt/profiles.yml
```

**📝 In VS Code**, paste in this configuration:

```yaml
jaffle_shop_dbt:  # Must match your project name
  target: dev
  outputs:
    dev:
      type: duckdb
      path: dev.duckdb  # Will use the symlink in your project directory
      threads: 4
```

**Important:** The path `dev.duckdb` points to the symlink in your project, which points to `../../../dbt-shared/dev.duckdb` (shared database in `03-Data-Transformation/dbt-shared/`).

**💾 Save the file** (Cmd+S on macOS, Ctrl+S on Windows) and close VS Code.

### 2.5. Test Connection

**📍 Back in your terminal**, change the directory into the `jaffle_shop_dbt` project:

```bash
cd jaffle_shop_dbt
```

And then, test the connection:

```bash
dbt debug
```

<details>
<summary markdown="span">**Expected output**</summary>

```bash
Connection test: [OK connection ok]
```

</details>

If `dbt debug` passes, you're ready to start transforming data!

<details>
<summary markdown="span">**🔧 Troubleshooting: Cannot open file "dev.duckdb"**</summary>

**Error:** `IO Error: Cannot open file "...dev.duckdb": No such file or directory`

**Problem:** The symlink is broken or the database file doesn't exist.

**📍 In your terminal**, first navigate back to the challenge directory:

```bash
cd ..
```

Then check if the symlink exists and points to the right place:

```bash
# Check if symlink exists
ls -l jaffle_shop_dbt/dev.duckdb
# Should show: jaffle_shop_dbt/dev.duckdb -> ../../../dbt-shared/dev.duckdb

# Test if symlink works (should show file info, not "broken symbolic link")
file jaffle_shop_dbt/dev.duckdb

# If broken, recreate the database and symlink:
rm -f jaffle_shop_dbt/dev.duckdb
python -c "import duckdb; duckdb.connect('../../dbt-shared/dev.duckdb').close()"
ln -s ../../../dbt-shared/dev.duckdb jaffle_shop_dbt/dev.duckdb
```

Then navigate to the dbt project:

```bash
cd jaffle_shop_dbt
```

And test the connection again:

```bash
# Try dbt debug again
dbt debug
```

**Check the symlink path:** The symlink must be `../../../dbt-shared/dev.duckdb` (three levels up) because:

- Symlink is evaluated from inside `jaffle_shop_dbt/` directory
- Need to go up three levels to reach the `03-Data-Transformation/` directory
- Then into `dbt-shared/` directory

</details>

## 3. Connect to Your Data Sources

### 3.1. Update dbt_project.yml

<details>
<summary markdown="span">**💡 Understanding Materialization**</summary>

Materialization determines how dbt stores your models in the database:

**View** (lightweight)

- SQL query stored in database
- No physical data storage
- Recalculates every time you query it
- Best for: Staging models that transform raw data

**Table** (physical storage)

- Data stored physically in database
- Uses storage space
- Fast queries (no recalculation)
- Best for: Marts/final models used in dashboards

**Why we use different materializations:**

- **Staging → Views**: Keep storage low, data stays fresh
- **Marts → Tables**: Speed up dashboard queries

The `+schema` setting creates separate schemas to organize models (e.g., `staging`, `marts`).

</details>

**📝 In VS Code**, open `jaffle_shop_dbt/dbt_project.yml`.

We're going to replace everything in that file with the below:

```yaml
name: 'jaffle_shop_dbt'
version: '1.0.0'
config-version: 2

profile: 'jaffle_shop_dbt'

model-paths: ["models"]
analysis-paths: ["analyses"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

clean-targets:
  - "target"
  - "dbt_packages"

models:
  jaffle_shop_dbt:
    +materialized: view  # Default: create views (not tables)
    staging:
      +materialized: view
      +schema: staging
```

### 3.2. Define Sources

#### 💡 What are Sources in dbt?

Sources tell dbt about tables that exist in your database but weren't created by dbt (like raw data loaded from CSVs).

**Why define sources instead of hardcoding table names?**

1. **Lineage tracking**: See data flow from raw → transformed in docs
2. **Freshness tests**: Check if source data is up-to-date
3. **Refactoring safety**: Change source table name in one place
4. **Documentation**: Centralized place to document raw data
5. **Environment switching**: The schema resolves automatically for dev vs. prod — no SQL changes needed when promoting to production

**Without sources:**

```sql
SELECT * FROM raw.raw_customers  -- Hard to track, no freshness tests
```

**With sources:**

```sql
SELECT * FROM {{ source('jaffle_shop', 'raw_customers') }}  -- Tracked, testable!
```

#### Time to Define Your Sources

**📍 In your terminal**, Navigate to dbt project directory (only if you're in the challenge directory):

```bash
cd jaffle_shop_dbt
```

And then, use the below command to remove the example directory and everything inside:

```bash
# Remove example models
rm -rf models/example
```

**📝 In VS Code**, create a new file `models/schema.yml` with this content:

```yaml
version: 2

sources:
  - name: jaffle_shop
    description: "Jaffle Shop coffee shop raw data"
    schema: raw
    meta:
      owner: "Data Team"

    tables:
      - name: raw_customers
        description: "Customer information"

      - name: raw_orders
        description: "Order transactions"

      - name: raw_payments
        description: "Payment records"
```

### 🧪 Checkpoint 2: Push Source Definitions

**Before pushing, validate your sources:**

**📍 In your terminal**, if you are not already in the challenge directory, navigate there now:

```bash
cd ..
```

Then run the checkpoint 2 tests:

```bash
pytest tests/test_sources.py -v
```

**If all tests pass**, commit your source configuration:

```bash
# Stage the updated project config, deleted example models, and new schema file
git add jaffle_shop_dbt/dbt_project.yml jaffle_shop_dbt/models

# Commit with descriptive message
git commit -m "Add source definitions for raw data"

# Push to GitHub (triggers automated tests)
git push origin master
```

---

dbt now knows where your raw data lives. In the next challenge you'll load that data into DuckDB and write your first transformation model.

## 🎉 Challenge Complete

dbt is installed, connected to DuckDB, and your source tables are defined.

**Key takeaways:**

- `~/.dbt/profiles.yml` lives outside your project — it holds connection details that stay on your machine, not in git
- Defining sources in `schema.yml` instead of hardcoding table names is what enables the lineage graph
- `+schema: staging` in `dbt_project.yml` sets the schema for every model in that folder — one config, inherited by all
