+++ 
title = "My Kubernetes Home Lab"
description = "Step-by-step guide to building an enterprise-grade Kubernetes cluster at home using Kubespray, Ceph distributed storage, and Tinc VPN networking"
summary = "From hardware selection to production deployment - learn how to create a resilient Kubernetes cluster using consumer hardware and open source tooling"
categories = [ "Kubernetes", "Home Lab"]
tags = ["ansible", "kubernetes", "ceph", "tinc", "homelab", "infrastructure", "devops", "distributed-systems", "storage", "networking"]
keywords = ["kubernetes cluster setup", "kubespray ansible tutorial", "ceph storage cluster", "tinc vpn configuration", "home server kubernetes", "distributed systems networking"]
date = "12/08/2019"

# Template comments for future posts:
# description = "Focus on specific technical implementation and outcomes"
# summary = "Highlight the unique aspects (consumer hardware, production-grade)"
# tags = Use existing category hierarchy where possible
# keywords = Include both specific technologies and use case terms
+++

[Kubernetes](https://kubernetes.io/) is a highly modular container
platform open sourced by Google. Google modeled Kubernetes after
[Borg](https://ai.google/research/pubs/pub43438), the container platform
that has powered Google services for over 10 years. My current company,
[Workiva](https://www.workiva.com/careers), now uses Kubernetes to run
thousands of microservices on AWS. This blog post will walk through how
anyone can run a powerful Kubernetes cluster out of their home.

## The Dream

Workiva evaluated using Kubernetes to power its infrastructure
platform in 2017. The team decided against adopting it right away, but
the project sparked my interest Kubernetes. Programming
projects have always been a way for me to learn new concepts and sharpen
my programming skills. In the past I didn't always share these projects with the world. Hosting web apps can be expensive and
complicated to manage. Figuring out hosting didn't feel worth the effort for a toy
problem. After learning more about Kubernetes, I was inspired to build a 
cluster which could host my programming projects and other fun software.

## Hardware

I consider myself a computer enthusiast, and I used to be an avid gamer. From my past gaming, I have old computer hardware laying around. One of
Kubernetes' design goals it to make it easy to run many web applications on cheap consumer hardware. This paradigm fit well with my
ragtag group of desktops. One of my machines has a i7 Ivy Bridge CPU (8 cores) and
32 GB of ram and the other has an AMD A8-7600 (4 cores) and 16GB of ram. Once I
installed Ubuntu on the two computers I had the beginnings of a
Kubernetes cluster. What I lacked was a static IP for incoming traffic. I wanted to point my domains at a more stable network connection than whatever apartment I happened to live in. After surveying a couple of hosting providers, I settled on a 2 core 4GB of ram VPS from Vultr which costs me 20 dollars a month. 16 cpu cores, and 52 GB of ram split across three nodes would be plenty of hardware to run a modest Kubernetes cluster.

{{< image src="cluster_diagram.png" >}}

## Installation - Kubespray

I've used [Ansible](https://www.ansible.com/) to provision computers for long
time. I have a github repo which contains my custom made ansible modules and playbooks for bootstrapping a dev machine. Since I was already 
using Ansible to provision other machines, it made sense
to provision my Kubernetes cluster the same way.
[Kubespray](https://github.com/kubespray/kubespray) is a project which
automates creating Kubernetes clusters using Ansible scripts. It handles creating your master and worker nodes. In addtion it can install 3rd
party nicities such as nginx for ingress and certificate provider.
Since I had 3 nodes, I couldn't follow the best practice of separating
my worker nodes from masters. I ended up designating all three nodes as
masters and letting workloads run on the worker nodes in my apartment.

## Networking

Kubernetes master nodes need to communicate directly to each other; You should not expose them to the internet directly either. To facilitate this communication, I decided to run a Mesh
network between my nodes which would allow them direct private
communication. An added benefit to this network is that I can connect
to my nodes from my laptop from anywhere. I used the mesh network [Tinc](https://www.tinc-vpn.org/),
because of its ease of configuration via Ansible and because it provided the low
level networking connection I wanted. One of the downsides of Tinc is that the application is
single threaded. It runs in Linux kernel Userspace meaning that it uses a lot of CPU
at higher throughputs. When I started this project, 
[Wireguard](https://www.wireguard.com/) was still not a mature product. I will eventually migrate
to using it. Wireguard runs as part of the linux kernel so it can be much more performant than Tinc. The Wireguard team is trying to have it included in Linux by default so it could be even easier to set up in the future.

## Storage

For stateless workloads, Kubernetes doesn't require much 
storage space. However, I wanted to run applications like Plex, and Home
Assistant which are stateful and intended to be run on one computer. Kubernetes includes
a concept called "persistant volumes" to handle cases like this. Using
persistant volumes, Kubernetes containers have access to the correct 
files regardless of which node they are started on. During my search, I
evaluated several options for implementing persistent volumes. The top
contenders were [Ceph](https://ceph.io/),
[GlusterFS](https://www.gluster.org/), and good ol'
[NFS](https://en.wikipedia.org/wiki/Network_File_System). GlusterFS
wouldn't install for some reason I couldn't understand, and NFS had some
drawbacks like the lack of file locking. In the end I ended up going with Ceph.

What Ceph does and how to run a cluster could be the subject of another
blog post but I'll try to breifly explain what it is and how it works.
Ceph is a distributed filesystem, It forms a cluster with many nodes and
stores your data across them in a durable way. Think of it like
distributed [RAID](https://en.wikipedia.org/wiki/RAID).
Ceph requires at least three nodes and at maximum 1GB of Ram for each TB
of usable storage, so RAM is actually my limiting factor. If you ever
start to run out of space, you can add nodes to the Ceph cluster and it
will automatically rebalance your data across the cluster. Once Ceph is
set up you can expose its storage as a raw block device like a hard
disk, object storage (like AWS S3), or a Filesystem (what I needed the
most). Ceph's filesystem is accessable over the network after installing
the write kernel drivers so I'd be able to directly move files to it
from my laptop or any of my other devices provied that I'm connected to
my mesh network.

Outside of Kubernetes, I wanted to use Ceph for storing full disk
backups of my machines using [Borg
Backup](https://borgbackup.readthedocs.io/en/stable/) and
[Borgmatic](https://github.com/witten/borgmatic), my movie collection,
all of my pictures, and anything else I could need from anywhere. There
are endless usecases for large file storage so I didn't want to be
limited by my hardware. I bought 12 4TB drives as storage for the ceph
cluster and went to work adding them to my nodes.

## Final Product

After a few months of research, amazon packages, and a vpn
misconfiguration which made my hair gray, I had a solid Kubernetes
cluster fit for any enterprise. I've continually added more applications
over time, and the cluster is able to handle my changing requirements at
the drop of a hat. I deploy services to my cluster using
[Helm](https://helm.sh/), I keep my helm charts in [this
repo](https://github.com/tstapler/charts). Building my cluster was a
blast! I whole heartedly encourage you to try it too.
