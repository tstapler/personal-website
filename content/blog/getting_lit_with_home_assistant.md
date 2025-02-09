+++
title = "Getting Lit with Home Assistant: From Kubernetes Clusters to ESP32 Light Strips"
draft = true
+++

## I. Introduction
- Hook: Evolution from manual light switches to automated illumination
- Brief Home Assistant overview (local-first architecture, dashboard example screenshot)
- Thesis: How containerization + open hardware create reliable smart lighting

## II. Infrastructure Foundation
- Home Assistant in Kubernetes:
  - Helm chart configuration snippet from your GitHub repo
  - PVC setup for persistent configuration
  - NetworkPolicy for IoT VLAN segregation
- Why Kubernetes: 
  - Simplified updates (ChartMuseum integration)
  - Resource efficiency vs standalone VM

## III. Lighting Hardware Build
- **LED Strip Deployment**
  - WS2812B strip specs + soldering diagram
  - Weatherproofing for outdoor installation
  - Power injection challenges (12V vs 5V)
- **ESP32 Controller**
  - Flashing process with ESPHome (YAML config example)
  - WiFi reliability vs Zigbee alternatives
  - Cost comparison: $8 DIY vs $40 commercial controller

## IV. Z-Wave Integration
- Why Z-Wave in 2.4GHz polluted environment:
  - Channel scanning results from WiFi Analyzer
  - Z-Wave's 900MHz advantage
- Vera Edge setup:
  - Security pin configuration
  - Battery-operated device optimizations
- zwave-js-server in Home Assistant:
  ```yaml
  zwave_js:
    url: ws://vera-proxy:3000
  ```

## V. Automation Examples
- Morning routine flow:
  ```yaml
  trigger: 
    - platform: sun
      event: sunrise
  action:
    - service: light.turn_on
      target:
        entity_id: light.bedroom_strip
      data:
        brightness_pct: 50
        kelvin: 2700
  ```
- Motion-activated pathway lighting with adaptive timeout
- Vacation security modes using randomness + sunset tracking

## VI. Lessons Learned
- Stability considerations:
  - ESP32 dropout recovery strategies
  - Kubernetes liveness probes for HA
- Performance metrics:
  - Latency comparison (local vs cloud control)
  - Energy savings from automation (kWh usage graphs)

## VII. Conclusion
- Future plans: Thread protocol adoption
- Call-to-action: Fork the Helm chart from [your GitHub repo]

## FAQs Sidebar
- "Can I run this without Kubernetes?" (Docker-Compose alternative)
- "What soldering skills are needed?" (Link to wiring tutorial)
- "Z-Wave vs Zigbee in apartments?" (2.4GHz congestion diagram)
