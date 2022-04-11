from typing import Any, Dict, Optional
import jinja2
from jinja2 import StrictUndefined


def render_from_template(
    template_name: str,
    context_dict: Optional[Dict[str, Any]] = None,
    globals_dict: Optional[Dict[str, Any]] = None,
) -> str:
    env = jinja2.Environment(
        loader=jinja2.PackageLoader("resources", "templates"),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    tmpl = env.get_template(template_name)
    tmpl.globals.update(globals_dict)
    return tmpl.render(context_dict or {})
