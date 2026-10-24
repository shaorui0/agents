# 0004 public-history-rewrite

- Core idea: an exemption in a scanner ("old files are fine") is a debt. Either the old content is clean or the scan lies. I chose to make the content clean and delete the exemption.
- Counter-intuitive: the pattern list is only as good as your last incident. A manual pass found two categories (cloud cluster names, an internal directory name) the scanner had never been taught. Scanning proves the absence of known patterns, nothing more.
- Consistent mapping matters more than pretty names: same original, same substitute, everywhere. Otherwise prose that says "the second prod cluster" stops lining up with the commands.
- Pitfall: the evidence file for a leak-removal change is itself a leak risk. Record categories and counts, never the originals; I even had to keep my scratch path out of the command line because it contained a guarded word.
- Pitfall: before and after numbers need the same pattern set. 36 lines with the old patterns became 49 with the extended ones; say so rather than quote the smaller number.
- Rewriting history is cheap locally and irreversible once pushed. A backup branch that is never pushed makes the local step reversible; the force-push is the real decision and stays with the human.
- On macOS, `sed -i` needs an empty suffix argument. It silently ate my script once and the `&&` chain stopped, which is the only reason that commit did not happen with a broken tree.
