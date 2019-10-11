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
{{ elasticsearch.config }}
```

- ./logstash/config/logstash.yml
```markdown
{{ logstash.config }}
```

- ./kibana/config/kibana.yml
```markdown
{{ kibana.config }}
```
  
### Basic `Dockerfile` for services

- ./elasticsearch/Dockerfile
```markdown
{{ elasticsearch.dockerfile }}
```

- ./logstash/Dockerfile
```markdown
{{ logstash.dockerfile }}
```

- ./kibana/Dockerfile
```markdown
{{ kibana.dockerfile }}
```

### Basic `docker-compose.yml`

There is an alternative configuration for running in a Docker swarm
activated environment, providing additional safeties by spawning
Elasticsearch in master/slave mode, with at least 3 nodes running at
any given time. The Docker swarm orchestrator is smart enough to
distribute those nodes across multiple machines in the swarm.

```markdown
{{ dockercompose }}
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
{{ metricbeat.config }}
```

- ./metricbeat/Dockerfile
```markdown
{{ metricbeat.dockerfile }}
```

- ./packetbeat/config/packetbeat.yml
```markdown
{{ packetbeat.config }}
```

- ./packetbeat/Dockerfile
```markdown
{{ packetbeat.dockerfile }}
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


