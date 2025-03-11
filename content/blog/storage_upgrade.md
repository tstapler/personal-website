+++
title = "Must construct additonal hard drives"
categories = [ "Kubernetes", "Ceph"]
tags = ["ceph", "kubernetes" ]
draft = true
date = "2020-02-08"
+++

# Overview

In 2023 my Ceph cluster reached max storage. I needed to add more storage to the cluster.

- Show graphs of the cluster in grafana
- Detail the process of using `ceph-deploy` to add a new osds to the cluster
- Talk about the harddrive selection process using PcPartPicker and a parametic filter for the best price per TB
- Talk about the monitoring in place on ceph using the prometheus exporter and grafna alerting to Discord
