#!/usr/bin/env bash
docker run docker.elastic.co/beats/metricbeat:7.1.1 setup -E setup.kibana.host=kibana:5601 -E output.elasticsearch.hosts=["elasticsearch:9200"]
