READING: frontmatter is opaque to the block parse, but 0001 §4 makes the
conflict-marker refusal a line scan before any parsing, so it reaches inside
frontmatter as it reaches inside a fence. READING: frontmatter content is not
checked as YAML, so the refusal is the conflict marker, not invalid YAML.
