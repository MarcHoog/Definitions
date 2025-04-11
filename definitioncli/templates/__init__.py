from jinja2 import Environment, PackageLoader


def get_jinja2_env():
    env = Environment(loader=PackageLoader("definitioncli", "templates"))
    return env
