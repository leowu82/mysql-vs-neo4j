# Elder-fraud resource database prototype

The five-page [PDF](VPL-1_resources.pdf) lists **50 resource mentions**. This prototype stores them as **49 records** because one website appears twice. It keeps both original citations, page numbers, access dates, audience and topic notes, goals, and issues that need review.

**Use MySQL as the main catalog database.** It supports editing, search, filters, and reports. Neo4j helps explore shared topics, audiences, contributors, and possible duplicates. This small collection does not need both databases.

See the [analysis and comparison](docs/analysis.md) for details and diagrams. [data/catalog.json](data/catalog.json) holds the records, and [data/profile.json](data/profile.json) holds the counts.

## Run the local demo

Use Python 3.10 or newer with SQLite FTS5 search support. No extra Python packages or internet connection are needed.

```powershell
python -m elder_catalog demo
python -m elder_catalog search phishing
python -m elder_catalog search --topic phishing --format video --audience older_adults
python -m elder_catalog show r022
python -m elder_catalog related r034
python -m elder_catalog coverage
python -m unittest discover -s tests -v
```

The demo runs in SQLite. The phishing-video search returns `r034` and `r041`. The related-resource search for `r034` returns `r013` and `r041`, which share the phishing topic. Topic and audience labels still need review.

## Run MySQL and Neo4j

Start Docker Desktop with Linux containers enabled. The setup uses MySQL 8.4 and Neo4j 5.26 Community and their patch updates. To change the default passwords, copy `.env.example` to `.env` before the first start. Existing databases keep their original passwords.

```powershell
python -m elder_catalog build
docker compose up -d --wait
python -m elder_catalog load mysql
python -m elder_catalog load neo4j
$env:ELDER_NATIVE_TESTS = '1'
python -m unittest discover -s tests -v
Remove-Item Env:ELDER_NATIVE_TESTS
```

These tests load the data twice, check record counts, run example searches, and check database rules. They run only when `ELDER_NATIVE_TESTS=1`. Use databases with only prototype data.

| Database | Local address | Database name | User | Default password |
| --- | --- | --- | --- | --- |
| MySQL | `127.0.0.1:3307` | `elder_catalog` | `catalog` | `catalog_local_dev` |
| Neo4j | `127.0.0.1:7687` | `neo4j` | `neo4j` | `neo4j_local_dev` |

Open Neo4j Browser at <http://localhost:7474>. The database ports are available only on this computer. Stop the containers and keep their data with:

```powershell
docker compose stop
```

## Build files

| File | Contents |
| --- | --- |
| `build/catalog.sqlite3` | Local demo database with search and relationship checks |
| `build/mysql_schema.sql` | MySQL tables, rules, and search indexes |
| `build/mysql_seed.sql` | Sample data; adds or updates records in one transaction |
| `build/mysql_queries.sql` | Seven MySQL examples |
| `build/neo4j_schema.cypher` | Neo4j rules and indexes for Community Edition |
| `build/neo4j_seed.cypher` | Sample data; adds or updates nodes and links in one transaction |
| `build/neo4j_queries.cypher` | The same searches plus a graph example |
| `build/graph.json` | Graph nodes and links |
| `data/catalog.json` | Catalog records and original citations |
| `data/profile.json` | Source and catalog counts |

Run `python -m elder_catalog build` to rebuild these files. It replaces the SQLite file after a successful build, so edits to that file are lost.

MySQL and Neo4j imports add or update sample records. They overwrite those records' values and review statuses. They keep old records and links even if a later import omits them. Before regular catalog editing, add tracking for database changes and import versions.

## Source data

`elder_catalog/curation.py` holds details copied from the PDF. `elder_catalog/dataset.py` reads the extracted text and tracks each record's source. The importer handles this PDF's layout.

To extract the text again with Poppler installed:

```powershell
pdftotext -layout -enc UTF-8 VPL-1_resources.pdf data/source.txt
python -m elder_catalog build
```

## Checks and limits

**21 local tests pass.** They check citations, page numbers, dates, repeated references, source file hashes, URL fixes, database rules, search, rejected tags, graph links, and repeat imports. The Docker Compose setup also passes its configuration check.

The Docker engine was unavailable during setup, so the **six MySQL and Neo4j tests have not been run**. Use the commands above to check them. The local demo does not test those databases or their speed.

The 49 citations were copied from the PDF. Their details and website links have not been checked against other sources.
