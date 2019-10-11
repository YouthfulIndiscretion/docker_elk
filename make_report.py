from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from jinja2 import Template


def _read(path: Path) -> str:
    return path.read_text(encoding='utf8', errors='strict')


@dataclass
class Context:
    name: str
    dockerfile: str = field(init=False)
    config: str = field(init=False)

    @property
    def _path(self) -> Path:
        return Path(HERE, self.name)

    @property
    def _config_dir(self) -> Path:
        return Path(self._path, 'config')

    def __post_init__(self):
        self.dockerfile = _read(Path(self._path, 'Dockerfile'))
        self.config = _read(Path(self._config_dir, f'{self.name}.yml'))


HERE = Path('.').absolute()
TEMPLATE_PATH = Path(HERE, 'report.template.md')

DOCKER_COMPOSE_FILE = Path(HERE, 'docker-compose.yml')


def read_template_as_text() -> str:
    return _read(TEMPLATE_PATH)


def get_template() -> Template:
    return Template(read_template_as_text())


if __name__ == '__main__':
    elasticsearch = Context('elasticsearch')
    logstash = Context('logstash')
    kibana = Context('kibana')
    metricbeat = Context('metricbeat')
    template = get_template()
    dockercompose = _read(DOCKER_COMPOSE_FILE)
    output = template.render(**locals())
    Path(HERE, 'report.output.md').write_text(output)
    # print(read_template_as_text())
