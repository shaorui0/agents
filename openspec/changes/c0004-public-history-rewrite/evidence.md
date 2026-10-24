# c0004 evidence (categories and counts only; original identifiers are deliberately not reproduced)

## 4.1a BEFORE: scan the backup branch with its own old tool, extended patterns (first line only)
```
$ W=$(mktemp -d)/old; git worktree add -q $W pre-public-history && cp .leak_patterns.local $W/ && python3 $W/tools/check_rules.py $W --list-legacy | head -1; git worktree remove --force $W
legacy leak hits (reported, not modified): 49 lines in 13 files
[exit=0]
```

## 4.1b AFTER: current tree, no exemptions
```
$ python3 tools/check_rules.py --list-legacy
legacy leak hits: 0 (no exemptions; all files scanned)
check_rules: OK
[exit=0]
```

## 4.1c Reading the numbers
- c0001 evidence recorded 36 hit lines in 11 files with the original pattern set. The 4.1a scan uses the pattern set as extended in this change (adds real cloud cluster names and an ops-directory name), which found 13 more lines in 2 more files: 49 lines in 13 files.
- Categories: cluster aliases, ticket ids, internal work-repo path, local home path, workspace domain, cloud cluster names, ops-directory name.
- After the rewrite: 0 (4.1b).

## 4.2a author and committer emails (one address expected)
```
$ git log --format='%ae%n%ce' | sort -u
sr1054461216@163.com
[exit=0]
```

## 4.2b commit count
```
$ git log --oneline | wc -l
      21
[exit=0]
```

## 4.2c backup branch exists
```
$ git branch --list pre-public-history
  pre-public-history
[exit=0]
```

## 4.2d make test
```
$ make test
python3 -m unittest discover -s tools -p 'test_*.py'
.....
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
python3 -W ignore -m unittest discover -s tests -t . -p 'test_*.py'
................................................
----------------------------------------------------------------------
Ran 48 tests in 5.063s

OK
[exit=0]
```

## 4.2e root commit
```
$ git log --reverse --format='%h %s' | head -1
4dde8f1 init: public snapshot, internal identifiers generalized
[exit=0]
```

## 4.3 openspec validate
```
$ openspec validate c0004-public-history-rewrite
Change 'c0004-public-history-rewrite' is valid
[exit=0]
```
