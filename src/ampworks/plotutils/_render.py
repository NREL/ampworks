from pathlib import Path
from tempfile import NamedTemporaryFile


def _render_plotly(fig, figsize, save):

    from ampworks import _in_notebook
    from ampworks.plotutils._style import PLOTLY_CONFIG

    # Configure size, with optional responsiveness
    config = PLOTLY_CONFIG.copy()
    if figsize is not None:
        fig.update_layout(width=figsize[0], height=figsize[1])
        config['responsive'] = any([size is None for size in figsize])

    # Save or create temp file to display when not in notebook
    if save is not None:
        path = Path(save)
        if not path.suffix.lower() == '.html':
            path = path.with_suffix('.html')

        path.parent.mkdir(parents=True, exist_ok=True)

    else:
        tmp = NamedTemporaryFile(delete=False, suffix='.html')
        path = Path(tmp.name)
        tmp.close()

    # Optionally write to file, then display
    in_nb = _in_notebook()

    if (not in_nb) or (save is not None):
        auto_open = True if not in_nb else False
        fig.write_html(path, auto_open=auto_open, config=config)

    if in_nb:
        fig.show(config=config)
