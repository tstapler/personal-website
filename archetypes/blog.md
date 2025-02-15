+++ 
# Required Fields
title = "{{ replace .Name "-" " " | title }}"  # Keep under 60 characters
description = ""  # 160 chars max for SEO, focus on primary keywords
summary = """"""  # 2-3 sentence teaser shown in listings

# Category/Tag Schema
categories = [ "Primary Category" ]  # Use existing categories from _index.md
tags = [ "existing-tag" ]  # Max 10, lowercase with hyphens

# SEO Optimization
keywords = [ "primary keyword", "long-tail variation" ]  # 5-8 phrases

# Optional Fields
date = {{ .Date.Format "2006-01-02" }}
draft = true  # Set to false when ready to publish
featured_image = "/img/your-image.jpg"  # Social sharing image

# Template Guidance (Remove before publishing)
# ------------------------------------------------------------------
# Description: Include 2-3 primary keywords naturally
# Categories: Check content/_index.md for existing taxonomy
# Tags: Prefer existing tags, use hyphen-case
# Keywords: Use semantic variations and common misspellings
# Featured Image: Use /img/... path from static directory
# 
# Example Good Frontmatter:
# title: "Automating Kubernetes Deployments"
# description: "Step-by-step guide to GitOps workflows with ArgoCD and Kustomize"
# categories = ["DevOps", "Cloud Native"]
# tags = ["kubernetes", "gitops", "argocd", "ci-cd"]
# keywords = ["kubernetes deployment", "argoCD tutorial", "gitops workflow"]
+++
