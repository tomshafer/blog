"""Generate a static blog directory structure.

Usage:
    make_blog.py PUBLIC_DIR

This program behaves simply: Point it at a directory that contains Markdown
files in some configuration, and the program will:

1. Generate in-place HTML files, attaching a template.
2. Generate an index page (index.html) with either a long list of post titles
   or a long list of full posts.

The program makes many assumptions about titling, structure, templating, etc.
These assumptions could be relaxed via, e.g., a YAML configuration file in a
later update.

"""

from docopt import docopt

if __name__ == "__main__":
    cli_args = docopt(__doc__)
