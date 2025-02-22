+++
title = "Career Aide"
categories = [ "Iowa State Portfolio" ]
tags = ["school", "programming-project", "hack-isu"]
featured_image = "/img/career-aide.jpg"
github = "https://github.com/tstapler/career-aide"
+++

[Career Aide](https://github.com/tstapler/career-aide) is a project I built with my younger brother for Hack ISU Spring 2017.

**Technologies used**:
  - MongoDB
  - Node.js
  - Angular 2
  - LoopBack

## Inspiration

Updating your resume can be time consuming at best and down right painful at worst. We wanted to come up with an awesome hack that will make our lives easier

## What it does

This Career Aide gives users the ability to manage and create dynamic html and pdf based resumes. Users first enter their information into an easy to use form view. Once entered their resume is saved into the database for later reuse and addition to their existing content. When information has been enter into the database it can be then used to generate pdfs and html pages using a variety of different themes.

## How we built it
We built our back end on node.js, mongodb and Loopback. We chose node because of the wealth of libraries for all things web dev. For our frontend we used Typescript and Angular 2. Javascript/Typescript is a language we're both pretty familiar with, so it was a logical choice.

## Challenges we ran into
The biggest challenges we ran into were a bug in Angular 2's zone handling and the complexity of the JSON Resume standard.

Towards the end of the Hackathon we noticed that our resume editor wasn't updating properly in some situations. After around 4 hours of debugging we stumbled upon this open issue which perfectly described what we were facing. At that point we moved on to implementing other parts of the app but we do wish we had those four hours back.

Implementing the JSON Resume standard was challenging because of the multitude of choices it has. We ran into some edge cases with our rendering code.

## Accomplishments that we're proud of
We're incredibly proud that we were able to pick a project which was ambitious enough to take us the entire hackathon but wasn't so ambitious that we couldn't finish. We both sharpened our development skill and speed which is always nice.

## What we learned
We had both done some javascript development but this was the first time that we had worked with a MEAN stack. In previous hackathons we've opted to build our backend in Python. The Loopback framework lets you build APIs with ease and we'll definitely be considering using it for future projects. There were many struggles throughout the project and without a doubt they improved our debugging skills

## What's next for Career Aide
In the future we hope to expand the application by offering a service to update social media profiles and a browser extension to autocomplete job applications.
