+++
title = "Beating Powerline Interference with MoCA (The Powerline Effect)"
description = "Discover how halogen lighting interference crippled my powerline network and how MoCA adapters restored reliable high-speed connectivity through coaxial wiring"
summary = "A real-world case study diagnosing and solving mysterious network latency issues caused by powerline interference, with performance benchmarks comparing MoCA vs powerline solutions"
categories = ["Networking", "Home Lab"]
tags = ["powerline", "AV2", "MoCA", "networking", "troubleshooting", "home-network", "interference", "performance"]
keywords = ["powerline networking problems", "MoCA adapter setup", "diagnosing network interference", "halogen light interference", "latency troubleshooting", "home network optimization"]
date = "2020-07-04"

# Template comments for future posts:
# description = "Keep under 160 chars for SEO - focus on primary keywords and value proposition"
# summary = "2-3 sentence teaser shown in post listings"
# categories/tags = Choose existing where possible for consistency
# keywords = Include long-tail variations and semantic terms
+++

## My port problem

Moving is always filled with surprises. My unnwanted apartment warming present was crappy network connectivity. The prospect of a gigabit internet connection excited me the instant I looked up service providers, but it turns out, the only wired connection point is about 50 feet from my office and my servers (see my other [blog post]({{< ref "/blog/kubernetes_with_kubespray" >}}) to learn more about my homelab).

A few years ago, my Dad wanted to connect his router in his bedroom to devices in his living room. I did a little research and I bought him a [powerline adapter](https://smile.amazon.com/gp/product/B01H74VKZU/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=0). The living room and bedroom were in the same corner of the house (but on separate floors) so they shared circuit breaker. My dad was able to stream 4K movies to his TV with ease after installing the adapter.

After a great experience with my dad's network, I thought powerline would be a panacea for my networking woes. I quickly realized that was not the case. 

## Unexpected Latency

My brother Chris was staying in my office for about a month after my move to Seattle. He was also moving, but had a gap before his next lease started. One morning, he told me that *League of Legends* was lagging when he used the powerline connection instead of the WiFi. 

I thought it was strange. How could a wired connection over powerline be so laggy? I tested the latency to one of my servers and everything seemed fine.

The stats looked something like this (I used [MTR](https://en.wikipedia.org/wiki/MTR_(software)) to gather the stats):

| % Packets Lost | Packets Sent | Avg Ping | Best Ping | Worst Ping | StDev |
|----------------|--------------|----------|-----------|------------|-------|
| 0.0%           | 224          | 9.2ms    | 3.3ms     | 32.8ms     | 5.4ms |


Later that evening, Chris reported more internet problems so I checked again:

| % Packets Lost | Packets Sent | Avg Ping | Best Ping | Worst Ping | StDev |
|----------------|--------------|----------|-----------|------------|-------|
| 0.0%           | 69           | 268.8ms  | 95ms      | 393.4ms    | 61.3  |

I could send packets to Austrailia in the of time it took them to go from my living room to my bedroom.

Something was very obviously wrong with my setup, and I wasn't sure what it could be. My suspicions were:

- Washing machines and Driers in my building/unit.
- The Elevator for the building. 
- A neighbor running an air conditioning unit.

Without monitoring the sin waves of my electrical power, it was hard to tell. But regardless of the cause, I was hungry for stable internet.

{{< image class="left floated" img_class="centered medium" src="yall_got_ethernet.jpg" >}}

A few weeks later, my brother moved out. With my office now empty, I locked eyes with the coaxal cable protruding from the back wall.

Internet sleuthing revealed that you can run Ethernet over coaxial cable. Apparently, the standard for doing this is called [MoCA (Multimedia over Coax Alliance)](https://en.wikipedia.org/wiki/Multimedia_over_Coax_Alliance) . Not to be confused with: [MoCA (Modern Cannabis)](https://moderncann.com/). It's similar to what many cable providers use to bring internet into the house. 

I bought my adapter after a bit of research. There are a couple revisions of the MoCA standard [according to the MoCA Alliance](http://www.mocalliance.org/about/faqs.htm), the 2.5 standard boasts 2.5 Gbps of throughput, while the 1.0 standard supports 1 Gbps. I went with an [Actiontec adapter which supports MoCA 2.5](https://smile.amazon.com/gp/product/B088KV2YYL/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1). 

After placing my order for the MoCA adapter, I tried to figure out what unintended effects this latency was having on my Home Lab.

I installed [goldpinger](https://github.com/bloomberg/goldpinger) to help me learn more about how my Kubernetes cluster was handling the latency. Goldpinger monitors latency in your Kubernetes cluster by deploying a mesh of daemonsets. The daemonsets ping each other over HTTP to track inter-node latency tracks Kubernetes control plane latency.

{{< image src="goldpinger_latency.png" >}}

When I looked at this graph, I realized that control plane operations were talking far longer than I expected.
Kubernetes was struggling to keep up with regular control plane operations. 

I found that I was unable to perform helm installs when latency was too high. The command would time out when trying to fetch secrets for the target namespace.


I posted about my problem in Workiva's `#homelab` Slack channel and found some interest from one of my team members.

Talking through the patterns in my increased latency turned on a lightbulb in my head.

{{< image img_class="large centered" src="conversation_with_andrew.png" >}}

I was standing in my office when I read Andrew's message, so the first thing I did was turn off the lights. For the sake of science, I went through the rest of my apartment turning off the rest of the lights.

## The Culprit
{{< image 
title="Control Plane Latency Measured By Goldpinger"
caption="**Click on the image to seen an enlarged view**. The vertical blue dotted lines represent a light switch toggle. The first line on the left is when I turned off all lights in my apartment. The next two lines were when I turned on tack lights in the living room. The fourth line was a light switch in the master bedroom. The final line was when I turned on the office track lighting which was causing my problems."
src="lights_experiment.png" >}}

The halogen track lighting in my office was interfering with the powerline adapter.

A [*COMPUTERWORLD*](https://www.computerworld.com/article/2541274/powerline-adapters--home-networking-without-rewiring.html?page=3) article from 2008 confirmed my suspicions.

> ... HomePlug AV system might, in an ideal environment, achieve 86Mbit/sec. to 90Mbit/sec., but that extensive testing showed that 35Mbit/sec. is a realistic expectation. However, he noted that 35Mbit/sec. is sufficient for high-definition video, which usually takes 20Mbit/sec. Aluminum house wiring (used three decades ago), halogen lights, long wiring runs and electric motors can also degrade a signal, he noted

By the time I figured this out, I had already ordered my MoCA adapters, but part of me wondered what I could do to fix the interference from the halogen lights. Would LED equivalents have the same problem?


## A Happy Ending

The MoCA adapters arrived and I was elated! It didn't take me too long to set them up.

{{< image img_class="medium centered" src="moca_adapter.jpg" height="600" >}}

To make sure that everything worked, I followed up with MTR to check my latency. MoCA turned out to be better in pretty much every way.

| Case                   | % Packets Lost | Packets Sent | Avg Ping | Best Ping | Worst Ping | StDev |
|------------------------|----------------|--------------|----------|-----------|------------|-------|
| MoCA                   | 0.0%           | 103          | 6.8ms    | 5.1ms     | 12ms       | 1.1ms |
| Powerline (Best Case)  | 0.0%           | 224          | 9.2ms    | 3.3ms     | 32.8ms     | 5.4ms |
| Powerline (Worst Case) | 0.0%           | 69           | 268.8ms  | 95ms      | 393.4ms    | 61.3  |

The only category Powerline seemed to beat MoCA was minimum latency. In some cases it managed to beat MocA by about 2ms.

I am not sure where the coax for my apartment is terminated, it's possible that there's a large coax cable running down to the basement. That's a topic for another blog post.

If you live somewhere that doesn't have ethernet jacks in every room, but is wired for cable, consider MoCA, it's a solid alternative to ethernet.
