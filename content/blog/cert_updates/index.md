
+++ 
title = "Time flies when you're running Kubernetes"
categories = ["Kubernetes", "Home Lab"]
tags = ["ceph", "kubernetes", "certs", "kubeadm"]
draft = true 
date = "20/08/2019"
+++

Have you ever come home to lights that won't turn on? Typically, the
problem lies with your power company, or the [Phoebus
Cartel](https://en.wikipedia.org/wiki/Phoebus_cartel). A few weeks ago I
was confronted with this frustrating situation. The culprit was my
Kubernetes cluster.

I've been running Kubernetes at home for about three years now. You can
read about my cluster in [another post]({{< ref"/blog/kubernetes_with_kubespray" >}}). Since I've setup my cluster,
the Kubernetes deployment landscape has changed. The new recommended
method for bootstrapping clusters is using
[kubeadm](https://github.com/kubernetes/kubeadm/tree/19b63e043e1bd1276cf8470c7ef71952d0b2616a#what-is-kubeadm-).
The higher level tools such as
[kops](https://github.com/kubernetes/kops) and
[kubespray](https://github.com/kubernetes-sigs/kubespray) (What I use)
now use kubeadm for low level cluster management. With kubeadm taking
care of basic cluster management, frameworks are able to add 
features beyond setting up a cluster.

Before kubeadm, kubespray had to manage Kubernetes certificates.
Mid 2019 I was able to upgrade my Kubernetes cluster from version
`1.12.x` to `1.14.x`. For reasons unknown to me, I was unable to
make the jump from `1.14.x` to `1.15.x`. 

The next year, I stayed on `1.14`. There wasn't anything wrong with the version. After all, I was still ahead of EKS's release cycle (The EKS team eventually caught up).


{{< image src="still_waiting.jpg" height="300" >}}

But, one day, I was unable to connect to my Kubernetes cluster.

The funny part is that I started writing this blog post in 2019, but I peetered out because I had neglected to write down the steps I took to fix the cluster. Now it's 2025 and I'm hitting the same problem, but this time I have the powers of Personal Knowledge Management (PKM) on my side. Checkout my other blogpost
