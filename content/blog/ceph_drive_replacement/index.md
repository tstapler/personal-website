+++
draft = true
+++

## Diagnosing and Replacing Failed Drives in Ceph

When dealing with drive failures in a Ceph cluster, systematic troubleshooting is crucial. Here's how these commands helped me identify and replace failed drives:

### 1. Identifying Failed OSDs
```
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

```
This command revealed the cluster layout and OSD statuses. Key observations:
- OSD 4 and 10-11 were `down`
- Host `Leviathan` had multiple failed drives
- Weight distribution showed imbalance

### 2. Mapping Physical Drives to OSDs
```
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

```
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

```
Cross-referenced mount points with serial numbers to:
- Identify physical drive locations in the server
- Confirm which OSDs mapped to failed drives
- Verify drive health status through SMART tests

### 3. Confirming Drive Failure
```
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


```
This SMART test output showed:
- Recent successful short test (LifeTime 14 hours)
- Older vendor-specific tests passed
- No immediate hardware errors (completed without error)

### 4. Monitoring Recovery Progress
```
Key recovery metrics observed:
- Object migration rate (32 MiB/s)
- Backfill operations progress
- Cluster capacity changes (47 TiB → 51 TiB)
- Reduction in degraded objects (1.981% → 1.483%)
- PG state transitions during recovery
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

```
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
