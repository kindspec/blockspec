0002, Addendum (three defaults): "When duplicate-name and unpaired-region
both apply, the refusal is duplicate-name. A name is declared by a one-line
marker or by a `:begin`." Two `:begin` lines declare `a` twice, and one of
them has no `:end`, so both refusals apply.
