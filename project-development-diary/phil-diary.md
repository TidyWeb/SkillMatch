Written with help from Claude, from my own answers.

# Phil's project development diary: SkillMatch, Code Institute Unit 4 hackathon

## What I thought I was getting into

I knew what it was. Four days, small teams, and a suggestion from the Code Institute that we do another data analysis like the ones we'd done in Units 1, 2 and 3. I thought that was a bit boring. What it was really trying to teach us was how to collaborate using GitHub and version control. We have collaborated. We've failed a little bit on version control.

The idea came from Oana. She said something to me about the blizzard of job adverts and how on earth anyone was meant to find a job in it. I thought it was a great idea and suggested we build the hackathon around it. She agreed. That was the two of us.

I invited seven people at first. The course coordinator said that was too big, and after some negotiation we ended up with four. A lot of people wanted a health-focused data analysis. We weren't doing that. We were building a utility, an app, and I wanted something useful, not an academic exercise. Then another team was split up because of non-contributing members, and SK joined us a day later.

I put myself forward as data architect straight away. I've got high standards now and I know what I can do. I suggested Oana as project manager, and Esmat and John took data analyst roles. All those roles came off the Code Institute's suggestion sheet.

I felt excited, and wary, because I knew it would be tough. I'd never built a live app that runs in the cloud. But mostly excited, because I thought it was a really good idea.

## Architect, plumber, electrician, bricklayer

I'm not naturally in the technical jargon, so I use analogies. The word architect is key for me. I saw myself as architect and plumber, architect and electrician, architect and bricklayer. The guy who puts up the wall that supports something, runs water to it, and wires it so a light comes on when someone walks into a certain part of the website.

I like thinking about concepts. I like grilling myself about what I'm trying to do, what it's for, and how people will use it. That's the architecture side. Then I love the building side, actually making it work. I expected to lead the build, because I've probably got more technical experience than the rest of the team. We split the jobs up as the idea grew.  That growing came about because we talked about the idea as a team in live Google meetins.

## How the idea changed

At the start it was just the SkillMatch app: filter the blizzard down to jobs that are close enough to get to, at a level where you've got a chance of an interview, and suited to your skills. That was the hard part, because the language of recruitment is slippery, sometimes disingenuous and often incoherent. When it is precise, it's over-precise.

Then we realised the course hadn't taught anyone how to build a GitHub profile. Apart from a couple of CV masterclasses, it hadn't really taught anyone how to build a LinkedIn profile either. So those guides became key.

I've got dozens of CVs, because people have asked for them in different contexts. One for when I've worked between contracts as a PAYE person in material flow at Jaguar Land Rover. A completely different one for joining the executive board of a public limited company in the City of London. Same person, different transferable skills. That's when I realised the app couldn't just filter by keywords. It needed to understand transferable skills more than job titles, because everyone on the course is a career changer. I'm going to be 62 soon. I've done amazing things in my life, and none of it is two years experience of using Power BI in a shoe factory.

Some of the team worried we weren't doing a data analysis. This hackathon is voluntary and not assessed, but because of that worry I said we could analyse the output: how well the app works, and how well the skills we learned on the course match what the market wants right now. That became the Data analysis section.

## What I actually did

I always knew I'd do most of the building. I work fast, and I finished Unit 3 four days before anyone else, so I got ahead. I planned, tried things out and had a few ideas in my back pocket. Through group discussion the rest of the package came out naturally, and because I'd already explored a lot of it, I could show examples quickly. People said, "Oh, wow, yeah, that's good," or "that needs o do this" so everyone got on board because they could see where we were going.

I built the app (Oana's idea), the GitHub guide, CV Tailor (a group idea), the site, the data pipeline and the repo. I reviewed Esmat's LinkedIn guide, and she reviewed my GitHub guide in depth. SK was vital in working with me to get the CV Tailor working, it is the heart of everything to me now, the most important thing in the entire project (and will be more so once I link it up with my plan for a live mock interviewer skill that uses Claude voice, your CV and biography file, against the job spec requirements of any role selected from the SkillMatch app).  The data analysis grew out of the team's concern to actually have some data analysis in the project, and it was built mainly from John's notebook and the stored data output that we built into the repo.  It was mainly Oana and John leading it.

By the end we had 52 merged pull requests and 120 issues on the board. It's been a lot of hours. This last weekend alone I worked from Friday afternoon until after 11pm, Saturday from 9am until past midnight, and I was back at it on Sunday morning.

## What I'm proudest of

I thought it would be the app. Now it's built and I'm using it, it's actually CV Tailor. It runs locally in Claude desktop, and you talk to your biographer and keep adding to it. It pulls out your transferable skills and asks you for examples in the STAR format.

What I want next is a Mock Interviewer, built on top of it. It doesn't exist yet. The Code Institute careers adviser showed us a version, and voice mode changes everything. You'd have a dozen STAR stories from your working life and practise them like a stand-up comedian with a joke: tweak it, fix the timing, shrink it down. I tried it in Gemini and I was awful. I like talking and I was all over the place. I don't want to lose the colour of who I am, but I do want to deliver my story with punch.

## What was hard

The first real install of CV Tailor was with SK, live on Google Meet with him sharing his screen. It took about two and a half hours. We followed the instructions exactly, installed Desktop Commander in Claude desktop, and it couldn't see the SkillMatch folder. Under "Yours" there were two Desktop Commander entries with different icons: one with a chevron and slash, one with a stylised DC. We installed the second one, Windows Defender asked for permission, and I knew it was working. It listed the folder straight away. That fix is now in the instructions. I had to leave him to run it and send me the results, and I'm doing my own full test today.

The hardest part with people was SK arriving with no context, his head still in his old project. He's a lovely man with a lot of experience in old-school software engineering and project management qualifications. There was friction between him and Oana. A lot of his points were right in the formal sense, but they didn't help a team that didn't know that protocol. Some meetings ran two hours and I was saying, guys, I haven't got the time. Once we've agreed a path, we need to be out doing, not talking. What fixed it was people seeing the project get built, me constantly sending things out for review, and my sit-down session with SK. I think once he saw for himself what we were trying to do, and saw the utility of it, he climbed onboard.

We used Discord to talk to each other, and that sidetracked GitHub and the project board. By Saturday the board was badly out of step with what we'd shipped. Our PRs never said "Closes #", so nothing closed itself when it merged. I cleaned it up with my AI agents, after I'd looked at hundreds of cards and lost patience.

Then the tech annoyances: usage limits that cut me off mid-task, twice in one weekend, and the connection to my files dropping every time I switched windows. Deeply frustrating.

## What I'd do differently

I'd have a longer first meeting with a short bullet-point overview of the idea, then ask who fancies which part. I couldn't have been PM myself, or nothing would have got built. And I don't think SK's formal style would have fitted a team of newbies either. What I'd want is a relaxed PM who lives in the project board: someone who reads each PR, approves it or sends it back, closes the card, and hands out the next task. None of us knew how to do that. I only see it now, having been through it. I wouldn't change anything about how we built it, and I wouldn't say anyone was a hindrance. None of us knew that writing  "Closes #" and the issue number in a PR closes the issue automatically when it merges. I do now, and it's a lesson that will stay with me.

## How I used AI

Mainly Claude and Codex, plus Gemini for research. AI is brilliant at giving me the overview first, which is how I work. It's like an electrician reading a schematic, or a navigator's chart: it looks nothing like the building or the coast until you learn to read it against what's in front of you. It was brilliant on Google Cloud too. I found the Cloud CLI work hard, so we did it step by step: I'd run something, paste the output back into Codex, and we'd go on. Slow, precise, and it worked first time.

Where it frustrates me is design. I'm fussy about visual language and about teaching documents having a logic: overview, simple example, explain the example, then go deeper. Show me, don't give me walls of text. GitHub's interface is puzzling if you don't know it, so the guides needed pictures of where things are. Hard rules don't work with AI either, because it applies them out of context. Like the PM, I want broad contextual judgement, not hard rules.

The team agreed our house style, Navy A, from palettes I generated and everyone commented on in Discord. After applying focused personal attention on most of the pages of the website, I forgot the homepage, and it was a big wall of cream cards. I asked Rory, my data and design agent, to apply the Navy A style and mix it up, make it look pretty.  He did, with no other intervention and it looks  beautiful.

The major breakthrough was learning that Claude can now handle agents.md.  This is a revolution for me because I can drive Codex directly. Before that I copied prompts from one to the other by hand, which works, but is tedious and slow and can get very messy when you have multiple agents windows open doing mulitple different tasks.   The key breakthrough was leaning that I could set up a mailbox inside my local project folder for Claude, so my agents (Kevin the repo guardian, Rory the Data Guy, and Imogen the image mistress) could all message each other there directly.  No more flipping through windows and finding the right instance.  All I had to say was "Kevin, check your inbox." and the task was there ready to be worked on. That's changed how I'll work from now on. It's brilliant.

## What it's done for me

I don't think there's anything I can do now that I couldn't before. I'm bold because of what I've built previously with AI and because I have built things all my working life. I believe the world's changing: AIs can write better code than people, and every programmer is now a project manager, architect and chief designer. That's exciting and terrifying. I still review everything. I check what it did in the interface first, then the code, and I play different models off each other. Codex and Claude spot different things, so I like to have them mark each other's homework.  It costs more in usage, but it has not failed me yet.

It doesn't change what I'd say about myself to an employer. What it changes is that when I say I can build something, I can show them examples of what I have built. I've built motorcycles, a 400 square metre stand for multi-million-dollar yachts, houses. I've been in the loft putting in the right gauge of cable and wiring solar to a battery. I've got two sheds and two rooms full of tools, about two and a half tons of them. Mechanical, electrical, plumbing, landscaping, I have tools for tools. Yet coding with AI is the best toolbox I've ever had.

I don't want what is in effect a glorified data-entry role. 'Can you use SQL and Excel for this, can you use Power BI for that?' I find that boring and limited in ambition.  I understand that universal tools are important in large enterprises, but at the same time they are limiting.  My Unit 3 Assessment into healthy life expectancy is an example of that.  I could have built a Power BI dashboard to pass the assessment, but it would not have served the work with the richness or depth of the custom dashboard I built.  I understand why things like Tableau and Power BI exist, but they are just a hint of what can actually be done when it comes to data visualisation, and making things clear and comprehensible in a single look.

I want a role where people want to invent something new. A new way of working or of seeing the world.  I like thinking deeply about creating things that improve the world and enjoy the battle that comes with such tasks.  The world is changing, much as it did when steam power arrived. Old ways of working will begin to disappear, and new ways will emerge and out-compete those old ways.  I'm hoping my portfolio shows that's what I do.

Phil McCool - 01/11/2026 



