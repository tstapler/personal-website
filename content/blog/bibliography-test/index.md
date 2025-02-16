+++
title = "Bibliography System Test"
date = "2025-02-16"
draft = true
+++

This post tests the new bibliography shortcode system{{< cite "ceph_paper" >}}.

{{< bibliography >}}
@article{ceph_paper,
  title = {Ceph: A Scalable, High-Performance Distributed File System},
  author = {Weil, Sage A. and Brandt, Scott A. and Miller, Ethan L. and Maltzahn, Carlos},
  year = {2006},
  journal = {OSDI'06: Seventh Symposium on Operating Systems Design and Implementation},
  url = {https://www.usenix.org/legacy/events/osdi06/tech/weil.html}
}

@book{kube_book,
  title = {Kubernetes: Up and Running},
  author = {Burns, Brendan and Beda, Joe and Hightower, Kelsey and others},
  year = {2022},
  publisher = {O'Reilly Media}
}
{{< /bibliography >}}
