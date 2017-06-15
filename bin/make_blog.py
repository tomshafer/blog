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
from collections import namedtuple
from dateutil.parser import parse as parse_date
import markdown
from docopt import docopt
from mako.template import Template


conf = namedtuple("conf", ("url_base", "url_site_base", "local_base",
                           "local_tmpl_base"))

conf.url_base = "/blog"
conf.url_site_base = "/"
conf.local_base = None
conf.local_tmpl_base = os.path.expanduser("~/Sites/Personal/2017/assets/template")


def find_files(base_dir, extensions=("md",)):
    """Walk 'base_dir' and return files with extensions in 'extensions'."""
    print(base_dir, extensions)
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in filenames:
            if os.path.splitext(fname)[-1].lower().lstrip(".") in extensions:
                yield os.path.join(dirpath, fname)


class Post(object):
    """
    Simple representation of a blog post.

    source:      Raw Markdown
    source_path: Full path to source file
    html:        Parsed HTML
    title:       Title from the metadata
    date:        Datetime object
    slug:        Path to post relative to the blog root
    """
    title, date, source, html, source_path, slug = 6*[None]

    def __init__(self, file_path, md_parser):
        """Use 'md_parser' to parse 'file_path' into an object."""
        with codecs.open(file_path, mode="r", encoding="utf-8") as fh:
            self.source_path = file_path
            self.slug = self.make_slug(file_path)
            self.source = fh.read()
            self.html = md_parser.convert(self.source)
            # Assign meta, requiring title and date
            meta = md_parser.Meta
            self.title = self.unquote(meta["title"][0])
            self.date = parse_date(self.unquote(meta["date"][0]))

    @staticmethod
    def unquote(string):
        """Remove quotes from the beginning/end of a string."""
        return re.sub(r"(^['\"]|['\"]$)", "", string)

    @staticmethod
    def make_slug(source_path):
        """
        Take the source path and make a post slug using the format
            '<path rel to blog root>.html'.

        Uses the conf global.
        """
        relpath = os.path.relpath(source_path, conf.local_base)
        return "{}.html".format(os.path.splitext(relpath)[0])


if __name__ == "__main__":
    cli_args = docopt(__doc__)
    conf.local_base = cli_args["PUBLIC_DIR"]

    # Find Markdown files
    md_extensions = ("md", "mdown", "text")
    md_files = tuple(find_files(conf.local_base, md_extensions))
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
                             conf.local_tmpl_base, "blog_post_template.html"))
    tmpl_index = Template(input_encoding="utf-8",
                          filename=os.path.join(
                              conf.local_tmpl_base, "blog_index_template.html"))

    # Generate HTML from stored objects
    for post in posts:
        html_path = "{}.html".format(os.path.splitext(post.source_path)[0])
        with codecs.open(html_path, mode="w", encoding="utf-8") as fh2:
            fh2.write(tmpl_post.render(post=post, conf=conf))

    # Generate index file at base of blog root
    with codecs.open(filename=os.path.join(conf.local_base, "index.html"),
                     mode="w", encoding="utf-8")as fh3:
        posts = list(sorted(posts, key=lambda p: p.date, reverse=True))
        fh3.write(tmpl_index.render_unicode(posts=posts, conf=conf))
