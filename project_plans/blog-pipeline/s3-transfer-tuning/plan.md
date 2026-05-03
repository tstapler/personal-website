# Plan: Optimizing S3 Transfer Speeds

**Source**: ~/Documents/personal-wiki/logseq/journals/2024_01_25.md (links only); AWS CLI docs; AWS blog post on S3 CLI
**Target audience**: Engineers dealing with slow S3 uploads/downloads — homelab NAS backups, data pipeline transfers, CI artifact storage
**Tone**: Practical tip post — short, focused, show the settings and the result
**Estimated length**: 500–700 words

---

## ⚠️ Research Gap: Findings Not Documented

The source journal has the question ("Drew Marsh asked me to look into speeding up S3 file transfers") and reference links but no actual findings, benchmarks, or conclusions. Before drafting, you need:

- What did you actually try? Which settings did you change?
- Before/after transfer speeds (even rough numbers — "went from 80MB/s to 340MB/s")
- What infrastructure was this on? (AWS-to-AWS? On-prem to S3? Homelab NAS to S3?)
- Did you end up recommending `s5cmd` or another tool instead of the AWS CLI?

Without real numbers this is just a reshuffling of the AWS docs. The existing reference links are good but the post needs your benchmarks to be worth publishing.

---

## Post Structure

### H2: Why the AWS CLI is Slow by Default
- Default `max_concurrent_requests = 10`, `multipart_threshold = 8MB`, `multipart_chunksize = 8MB`
- These defaults are conservative: designed to work reliably on slow/flaky connections, not optimized for fast links
- On a fast link (homelab NAS, EC2 to S3) you're leaving most of your bandwidth on the table

### H2: The Key Settings
Small table showing the settings, defaults, and what to change them to:

| Setting | Default | Aggressive |
|---|---|---|
| `max_concurrent_requests` | 10 | 20–50 |
| `multipart_threshold` | 8MB | 64MB+ |
| `multipart_chunksize` | 8MB | 16–64MB |
| `max_bandwidth` | unlimited | set to avoid saturating link |

How to set them:
```ini
[profile default]
s3 =
  max_concurrent_requests = 20
  multipart_threshold = 64MB
  multipart_chunksize = 16MB
```

### H2: Finding Your Sweet Spot
- Transfer speed doesn't scale linearly with concurrency — there's a point of diminishing returns and a point where you start hurting yourself (connection errors, timeouts)
- Simple benchmark loop: try 10, 20, 30, 50 concurrent requests against a large file, record MB/s
- Personal results here

### H2: When to Reach for s5cmd Instead
- `s5cmd` is written in Go, uses the AWS SDK, and parallelizes at a different level
- Consistently outperforms the AWS CLI for bulk operations (link to their benchmarks)
- Worth mentioning: if you're transferring thousands of small files, concurrency config matters more than multipart settings

### H2: Caveats
- Different results on EC2 vs on-prem vs homelab NAS
- `max_bandwidth` matters if you're sharing the link with other things
- Don't set `max_concurrent_requests` above ~50 — you'll start hitting S3 rate limits

---

## Key Points to Nail
- Real before/after numbers are the whole point of this post
- Keep it short — this is a "tip" post, not a deep dive
- The `s5cmd` mention is a value-add for anyone who hits the CLI ceiling

## Next Step Before Drafting
Pull up actual benchmark numbers from wherever they were recorded (Slack with Drew? Local notes?). Even "went from X to Y on a Z MB file" is enough.
