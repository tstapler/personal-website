+++
title = "Career Aide"
description = "Dynamic resume builder with multi-format export capabilities using MEAN stack"
summary = "Hackathon-winning solution for streamlined resume management and job application automation"
categories = [ "Iowa State Portfolio" ]
tags = ["hackathon", "nodejs", "mongodb", "angular", "loopback"]
keywords = ["resume builder tool", "hackathon project winner", "MEAN stack resume generator", "job application automation", "dynamic pdf generation"]
featured_image = "/img/career-aide.jpg"
github = "https://github.com/tstapler/career-aide"
date = "2017-04-22"
+++

Career Aide revolutionizes resume management by combining a centralized information hub with dynamic output generation. Built during HackISU Spring 2017, this MEAN stack application addresses the pain points of maintaining multiple resume versions across job platforms.

**Key features**:
- Centralized resume information storage in MongoDB
- Angular-based form interface with real-time preview
- Multi-format export (PDF/HTML) with theme support
- JSON Resume standard compliance
- LoopBack API for extensible integrations

**Technical implementation**:
- Node.js backend with LoopBack API framework
- Angular 2 frontend using TypeScript
- Puppeteer for PDF generation
- JSON Schema validation for resume data
- Angular Reactive Forms for complex input handling

The project's biggest technical challenge came from Angular's zone.js integration, where we discovered a race condition in form validation during the final hours of the hackathon. By implementing a queue-based validation approach, we maintained functionality without requiring upstream framework changes.

Our JSON Resume implementation required careful schema mapping to support both standard fields and custom extensions like portfolio links. The result was a flexible validation system that ensured compatibility while allowing user customization.

**Lessons learned**:
- MEAN stack's rapid prototyping capabilities for hackathons
- PDF generation pitfalls with dynamic web content
- Schema design tradeoffs between flexibility and validation
- Importance of Angular change detection strategies
