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

import codecs
import os
import re
import markdown
from dateutil.parser import parse as parse_date
from docopt import docopt
from mako.template import Template


def find_files(base_dir, extensions=("md",)):
    """Walk 'base_dir' and return files with extensions in 'extensions'."""
    print(base_dir, extensions)
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in filenames:
            if os.path.splitext(fname)[-1].lower().lstrip(".") in extensions:
                yield os.path.join(dirpath, fname)


class Post(object):
    """
    Simple representation of a blog post. Includes:

    source: Raw Markdown
    html:   Parsed HTML
    title:  Title from the metadata
    date:   Datetime object
    """
    title, date, source, html, source_path = 5*[None]

    def __init__(self, file_path, md_parser):
        """Use 'md_parser' to parse 'file_path' into an object"""
        with codecs.open(file_path, mode="r", encoding="utf-8") as fh:
            self.source_path = file_path
            self.source = fh.read()
            self.html = md_parser.convert(self.source)
            # Assign meta, requiring title and date
            meta = md_parser.Meta
            self.title = self.unquote(meta["title"][0])
            self.date = parse_date(self.unquote(meta["date"][0]))

    @staticmethod
    def unquote(string):
        """Remove quotes from the beginning/end of a string"""
        return re.sub(r"(^['\"]|['\"]$)", "", string)


if __name__ == "__main__":
    cli_args = docopt(__doc__)

    # Find Markdown files
    md_extensions = ("md", "mdown", "text")
    md_files = tuple(find_files(cli_args["PUBLIC_DIR"], md_extensions))
    if not md_files:
        quit("No markdown files found.")

    # Initialize the parser
    parser = markdown.Markdown(
        output_format="html5",
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.footnotes",
            "markdown.extensions.tables",
            "markdown.extensions.codehilite",
            "markdown.extensions.meta",
            "markdown.extensions.smarty"
        ],
        extension_configs={
            "markdown.extensions.footnotes": {
                "UNIQUE_IDS": True
            },
            "markdown.extensions.codehilite": {
                "use_pygments": True
            }
        })

    # Generate a large list of post objects
    posts = []
    for filename in md_files:
        posts.append(Post(filename, parser))
        parser.reset()

    # Load templates
    tmpl_post = Template(input_encoding="utf-8",
                         filename=os.path.join(
                             os.path.dirname(__file__),
                             "../public/assets/template",
                             "post_template.html"))
    tmpl_index = Template(input_encoding="utf-8",
                          filename=os.path.join(
                              os.path.dirname(__file__),
                              "../public/assets/template",
                              "index_template.html"))

    # Generate HTML from stored objects
    for post in posts:
        html_path = "{}.html".format(os.path.splitext(post.source_path)[0])
        with codecs.open(html_path, mode="w", encoding="utf-8") as fh2:
            fh2.write(tmpl_post.render(post=post))

    # Generate index file
    with codecs.open(filename=os.path.join(os.path.dirname(__file__), "../public/index.html"),
                     mode="w", encoding="utf-8")as fh3:
        posts = list(sorted(posts, key=lambda p: p.date, reverse=True))
        fh3.write(tmpl_index.render_unicode(posts=posts))
