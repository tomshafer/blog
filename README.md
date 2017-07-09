Custom Blog Engine
==================

This repository houses a simple static blog engine that processes Markdown files, applies a templating system, and spits out a static blog in a directory. The engine is based on the following stack:

- [Python 3.6][py36]
    - [docopt][]: Maybe my favorite Python package
    - [Mako][]: Simple templating
    - [Markdown][]: Venerable Python Markdown implementation

This stack is simple to initialize:

```bash
> conda create -n python36 python=3.6 virtualenv
> source activate python36
> virtualenv venv
> source venv/bin/activate
> pip install docopt Mako Markdown
```

I wanted to use a fast C-based parser, e.g., `cmark-gfm` ([link][cmark-gfm]), but syntax highlighting looked difficult to implement without extra JavaScript libraries. Python Markdown is reasonably quick and includes a number of Markdown extensions (code highlighting, smart quotes, footnotes) out of the box.


Design Requirements
-------------------

1. Render Markdown as HTML via simple templates.
2. Be fast about it.
3. Allow code syntax highlighting.
4. Include MathJax or equivalent.


[cmark-gfm]: https://github.com/github/cmark/
[docopt]: https://github.com/docopt/docopt
[Mako]: http://www.makotemplates.org
[py36]: https://docs.python.org/3/whatsnew/3.6.html
[Markdown]: https://pypi.python.org/pypi/Markdown


Current Status & To-Do List
---------------------------

The engine works and already generates [my blog](https://tshafer.com/blog/).

Future upgrades and extensions:

- *Add better handling/factoring of configuration metadata.*  
    This could be handled by testing for a dotfile or a local config file.

- *Experiment with draft posts.*  
    This might be best implemented as a YAML post flag such that the engine renders the HTML but does not include the post in any indexes (e.g., index.html, rss.xml, feed.json).

- *Add better factoring of posts and template logic.*

- *Add logging and timing to the page generation.*

- *Add site generation and upload scripts to the repository.*

- *Add logic to convert relative links to full ones fir the index page and feeds.*
