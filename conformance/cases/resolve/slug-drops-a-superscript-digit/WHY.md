0001, Addendum (heading slugs, as rewritten): every character in
github-slugger 2.0.0's `regex.js` class is removed, and "it removes `²`".
github-slugger 2.0.0's `slug("x²")` returns `x`. A reader that kept
Unicode numbers would give `x²`, and one that normalised compatibility
characters first would give `x2`, which names nothing here.
