# Exercice 10

## Instructions

Install the ELK stack on different VMs.

Setup up beats to populate the log.

Automate the install using Ansible.

Since this does not represent anything new compared to what we have done before,
and with approbation of the instructor, I will build the stack using Docker instead
of VMs + Ansible.

## Initial setup & requirements

Any machine with a working Docker daemon (although Windows will probably requires a bit
if shenaniganning around).

## Design

### Sourcing

Elastic offers a *lot* of [official docker images](https://www.docker.elastic.co/).

Since the exercise requires we use 7.1.x, I'll use the 7.1.1 family for all containers:

- ./elasticsearch/Dockerfile
  > FROM docker.elastic.co/elasticsearch/elasticsearch:7.1.1

- ./logstash/Dockerfile
  > FROM docker.elastic.co/logstash/logstash:7.1.1

- ./kibana/Dockerfile
  > FROM docker.elastic.co/kibana/kibana:7.1.1

### Basic config

All usage of `xpack` has beens tripped for simplicity's sake.

- ./elasticsearch/config/elasticsearch.yml
```markdown
---
## Default Elasticsearch configuration from Elasticsearch base image.
## https://github.com/elastic/elasticsearch/blob/master/distribution/docker/src/docker/config/elasticsearch.yml
#
cluster.name: "docker-cluster"
network.host: 0.0.0.0

## Use single node discovery in order to disable production mode and avoid bootstrap checks
## see https://www.elastic.co/guide/en/elasticsearch/reference/current/bootstrap-checks.html
#
discovery.type: single-node

## X-Pack settings
## see https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-xpack.html
#
#xpack.license.self_generated.type: trial
#xpack.security.enabled: true
#xpack.monitoring.collection.enabled: true

```

- ./logstash/config/logstash.yml
```markdown
---
## Default Logstash configuration from Logstash base image.
## https://github.com/elastic/logstash/blob/master/docker/data/logstash/config/logstash-full.yml
#
http.host: "0.0.0.0"

```

- ./kibana/config/kibana.yml
```markdown
---
## Default Kibana configuration from Kibana base image.
## https://github.com/elastic/kibana/blob/master/src/dev/build/tasks/os_packages/docker_generator/templates/kibana_yml.template.js
#
server.name: kibana
server.host: "0"
elasticsearch.hosts: [ "http://elasticsearch:9200" ]

```
  
### Basic `Dockerfile` for services

- ./elasticsearch/Dockerfile
```markdown
# https://github.com/elastic/elasticsearch-docker
FROM docker.elastic.co/elasticsearch/elasticsearch:7.1.1

# Add your elasticsearch plugins setup here
# Example: RUN elasticsearch-plugin install analysis-icu

```

- ./logstash/Dockerfile
```markdown
# https://github.com/elastic/logstash-docker
FROM docker.elastic.co/logstash/logstash:7.1.1

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json

```

- ./kibana/Dockerfile
```markdown
# https://github.com/elastic/kibana-docker
FROM docker.elastic.co/kibana/kibana:7.1.1

# Add your kibana plugins setup here
# Example: RUN kibana-plugin install <name|url>

```

### Basic `docker-compose.yml`

There is an alternative configuration for running in a Docker swarm
activated environment, providing additional safeties by spawning
Elasticsearch in master/slave mode, with at least 3 nodes running at
any given time. The Docker swarm orchestrator is smart enough to
distribute those nodes across multiple machines in the swarm.

```markdown
version: '3.2'

services:
#  elasticsearch_master:
#    build:
#      context: elasticsearch/
#    ports:
#      - 9200:9200
#      - 9300:9300
#    environment:
#      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
#    volumes:
#      - type: bind
#        source: ./elasticsearch/config/master.yml
#        target: /usr/share/elasticsearch/config/elasticsearch.yml
#        read_only: true
#      - type: volume
#        source: elasticsearch_master
#        target: /usr/share/elasticsearch/data
#    networks:
#      - elk
#  elasticsearch_slave:
#    image: elasticsearch:7.1.1
#    ## Deploy will only work in a Docker swarm:
#    ## use: `docker stack deploy` instead of docker-compose
#    # deploy:
#    #  replicas: 2
#    volumes:
#        - type: bind
#          source: ./elasticsearch/config/slave.yml
#          target: /usr/share/elasticsearch/config/elasticsearch.yml
#          read_only: true
#        - type: volume
#          source: elasticsearch_slave
#          target: /usr/share/elasticsearch/data
#    networks:
#      - elk
#    environment:
#      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"

  elasticsearch:
    build:
      context: elasticsearch/
    volumes:
      - type: bind
        source: ./elasticsearch/config/elasticsearch.yml
        target: /usr/share/elasticsearch/config/elasticsearch.yml
        read_only: true
      - type: volume
        source: elasticsearch
        target: /usr/share/elasticsearch/data
    ports:
      - "9200:9200"
      - "9300:9300"
    environment:
      ES_JAVA_OPTS: "-Xmx512m -Xms512m"
    networks:
      - elk

  logstash:
    build:
      context: logstash/
    volumes:
      - type: bind
        source: ./logstash/config/logstash.yml
        target: /usr/share/logstash/config/logstash.yml
        read_only: true
      - type: bind
        source: ./logstash/pipeline
        target: /usr/share/logstash/pipeline
        read_only: true
    ports:
      - "5000:5000"
      - "9600:9600"
    environment:
      LS_JAVA_OPTS: "-Xmx256m -Xms256m"
    networks:
      - elk
    depends_on:
      - elasticsearch

  kibana:
    build:
      context: kibana/
    volumes:
      - type: bind
        source: ./kibana/config/kibana.yml
        target: /usr/share/kibana/config/kibana.yml
        read_only: true
    ports:
      - "5601:5601"
    networks:
      - elk
    depends_on:
      - elasticsearch

  metricbeat:
    build:
      context: metricbeat/
    volumes:
      - type: bind
        source: /var/run/docker.sock
        target: /var/run/docker.sock
        read_only: true
      - type: bind
        source: /
        target: /hostfs
        read_only: true
      - type: bind
        source: ./metricbeat/config/metricbeat.yml
        target: /usr/share/metricbeat/metricbeat.yml
        read_only: true
    networks:
      - elk
    depends_on:
      - elasticsearch

  packetbeat:
    build:
      context: packetbeat/
    volumes:
      - type: bind
        source: ./packetbeat/config/packetbeat.yml
        target: /usr/share/packetbeat/packetbeat.yml
        read_only: true
#    networks:
#      - elk
    network_mode: "host"
    depends_on:
      - elasticsearch
    cap_add:
      - NET_ADMIN
      - NET_RAW


networks:
  elk:
    driver: bridge
    # This to allow packetbeat to capture host traffic
#    external: true

volumes:
  elasticsearch:
  # elasticsearch_master:
  # elasticsearch_slave:

```

This very basic setup gives us three concurrently running containers,
placed on their own little private virtual network, and exposing all
relevant ports to the host machine.

## Onward

What's left to do now is to generate some noise to log, namely:

- packetbeat

- metribeat

Fairly straightforward by now:

- ./metricbeat/config/metricbeat.yml
```markdown
metricbeat.config:
  modules:
    path: ${path.config}/modules.d/*.yml
    # Reload module configs as they change:
    reload.enabled: true

metricbeat.autodiscover:
  providers:
    - type: docker
      hints.enabled: true

metricbeat.modules:
- module: docker
  metricsets:
    - "container"
    - "cpu"
    - "diskio"
    - "healthcheck"
    - "info"
    - "memory"
    - "network"
  hosts: ["unix:///var/run/docker.sock"]
  period: 10s
  enabled: true

processors:
  - add_cloud_metadata: ~

output.elasticsearch:
  hosts: 'elasticsearch:9200'

```

- ./metricbeat/Dockerfile
```markdown
FROM docker.elastic.co/beats/metricbeat:7.1.1


```

- ./packetbeat/config/packetbeat.yml
```markdown
packetbeat.interfaces.device: any

packetbeat.flows:
  timeout: 30s
  period: 10s

packetbeat.protocols.icmp:
  enabled: true

packetbeat.protocols.dns:
  ports: [53]
  include_authorities: true
  include_additionals: true

packetbeat.protocols.http:
  ports: [80, 5601, 9200, 8080, 8081, 5000, 8002]

packetbeat.protocols.memcache:
  ports: [11211]

packetbeat.protocols.mysql:
  ports: [3306]

packetbeat.protocols.pgsql:
  ports: [5432]

packetbeat.protocols.redis:
  ports: [6379]

packetbeat.protocols.thrift:
  ports: [9090]

packetbeat.protocols.mongodb:
  ports: [27017]

packetbeat.protocols.cassandra:
  ports: [9042]

processors:
- add_cloud_metadata: ~

output.elasticsearch:
  hosts: '127.0.0.1:9200'

```

- ./packetbeat/Dockerfile
```markdown
# https://github.com/elastic/logstash-docker
FROM docker.elastic.co/beats/packetbeat:7.1.1

# Add your logstash plugins setup here
# Example: RUN logstash-plugin install logstash-filter-json

```

The only difference here is that we want `packetbeat` on the host
network, not on the private virtual  Docker network:

```markdown
...
#    networks:
#      - elk
    network_mode: "host"
    depends_on:
      - elasticsearch
    cap_add:
      - NET_ADMIN
      - NET_RAW
...
```

