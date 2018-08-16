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
import json
import os
import re
from collections import namedtuple
from datetime import datetime

import markdown
import pytz
from dateutil.parser import parse as parse_date
from docopt import docopt
from mako.template import Template


################################################################################
## Global configuration
################################################################################
conf = namedtuple("conf", ("url_base", "url_site_base",
                           "local_base", "local_tmpl_base"))

conf.url_base = "/blog"
conf.url_site_base = "/"
# local_base is assigned at runtime as the local root of the blog
conf.local_base = None
conf.local_tmpl_base = os.path.expanduser("~/Sites/Personal/2017/assets/template")


def find_files(base_dir, extensions=("md",)):
    """Walk 'base_dir' and return files with the listed extensions."""
    print(base_dir, extensions)
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in filenames:
            if os.path.splitext(fname)[-1].lower().lstrip(".") in extensions:
                yield os.path.join(dirpath, fname)

def render_rss_feed(template, posts):
    """
    Render an XML file from posts and a template.

    The only extra information needed are the :config: dict and
    the curent time in UTC.
    """
    return template.render_unicode(
        posts=posts, config=conf, build_date=datetime.now(tz=pytz.utc))

def render_json_feed(template, posts):
    """
    Render an XML file from posts and a template.

    The only extra information needed are the :config: dict and
    the curent time in UTC.
    """
    return template.render_unicode(
        posts=posts, config=conf, build_date=datetime.now(tz=pytz.utc))

class Post(object):
    """
    Simple representation of a blog post.

    date:        Datetime object
    json_html:   Sanitized HTML for JSON
    html:        Parsed HTML
    slug:        Path to post relative to the blog root
    source:      Raw Markdown
    source_path: Full (local) path to source file
    title:       Title from the metadata
    """
    title, date, source, html, source_path, slug = 6*[None]

    def __init__(self, file_path, md_parser):
        """Use 'md_parser' to parse 'file_path' into an object."""
        with codecs.open(file_path, mode="r", encoding="utf-8") as fh:
            self.source_path = file_path
            self.slug = self.make_slug(file_path)
            self.source = fh.read()
            self.html = md_parser.convert(self.source)
            self.json_html = json.dumps(self.html)

            # Assign meta, requiring title and date
            meta = md_parser.Meta
            self.title = self.unquote(meta["title"][0])
            # localize() intelligently adds DST/timezone info to naive dates
            self.date = pytz.timezone("US/Eastern").localize(
                parse_date(self.unquote(meta["date"][0])), is_dst=None)

    @staticmethod
    def unquote(string):
        """
        Remove quotes from the beginning/end of a string.

        Markdown metadata often appears as key: "value", but Python Markdown
        will not remove the quotes.
        """
        return re.sub(r"(^['\"]|['\"]$)", "", string)

    @staticmethod
    def make_slug(source_path):
        """
        Take the source path and make a post slug using the format
            '<path rel to blog root>.html'.

        Uses the conf global.
        """
        relpath = os.path.relpath(source_path, conf.local_base)
        return "{}".format(os.path.splitext(relpath)[0])


if __name__ == '__main__':
    cli_args = docopt(__doc__)
    conf.local_base = cli_args['PUBLIC_DIR']

    # Find Markdown files
    md_extensions = ('md', 'mdown', 'text')
    md_files = tuple(find_files(conf.local_base, md_extensions))
    if not md_files:
        quit('No markdown files found.')

    # Initialize the parser
    parser = markdown.Markdown(
        output_format='html5',
        extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.footnotes',
            'markdown.extensions.tables',
            'markdown.extensions.codehilite',
            'markdown.extensions.meta',
            'markdown.extensions.smarty',
            'mdx_math'
        ],
        extension_configs={
            'markdown.extensions.footnotes': {
                'UNIQUE_IDS': True,
                # https://github.com/jekyll/jekyll/issues/3751#issue-83081590
                'BACKLINK_TEXT': '&#8617;&#xfe0e;'
            },
            'markdown.extensions.codehilite': {
                'use_pygments': True
            },
            'mdx_math': {
                'enable_dollar_delimiter': True
            }
        })

    # Generate a large list of post objects
    posts = []
    for filename in md_files:
        posts.append(Post(filename, parser))
        parser.reset()
    posts = list(sorted(posts, key=lambda p: p.date, reverse=True))

    # Load templates
    tmpl_post = Template(
        input_encoding='utf-8',
        filename=os.path.join(conf.local_tmpl_base, 'blog_post_template.html'))

    tmpl_index = Template(
        input_encoding='utf-8',
        filename=os.path.join(conf.local_tmpl_base, 'blog_index_template.html'))

    tmpl_archive= Template(
        input_encoding='utf-8',
        filename=os.path.join(conf.local_tmpl_base, 'blog_archive_template.html'))

    # Generate HTML from stored objects
    for post in posts:
        html_path = '{}.html'.format(os.path.splitext(post.source_path)[0])
        with codecs.open(html_path, 'w', 'utf-8') as fh:
            fh.write(tmpl_post.render(post=post, conf=conf))

    # Generate index file at base of blog root
    with codecs.open(os.path.join(conf.local_base, 'index.html'), 'w', 'utf-8')as fh:
        fh.write(tmpl_index.render_unicode(posts=posts, conf=conf))

    # Year and month archives
    for yr in set(p.date.year for p in posts):
        year_posts = list(filter(lambda p: p.date.year == yr, posts))
        with codecs.open(os.path.join(conf.local_base, f'{yr}/index.html'), 'w', 'utf-8')as fh:
            fh.write(tmpl_archive.render_unicode(posts=year_posts, conf=conf, archive_title=f'{yr}'))
        for mn in set(p.date.month for p in year_posts):
            month_posts = list(filter(lambda p: p.date.month == mn, year_posts))
            with codecs.open(
                    os.path.join(conf.local_base, '{year}/{month:02d}/index.html'.format(year=yr, month=mn)),
                    "w", "utf-8")as fh:
                fh.write(tmpl_archive.render_unicode(
                    posts=month_posts,
                    conf=conf,
                    archive_title='{}'.format(month_posts[0].date.strftime('%B %Y'))))

    # Month archives
    for yr_mon in set(p.date.strftime('%B %Y') for p in posts):
        year_mon_posts = filter(lambda p: p.date.strftime('%B %Y') == yr_mon, posts)


    # Mutate posts, rewriting /blog/ URLs with the full domain name
    for post in posts:
        post.html = re.sub(r'([\'"])/blog', r'\1https://tshafer.com/blog', post.html)
    
    # Generate RSS feed at the blog root
    with codecs.open(os.path.join(conf.local_base, 'rss.xml'), 'w', 'utf-8') as fh:
        template = Template(
            input_encoding='utf8',
            filename=os.path.join(conf.local_tmpl_base, 'rss.xml'))
        fh.write(render_rss_feed(template=template, posts=posts))

    # Generate JSON feed
    with codecs.open(os.path.join(conf.local_base, 'feed.json'), 'w', 'utf-8') as fh:
        template = Template(
            input_encoding='utf8',
            filename=os.path.join(conf.local_tmpl_base, 'feed.json'))
        fh.write(render_json_feed(template=template, posts=posts))
