+++
title = "When Drives Go Bad: My Ceph Cluster Rescue Mission"
description = "Walkthrough of diagnosing and replacing failed drives in a Ceph storage cluster with real-world examples"
summary = "Practical guide to identifying failed OSDs, mapping physical drives, and monitoring recovery in Ceph clusters"
categories = ["Storage", "Troubleshooting"]
tags = ["ceph", "drive-replacement", "linux", "storage-cluster", "hardware-failure"]
keywords = ["Ceph drive replacement", "failed OSD recovery", "Ceph cluster maintenance", "storage troubleshooting", "SMART monitoring", "failed"]
date = '2025-02-16'
draft = false
featured_image = "/img/tech-logos/Ceph_Logo_Standard_RGB_120411_fa.png"
+++

Let's be real - storage hardware fails. A lot. When three drives died simultaneously in my [Ceph](https://ceph.io/en/) cluster last month, I
learned firsthand why proper diagnostics matter. What started as some weird latency spikes turned into a crash course in
distributed storage triage. Here's how I navigated the crisis:

### 1. The Smoking Gun: Tracking Down Dead [OSDs](https://docs.ceph.com/en/latest/rados/operations/operating/#add-or-remove-an-osd)

My first clue something was wrong? The dashboard showed weird latency spikes during peak hours. Running the classic
`ceph osd tree` ([Ceph OSD Tree Documentation](https://docs.ceph.com/en/latest/rados/operations/operating/#monitoring-osds)) gave me the lay of the land:

```shell
❯ sudo ceph osd tree
ID  CLASS WEIGHT   TYPE NAME          STATUS REWEIGHT PRI-AFF 
 -1       45.41072 root default                               
 -3              0     host Absis                             
 -2              0     host Leviathan                         
 -4        9.97719     host absis                             
  4   hdd  1.81360         osd.4        down        0 1.00000 
  5   hdd  1.81360         osd.5          up  0.95001 1.00000 
  6   hdd  1.81360         osd.6          up  1.00000 1.00000 
  7   hdd  1.81360         osd.7          up  0.95001 1.00000 
  8   hdd  2.72279         osd.8          up  0.95001 1.00000 
 -5       19.05956     host leviathan                         
  0   hdd  2.72279         osd.0          up  1.00000 1.00000 
  1   hdd  2.72279         osd.1          up  1.00000 1.00000 
  2   hdd  2.72279         osd.2          up  1.00000 1.00000 
  3   hdd  2.72279         osd.3          up  1.00000 1.00000 
  9   hdd  2.72279         osd.9          up  1.00000 1.00000 
 10   hdd  2.72279         osd.10       down        0 1.00000 
 11   hdd  2.72279         osd.11       down        0 1.00000 
-11       16.37398     host smicro1                           
 12   hdd  5.45799         osd.12         up  1.00000 1.00000 
 13   hdd  5.45799         osd.13         up  1.00000 1.00000 
 14   hdd  5.45799         osd.14         up  1.00000 1.00000 
```

This command revealed the cluster layout and OSD statuses. Key observations:

- OSD 4 and 10-11 were `down`
- Host `Leviathan` had multiple failed drives
- Weight distribution showed imbalance

### 2. Hardware Sleuthing: From Logs to Laptop Drives ([lsblk man page](https://man7.org/linux/man-pages/man8/lsblk.8.html))

Here's where things got physical. Ceph's logical OSD IDs don't mean squat when you're standing in front of a rack server
with 12 drive bays. My "aha" moment came cross-referencing these outputs:

```shell
❯ sudo lsblk -o KNAME,MOUNTPOINT,SERIAL
KNAME MOUNTPOINT               SERIAL
sda                            YBKWYRXF
sda1  /var/lib/ceph/osd/ceph-4 
sda2                           
sdb                            BFHJD9VF
sdb1  /var/lib/ceph/osd/ceph-5 
sdb2                           
sdc                            BFG5AJEF
sdc1  /var/lib/ceph/osd/ceph-6 
sdc2                           
sdd                            BFG6NTNF
sdd1  /var/lib/ceph/osd/ceph-7 
sdd2                           
sde                            P8H5PG4P
sde1  /var/lib/ceph/osd/ceph-8 
sde2                           
sdg                            Z1DANJQA
sdg1  /    
```

```shell
❯ sudo lsblk -o NAME,SERIAL,MODEL,MOUNTPOINT
NAME   SERIAL          MODEL            MOUNTPOINT
loop1                                   /snap/code/40
loop2                                   /snap/gnome-3-28-1804/128
loop3                                   /snap/core18/1880
loop4                                   /snap/gnome-3-26-1604/100
loop5                                   /snap/gtk-common-themes/1506
loop6                                   /snap/discord/112
loop7                                   /snap/core/9665
loop8                                   /snap/gnome-3-28-1804/116
loop9                                   /snap/core/9804
loop10                                  /snap/gtk-common-themes/1502
loop11                                  /snap/gnome-3-26-1604/98
loop12                                  /snap/discord/109
loop13                                  /snap/core18/1885
loop14                                  /snap/code/39
sda    P8H56V9R        Hitachi HUS72403 
├─sda1                                  /var/lib/ceph/osd/ceph-9
└─sda2                                  
sdb    S33FNX0J300111J Samsung SSD 850  
├─sdb1                                  /
├─sdb2                                  
└─sdb5                                  
sdc    P8G9HJUR        Hitachi HUS72403 
├─sdc1                                  /var/lib/ceph/osd/ceph-3
└─sdc2                                  
sdd    P8G957GR        Hitachi HUS72403 
├─sdd1                                  /var/lib/ceph/osd/ceph-0
└─sdd2                                  
sde    P8GD8HYX        Hitachi HUS72403 
├─sde1                                  /var/lib/ceph/osd/ceph-1
└─sde2                                  
sdf    P8HAKSMR        Hitachi HUS72403 
├─sdf1                                  /var/lib/ceph/osd/ceph-2
└─sdf2    
```

Cross-referenced mount points with serial numbers to:

- Identify physical drive locations in the server
- Confirm which OSDs mapped to failed drives
- Verify drive health status through SMART tests

### 3. Confirming Drive Failure with [SMART Tests](https://en.wikipedia.org/wiki/S.M.A.R.T.)

```shell
❯ sudo smartctl -l selftest /dev/sdb
smartctl 7.1 2019-12-30 r5022 [x86_64-linux-5.7.10-1-MANJARO] (local build)
Copyright (C) 2002-19, Bruce Allen, Christian Franke, www.smartmontools.org

=== START OF READ SMART DATA SECTION ===
SMART Self-test log structure revision number 1
Num  Test_Description    Status                  Remaining  LifeTime(hours)  LBA_of_first_error
# 1  Short offline       Completed without error       00%        14         -
# 2  Vendor (0xb0)       Completed without error       00%     33786         -
# 3  Vendor (0x71)       Completed without error       00%     33786         -
```

This SMART test output showed:

- Recent successful short test (LifeTime 14 hours)
- Older vendor-specific tests passed
- No immediate hardware errors (completed without error)

The SMART test showed that the drive had no remaining life and was likely the cause of the failure.

### 4. The Long Haul: Watching Rebuild Progress

This is where patience becomes a virtue. As my cluster slowly rebuilt itself, I learned to love the `ceph -s` command.
The numbers told a story of gradual healing:
Key recovery metrics observed:

- Object migration rate (32 MiB/s)
- Backfill operations progress
- Cluster capacity changes (47 TiB → 51 TiB)
- Reduction in degraded objects (1.981% → 1.483%)
- PG state transitions during recovery

The output from this command shows the cluster's health from before I replaced one of the drives.

```shell
  cluster:
    id:     1d7c1a74-29f3-451b-9774-dd97d07de6a2
    health: HEALTH_WARN
            1 nearfull osd(s)
            2 pool(s) nearfull
            2376687/9406278 objects misplaced (25.267%)
            Degraded data redundancy: 186338/9406278 objects degraded (1.981%), 27 pgs degraded, 30 pgs undersized
            mon Leviathan is low on available space
 
  services:
    mon: 3 daemons, quorum Absis,Leviathan,smicro1
    mgr: smicro1(active), standbys: absis, leviathan
    mds: archive-1/1/1 up  {0=smicro1=up:active}, 2 up:standby
    osd: 15 osds: 15 up, 15 in; 285 remapped pgs
 
  data:
    pools:   2 pools, 640 pgs
    objects: 4.70 M objects, 13 TiB
    usage:   29 TiB used, 19 TiB / 47 TiB avail
    pgs:     186338/9406278 objects degraded (1.981%)
             2376687/9406278 objects misplaced (25.267%)
             355 active+clean
             253 active+remapped+backfill_wait
             23  active+undersized+degraded+remapped+backfill_wait
             4   active+undersized+degraded+remapped+backfilling
             2   active+undersized+remapped+backfill_wait
             2   active+remapped+backfilling
             1   active+undersized+remapped+backfilling
 
  io:
    client:   16 MiB/s rd, 789 KiB/s wr, 51 op/s rd, 79 op/s wr
    recovery: 32 MiB/s, 7 keys/s, 14 objects/s
```

After replacing the drive, you can see that there are now 16 Ceph OSDs and the number of degraded objects had started to
recover.

```shell
❯ sudo ceph -s
  cluster:
    id:     1d7c1a74-29f3-451b-9774-dd97d07de6a2
    health: HEALTH_WARN
            1 nearfull osd(s)
            2 pool(s) nearfull
            3019639/9407604 objects misplaced (32.098%)
            Degraded data redundancy: 139470/9407604 objects degraded (1.483%), 22 pgs degraded, 23 pgs undersized
            mon Leviathan is low on available space
 
  services:
    mon: 3 daemons, quorum Absis,Leviathan,smicro1
    mgr: smicro1(active), standbys: absis, leviathan
    mds: archive-1/1/1 up  {0=smicro1=up:active}, 2 up:standby
    osd: 16 osds: 16 up, 16 in; 333 remapped pgs
 
  data:
    pools:   2 pools, 640 pgs
    objects: 4.70 M objects, 13 TiB
    usage:   28 TiB used, 22 TiB / 51 TiB avail
    pgs:     139470/9407604 objects degraded (1.483%)
             3019639/9407604 objects misplaced (32.098%)
             308 active+remapped+backfill_wait
             307 active+clean
             18  active+undersized+degraded+remapped+backfill_wait
             4   active+undersized+degraded+remapped+backfilling
             2   active+remapped+backfilling
             1   active+undersized+remapped+backfill_wait
 
  io:
    client:   162 KiB/s rd, 658 KiB/s wr, 0 op/s rd, 30 op/s wr
    recovery: 22 MiB/s, 2 keys/s, 9 objects/s

```

I had to repeat this process for the other two drives that had failed.

## Lessons Learned the Hard Way


- **Hot spares matter**: Having replacement drives on hand would have saved hours of downtime
- **Monitor your monitors**: The near-full OSD warning almost caused cascading failures
- **Document drive locations**: A simple rack diagram would have saved 30 minutes of physical inspection
- **Balance as you grow**: My haphazard drive additions created imbalance that exacerbated the failure. With Ceph specifically, using different sized drives on different hosts cause drive failures to have to relocate more PGs (Placement Groups) than if all the drives were the same size.

The cluster lived to serve another day, but this experience taught me that even "self-healing" systems need human
oversight. Next time? I'll be ready with better monitoring and spare drives on standby.

## Appendix
Related Post about how and why I'm using Ceph: [Kubernetes Cluster Setup with Kubespray](/blog/kubernetes_with_kubespray)
Further Reading: [Ceph Hardware Recommendations](https://docs.ceph.com/en/latest/start/hardware-recommendations/)
