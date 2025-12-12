import os
import re
import sys
import glob
import subprocess
import tomllib
from typing import Any

EPICLANG_DOTFILE = '.epiclang'
EPICLANG_PLUGINS_DIRS = [
    '/usr/lib/epiclang/plugins',
    '/usr/local/lib/epiclang/plugins',
]
BASE_COMMAND = 'clang'


class EpiclangConfig:

    def __init__(self, toml_config: dict[str, Any]):
        self.plugins_config: dict[str, dict[str, str]] = {}
        if 'plugins' in toml_config:
            for plugin, config in toml_config['plugins'].items():
                if type(config) != dict:
                    raise ValueError(f'{plugin} is not a table')
                self.plugins_config[plugin] = {}
                for key, value in config.items():
                    if type(value) != str:
                        raise ValueError(
                            f'{plugin}.{key} value must be a string')
                    self.plugins_config[plugin][key] = value

    def get_config_for_plugin(self, plugin: str) -> dict[str, str] | None:
        return self.plugins_config.get(plugin)


def find_epiclang_dotfile() -> str | None:
    current_dir = os.getcwd()
    while True:
        if os.path.exists(os.path.join(current_dir, EPICLANG_DOTFILE)):
            return os.path.join(current_dir, EPICLANG_DOTFILE)
        if current_dir == '/':
            break
        current_dir = os.path.dirname(current_dir)
    return None


def load_epiclang_dotfile() -> EpiclangConfig | None:
    dotfile_path = find_epiclang_dotfile()
    if dotfile_path is None:
        return None

    dotfile_content: EpiclangConfig | None = None
    try:
        with open(dotfile_path, 'rb') as dotfile:
            toml_content = tomllib.load(dotfile)
            dotfile_content = EpiclangConfig(toml_content)
    except tomllib.TOMLDecodeError as e:
        print(
            f'Error while loading .epiclang, ignoring it: {e}', file=sys.stderr)
    return dotfile_content


PLUGIN_NAME_REGEX = re.compile(r'.*/\w+-plugin-(\w+)\.so')


def get_plugin_name_from_path(path: str) -> str | None:
    fm = PLUGIN_NAME_REGEX.fullmatch(path)
    if not fm:
        return None
    return fm.group(1)


def main():
    epiclang_dotfile = load_epiclang_dotfile()
    final_command = [BASE_COMMAND]

    for plugins_dir in EPICLANG_PLUGINS_DIRS:
        if os.path.exists(plugins_dir):
            for plugin in glob.glob(os.path.join(plugins_dir, '*.so')):
                if os.path.isfile(plugin):
                    final_command.extend([f'-fplugin={plugin}'])
                    if epiclang_dotfile:
                        plugin_name = get_plugin_name_from_path(plugin)
                        plugin_config = epiclang_dotfile.get_config_for_plugin(
                            plugin_name)
                        if plugin_config:
                            for key, value in plugin_config.items():
                                final_command.extend(
                                    [f'-fplugin-arg-{plugin_name}-{key}={value}'])

    final_command.extend(sys.argv[1:])

    try:
        subprocess.run(final_command, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except FileNotFoundError:
        print(f"Error: {BASE_COMMAND} not found in PATH", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
