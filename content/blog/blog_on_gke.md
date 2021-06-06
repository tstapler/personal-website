+++
title = "Blogging in style with Hugo and GKE: Part 1"
categories = [ "Kubernetes" ]
tags = ["gcp", "gke" ,"kubernetes", "hugo", "terraform"]
draft = true
+++

Do you run your blog like it's 1999? FTP and GoDaddy your best friends? Well today, we're going to bring you into the new millennium. At the end of this series you'll be writing in style using the hottest technologies like, Kubernetes, Hugo, and Terraform.

I'm writing this guide on linux, so to follow along, you can install it yourself! :) or you can download the awesome WSL TODO: Add WSL link to get many of these tools for Windows. 

To get started we need to do a couple of things:

* Create (or Use an existing) Google Account
* [Setup Google Cloud SDK](https://cloud.google.com/sdk/install)
* [Setup a Google Cloud service account](https://cloud.google.com/docs/authentication/getting-started)
* [Install Hugo](https://gohugo.io/getting-started/installing/)
* [Setup Terraform](+)
* [Install Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

TODO: Give github repo with project resources

## First things first - Hugo

The Hugo project [sums up](https://gohugo.io/about/what-is-hugo/) how it works pretty well.

> Hugo is a fast and modern static site generator written in Go, and designed to make website creation fun again.

You might wonder: "Why should I use Hugo, everyone else is using Wordpress"

Again, the Hugo project sums up the benefits of a static site generator pretty well.

> Improved performance, security and ease of use are just a few of the reasons static site generators are so appealing.

If you want more information just checkout [Hugo's website](https://gohugo.io/about/benefits/).


Let's get started by creating your blog. This content is branch off of surprise [The Hugo quick-start guide](https://gohugo.io/getting-started/quick-start/).

Everyone needs a good resume site which sums them up. We'll be building a site that serves as a personal resume.

Start out with generating necessary files with the `hugo new site` command

```
$ hugo new site hot-blog
Congratulations! Your new Hugo site is created in /home/tstapler/Programming/hot-blog.

Just a few more steps and you're ready to go:

1. Download a theme into the same-named folder.
   Choose a theme from https://themes.gohugo.io/, or
   create your own with the "hugo new theme <THEMENAME>" command.
2. Perhaps you want to add some content. You can add single files
   with "hugo new <SECTIONNAME>/<FILENAME>.<FORMAT>".
3. Start the built-in live server via "hugo server".

Visit https://gohugo.io/ for quickstart guide and full documentation.
```


## Put it in the cloud - Google Code Build

## Is your server running? You should catch it - GKE


You need to create a billing account on GCP in order to use GKE. This will enable useage of the apis

Create a service account:
```
$ gcloud iam service-accounts create bloggymcblogface
```

Give it permissions to access your account
```
$ gcloud projects add-iam-policy-binding blog-blog --member "serviceAccount:bloggymcblogface@blog-blog.iam.gserviceaccount.com" --role "roles/owner"
Updated IAM policy for project [blog-blog].
bindings:
- members:
  - serviceAccount:bloggymcblogface@blog-blog.iam.gserviceaccount.com
  - user:tystapler@gmail.com
  role: roles/owner
etag: BwV-mdOo4Xc=
version: 1
```

Generate a key file
```
$ gcloud iam service-accounts keys create keyfile.json --iam-account bloggymcblogface@blog-blog.iam.gserviceaccount.com
```

Once you have all of the pre-requisites set up, you'll need to spin up your very own Kubernetes cluster. Terraform makes it very easy to do this.

Terraform is a declarative configuration language which means it will create cloud resources from your configuration files.


Here's a sample Terraform file:
```
TODO: Sample terraform file
```

```shell
$ terraform apply
```

Now we're going to deploy your blog!

First get your Kubernetes 

If you stop for any period of time you might have to run `gcloud auth login` to get your credentials again.

Once your cluster is running, you'll need to find your instance and set a static ip. A static IP will ensure that we can point your domain at your blog. https://cloud.google.com/network-tiers/docs/using-network-service-tiers#creating_static_external_addresses

If you want to tear down your cluster (and save a little bit of cash) run `terraform delete`
