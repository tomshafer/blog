# Custom Blog Engine

I want a static blog engine that processes Markdown files in place, applies a templating system, and spits out a basic static blog directory. Presently the engine is based on the following stack:

- Python 3.6 ([format string literals!][py36])
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

I would like to use, e.g., `cmark-gfm` ([link][cmark-gfm]) as the Markdown parser, but syntax highlighting seems challenging at the moment. I don't want to require a JavaScript library to highlight code blocks.

## Requirements

1. Render Markdown as HTML via simple templates.
2. Be fast about it.
3. Code syntax highlighting.
4. MathJax or equivalent. I want to be able to use mathematics.


[cmark-gfm]: https://github.com/github/cmark/
[docopt]: https://github.com/docopt/docopt
[Mako]: http://www.makotemplates.org
[py36]: https://docs.python.org/3/whatsnew/3.6.html
[Markdown]: https://pypi.python.org/pypi/Markdown
