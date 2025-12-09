Skip to content
Chat history

You said:
Generate project plan to make a Demo project.

# Object of our Project: Generate Anki (desktop version) cards from PDF file (lecture note, scientific literature)

# Method: 
## Step 1: Convert PDF to Markdown format with marker-pdf Python library (https://github.com/VikParuchuri/marker).
## Step 2: Prepare prompt with the converted markdown file.
### It need specify format of Anki cards (basic), what kind of problem the user want to generate, number of cards to be generated.

## Step 3 : import the generated cards to Anki file manually.
## Step 4 (additional): automate the importing step by integrating this functions as an add-on of Anki application. 

#Timeline
Today is Sep. 30th 2025. and we will have interim presentation on Oct. 14th, 2025. We need to finalize preparation for the interim presentatio by Oct 8th. 
Then, we will have final presentation by the Dec 2nd.

Presentation should be 5 to 10 min. 

# Members
Two graduate students will work

# Development style
We will setup Github repo for this project. We must use Cursor to do vibe coding as  experience vibe coding is important requirement for this project.
ChatGPT said:
Thanks for outlining your project. To create a clear and actionable project plan, could you clarify the following:

What scope or complexity of PDFs are you targeting for the demo (e.g., textbook-style lecture notes, journal articles with figures/equations)?

For Step 2, do you already have a model or method in mind for generating the Anki card content from markdown (e.g., GPT-based prompt chaining)?

Do you want the demo to include Step 4 (Anki add-on automation), or should that be marked as a stretch goal for after the interim?

What operating system will the team use (for compatibility with Anki/marker-pdf setup)?

Let me know and I’ll structure the project plan with milestones, roles, and buffer time leading up to both the interim and final presentations.

You said:
What scope or complexity of PDFs are you targeting for the demo (e.g., textbook-style lecture notes, journal articles with figures/equations)?
Lecture slide and journal articles with figures and equations

For Step 2, do you already have a model or method in mind for generating the Anki card content from markdown (e.g., GPT-based prompt chaining)?
No. We need to and plan to use API 

Do you want the demo to include Step 4 (Anki add-on automation), or should that be marked as a stretch goal for after the interim?
It should be a stretch goal for after the interim

What operating system will the team use (for compatibility with Anki/marker-pdf setup)? Windows
ChatGPT said:
Thanks for the details. I’ll create a project plan to develop a demo that generates Anki cards from lecture slides and scientific PDFs using marker-pdf and a GPT-based prompt system. The initial demo will cover PDF conversion and Anki card generation, with Anki add-on integration as a post-interim stretch goal. I’ll also factor in your Windows environment and the requirement to use Cursor for collaborative development.

I’ll get started on your project plan now and let you know when it’s ready.

Research completed in 3m · 7 sources · 8 searches
Project Plan for Anki Card Generator from PDF

Project Plan: PDF-to-Anki Card Generator Demo
Objective and Overview
The goal is to develop a demo application that automatically generates Anki flashcards from PDF documents (e.g., lecture slides or scientific papers). This will streamline the creation of study flashcards by extracting key information from PDFs and converting it into question-answer card format. The project focuses on implementing a pipeline with the following steps:
PDF to Markdown Conversion – Use an open-source tool (marker-pdf) to convert PDF content into Markdown text for easier processing.
Flashcard Content Generation – Feed the Markdown content into an AI (via API) to generate flashcard questions and answers in a Basic Anki card format.
Card Import into Anki – Import the generated cards into the Anki desktop application (manually for the demo).
(Stretch Goal) Anki Add-on Integration – Optionally, create an Anki add-on to automate the import process (planned after the interim demo).
This demo will handle textbook-style lecture notes and journal articles, including content with figures and equations. The interim focus is on Steps 1–3, while Step 4 is a future enhancement (not required for the interim presentation).
Project Scope and Requirements
Input PDF Types: Lecture slides and academic papers, which may contain formatted text, images, tables, and mathematical equations. The conversion tool (marker-pdf) supports advanced formatting – it can extract images and tables, and even convert math equations to LaTeX
github.com
, ensuring that complex content is preserved in Markdown form.
Output Flashcards: Basic Anki cards with a front (question) and back (answer). The flashcards will target key facts or concepts from the PDF. For example, a slide about a definition could become a “What is X?” card. We will let the user specify the number of cards to generate and possibly the focus (e.g. definitions, concepts, or questions covering each section).
No Pre-trained Model: We are not training a custom model. Instead, we will use an API (likely a GPT-4 based service) to generate flashcard text from the Markdown. Prompt engineering will be crucial to guide the AI to produce useful Q&A pairs.
Platform: Development and demo will be on Windows (the team's working OS). marker-pdf will be used as a Python library (can be installed via pip). Anki Desktop (Windows version) will be used to import and display the cards.
Methodology and Approach
Step 1: PDF to Markdown Conversion
Tool: We will use marker-pdf (GitHub: VikParuchuri/marker) Python library to convert PDFs to Markdown. marker-pdf provides a powerful PDF-to-Markdown conversion with high accuracy. Key advantages: it preserves formatting, extracts images/tables, and even handles math equations by converting them to LaTeX syntax. This suits our needs for lecture notes with formulas or papers with equations.
Setup: The team will install marker-pdf via pip in a Python environment. Installation is simple: `pip install marker-pdf`. The library handles PDF parsing internally using its deep learning models for layout detection and OCR.
Execution: Once installed, using marker-pdf is straightforward in Python code. We import the library, create a PdfConverter instance, and call it with the PDF path. It returns a rendered object containing the Markdown text and extracted images as PIL Image objects.
Output Handling: The returned Markdown will contain the textual content of the PDF, including any images (usually referenced as image files) and LaTeX for equations. For the demo’s scope, text content will be the primary source for flashcards. Non-text elements:
Images: We will note that images are extracted by marker-pdf (placed in a folder, referenced in Markdown). However, generating flashcard Q&A from images automatically is complex and out-of-scope. We might simply ignore direct image-based questions for now. (If needed, we could include a few manually or as future work).
Equations: Since equations are converted to LaTeX, the AI could generate questions about them (e.g., “What does the following equation represent: …?”). Anki supports LaTeX in cards, so we will ensure the LaTeX text is wrapped properly so Anki can render it (Anki uses MathJax for LaTeX). We will test a sample equation card.
Verification: We’ll test marker-pdf on a couple of sample PDFs (one lecture slide deck, one paper) early on. This ensures the conversion quality is acceptable (e.g., headings, bold text, etc., come through in Markdown) and to see how large the Markdown gets for a typical document. This informs how we prompt the AI in Step 2 (since very large Markdown might need splitting or summarizing).
Step 2: Generating Anki Cards from Markdown
Approach: We will use an AI text-generation API (likely OpenAI GPT-4 or similar) to transform the Markdown content into a set of flashcard Q&A pairs. The procedure will be:
Prompt Design: Create a prompt template that instructs the model to produce flashcards. For example: “You are an assistant that creates flashcards. Given the following content extracted from a lecture or article, generate X flashcards in Q&A format suitable for Anki (basic card). Focus on key concepts, definitions, or important details. Provide output as a list of 'Question: ... Answer: ...' pairs.” We will fine-tune the wording of this prompt to get the desired output style.
Feeding Content: Insert the Markdown text (or a relevant portion of it) into the prompt. If the PDF content is very large (e.g., a long article), we might not send the entire text at once to avoid token limits. In that case, possible strategies include:
Splitting the content by sections and generating a few cards per section, then combining results.
Or summarizing the text first (though that risks missing details for specific flashcards).
We will experiment with a manageable size first (perhaps 5-10 pages) and scale up if possible.
Choosing Number of Cards: Allow the user (for demo purposes, ourselves) to specify the number of cards (e.g., 5, 10, 15) to generate. This will be a parameter in the prompt. The model will then try to output that many Q&A pairs. We’ll have to ensure the prompt clearly asks for a specific number of distinct Q&As and maybe enumerate them to be sure none are missed.
Ensuring Format: We need the output in a format that can be easily imported or parsed. Likely, we will use a simple delimiter format (each Q&A separated by a line break, with question and answer separated by a known token or just labeled). For example:
Q: What is ...?  
A: It is ...  
Or Question: ... Answer: ... on separate lines. We will parse this to create a tab-separated text for Anki import. We must instruct the AI not to produce extraneous text beyond the QA pairs.
Development: Implement a Python script that calls the AI API. This includes managing API keys securely (not hardcoding in the repo) and handling the response parsing. We will test this with small dummy content first (e.g., a paragraph of text) to verify the format.
Prompt Tuning & Testing: Generating good flashcards might require iterative prompt tuning. We’ll check:
Are the questions relevant and clear?
Are the answers correct and complete enough (not too verbose, just enough to answer the question)?
Do they cover important points from the text?
If the initial results are unsatisfactory, we may adjust instructions (e.g., “make questions concise,” “avoid trivial details,” or specify the style of questions). We might also post-process the answers (for example, if the answer text includes Markdown artifacts or references from the PDF, clean those out).
Handling Figures/Equations: As noted, fully automating question generation for images is out-of-scope. However, for equations in LaTeX, the AI might include them in questions or answers. We will verify that the LaTeX is intact. When importing to Anki, we’ll ensure the card type is set to render LaTeX (Anki by default can render if the content is enclosed in [latex]...[/latex] or between $ $). We will document how to handle this for the demo (perhaps instruct the AI to put $...$ around LaTeX so it displays as math in Anki).
Step 3: Importing Cards into Anki (Demo Procedure)
Output Format for Import: We plan to take the AI-generated Q&A pairs and format them into a file that Anki can import. The simplest is a tab-separated or comma-separated CSV file with two columns: front and back. For example:
What is Newton's first law of motion?\tEvery object will remain at rest or in uniform motion in a straight line unless compelled to change its state by the action of an external force.
Each line represents one card. We will generate such a file (e.g., cards.txt or cards.csv). If using tabs, it can be a .txt which Anki will parse with tab as the delimiter. We’ll avoid characters that might interfere with CSV format in the content (commas, newlines inside an answer – if an answer is multi-line, we might need to handle that or keep it one line).
Manual Import Process: For the demo, the import will be done manually through Anki’s GUI:
Open Anki on the demo machine (Windows laptop).
Create or select a target deck for the cards.
Use File > Import and select the generated cards.txt file.
In the import dialog, ensure it’s set to “Notes separated by tab” (if we use tab) and map the first field as Front, second as Back of a Basic note type.
Complete the import and verify that the cards appear in the deck.
Verification: We will test this import process beforehand with a sample file to ensure formatting is correct (for instance, check that question marks or special characters aren’t causing issues, and LaTeX formulas appear correctly in Anki’s review mode). If LaTeX is used, we’ll verify Anki’s LaTeX support is working (typically requires having LaTeX installed or using the built-in MathJax; in modern Anki, MathJax is included). We should document any setup needed (maybe none if using MathJax which is default).
Demo Presentation Usage: In the interim presentation, we might show the content of the generated file and a quick import (or have a few cards pre-imported to demonstrate). For final presentation, if time permits, a live demo of selecting a PDF and going through the pipeline to Anki would be ideal. If a live demo is risky, we will prepare a short video or screenshots showing each step.
Step 4: Anki Add-on Automation (Stretch Goal)
This step is planned after the interim presentation, as a stretch goal towards the final. The idea is to eliminate the manual import (Step 3) by integrating the functionality as an Anki add-on or using an automation API. Possible approaches:
Anki Add-on (Plugin): Develop a custom add-on in Python that runs inside Anki. This could add a menu option or button in Anki (e.g., “Import from PDF via marker-pdfAI”) which when clicked, prompts the user to select a PDF, then behind the scenes calls our conversion and generation pipeline, and finally creates new cards in the deck automatically.
Feasibility: Anki’s add-ons are written in Python and can call external scripts or Python code. We’d package our logic into the add-on, ensuring it can call the marker-pdf (maybe by running the conversion as a subprocess or requiring the user to have the marker-pdf running locally) and use Anki’s API to add cards to the collection. This might be complex to do fully by Dec 2, but we will research it.
AnkiConnect: Alternatively, use the AnkiConnect plugin (a popular add-on that exposes a localhost API to Anki). Our code (running outside Anki) could send a request to AnkiConnect with the new cards. This approach means we don’t have to write a full add-on UI, just ensure AnkiConnect is installed. It might be simpler, but it requires the user to run our script separately.
Planned Decision: After the interim demo, we will evaluate which approach is more doable in the remaining time. If the add-on path is chosen, we’ll allocate time to learn Anki’s add-on structure. If it seems too time-consuming, we might implement a basic solution with AnkiConnect as a proof-of-concept by final presentation. In either case, this feature is beyond the core demo; if we cannot fully implement it by final, we will document it as future work.
Timeline and Milestones
Today is Sept 30, 2025. The project has two key deadlines:
Interim Presentation: Oct 14, 2025 (with preparation finalized by Oct 8).
Final Presentation: Dec 2, 2025.
Below is the timeline with milestones and deliverables:
Week of Sept 30 – Oct 6, 2025: Project Setup & Initial Prototype
Setup Repository: Create a GitHub repository for the project. Initialize it with a README outlining the project goals. Both team members will have access and follow a consistent commit practice.
Environment Configuration: Set up development environment on Windows machines. Install Anki Desktop (Windows). Install marker-pdf via pip in a Python virtual environment. Test with a sample PDF to ensure the library works correctly.
Initial Conversion Test: Run marker-pdf on a small PDF to verify output. Examine the Markdown for structure and content fidelity (e.g., are headings correctly identified, are images referenced, etc.).
API Access: Ensure we have access to a GPT-based API (e.g., OpenAI API key or similar). Write a simple test script that calls the API with a trivial prompt to verify connectivity.
Prototype Prompt: Draft a basic prompt for flashcard generation. For example, take a short text and see if the API can output one Q&A pair. This is to gauge the format and any issues in parsing the response.
👍 Milestone (End of week): Achieve an end-to-end mini prototype – e.g., convert one page of a PDF to Markdown, feed it to the AI with our prompt, and get at least one Q&A pair. This prototype will help identify issues early (like formatting or API limitations).
Oct 7 – Oct 13, 2025: Interim Demo Preparation
Integrate Steps: Connect the pieces into a cohesive pipeline. Develop a script or notebook that takes a PDF file input and goes through Step 1 and 2 automatically, producing a set of flashcards. Minimal error handling is fine for now (assuming well-formed input).
Generate Sample Output: Choose 1-2 example documents (one lecture slide deck, one research paper excerpt) and generate a small set of flashcards from each. Refine the prompt based on the output quality. Possibly adjust how we chunk the input if needed.
Review Card Quality: Both team members review the generated cards. Check if the questions make sense and answers are correct. If the AI introduced errors (possible with technical content), make note. We might not have time to fix all content issues, but we should be aware of limitations to mention.
Interim Presentation Prep: Create slides for the interim presentation (5-10 minutes). Content to include:
Project motivation and objective.
System architecture/pipeline (diagram showing PDF -> Markdown -> AI -> Anki).
Demo of the prototype (e.g., show the Markdown output snippet and a couple of generated Q&A cards).
Early findings (what works, challenges like “long text summarization” or “math formula handling”).
Next steps (what we plan before final).
Possibly include a short live demo if feasible (e.g., show running the script on a small PDF and then showing the output cards). If live demo is risky, prepare screenshots of each step for the slides.
👍 Milestone (Oct 8): Interim demo ready – All components working in a basic way, and slides drafted. Do a practice run of the presentation to ensure timing and that the demo elements (if any) work on the presentation computer.
Oct 14, 2025: Interim Presentation
Deliver the presentation to the class/instructors, demonstrating the progress.
Gather feedback, especially on approach (maybe suggestions on improving card quality or additional features).
Discuss any scope adjustments if recommended by mentors (for example, if the project is too ambitious or not ambitious enough, adjust accordingly after this point).
Mid October – Early November 2025: Development and Refinement
Improve Flashcard Generation: Using feedback, improve the prompt or logic. For instance, if certain important details were missed by the AI, consider splitting input differently or explicitly instructing the AI to cover specific sections. We might introduce some preprocessing, e.g., extracting section titles from Markdown and ensuring at least one card per section.
Error Handling: Make the pipeline more robust. Handle cases like: marker-pdf fails on a PDF (have a fallback or meaningful error message), AI returns fewer cards than requested (maybe ask for more or adjust prompt), or outputs that contain markdown or references (clean them).
Testing on Various PDFs: Each team member will try at least one new PDF (not used before) – e.g., a different style lecture notes or a different field paper – to see how the pipeline handles it. Document results and any needed tweaks.
Begin Add-on Research: Start looking into Anki add-on development. By end of October, decide whether to proceed with building a simple add-on. If yes, create a plan:
Review Anki’s add-on documentation and existing simple add-ons for reference.
Outline how our add-on would work (likely a menu action that calls an external script or Python code to handle the PDF-to-cards pipeline).
Set up a development environment for the add-on (Anki add-ons are typically written in Python and can be tested by placing them in Anki’s add-on folder).
If this looks feasible, allocate time to implement in November. If it seems too complex, plan to demonstrate an automation concept via script + AnkiConnect instead.
November 2025: Implementation of Stretch Goal & Final Touches
Anki Add-on Development (early-to-mid Nov): If proceeding, develop a basic Anki add-on. For the demo, it could be simple: e.g., a button “Convert PDF to Cards” that when pressed, opens a file picker for PDF, then calls our Python conversion/generation logic (which might run as a separate process or within the add-on if possible), and finally adds the cards to the current deck. Ensure this is tested with a sample PDF.
If using AnkiConnect instead: write a script that does the same but uses AnkiConnect’s API to add cards. This script could be run outside Anki (so the workflow would be: user runs our script, it calls marker-pdf and AI, then calls AnkiConnect to create notes directly in Anki). Test that this works with Anki open.
Performance Considerations: If some PDFs are large, test how long conversion and generation take. We may need to note that very large documents might be slow. Optimize where possible (e.g., convert only needed pages for demo, or limit number of cards).
Finalize Documentation: Update the project README and prepare a short user guide (for demo purposes) explaining how to run the tool and import cards. This is useful if we distribute the code or if instructors want to test it.
Buffer for Issues: Leave some buffer time in case any component is troublesome (e.g., marker-pdf on Windows issues – we have time to adapt, maybe run on a server or use an alternate PDF-to-text method as backup, though marker is preferred).
👍 Milestone (Mid/Late Nov): Feature complete – The core pipeline is solid and (if targeted) the add-on or automation is functioning in a basic form. Begin focusing on final presentation.
End of November 2025: Testing & Final Presentation Prep
Comprehensive Testing: Run through the entire demo workflow multiple times with the final setup: from picking a PDF, generating cards, to importing them (or using the add-on). Make sure it works on the presentation machine offline (in case no internet, we might need to run the AI part with a cached result or ensure internet access for the API). Prepare contingencies like saving a set of generated cards in case the live generation fails due to network or API issues during the presentation.
Prepare Final Presentation (5–10 min): Emphasize the end-to-end demo. The presentation will likely include:
Problem & motivation (why automating flashcard creation is useful).
Solution approach recap (maybe a refined diagram of the pipeline including any add-on integration).
Live Demo or Recorded Demo: Show the tool in action – e.g., select a PDF, run conversion, show the generated flashcards, and show them in Anki. This will be the highlight if everything works smoothly. (We will practice this to fit in the time window).
Results: Discuss how well it worked on our test documents (perhaps how many cards generated, any interesting observations).
Challenges faced and how we solved them (e.g., dealing with large content, ensuring quality of questions, technical integration on Windows, etc.).
Future work: mention remaining tasks (for example, fully refining the add-on, improving question quality with more advanced NLP, or handling image-based cards, etc.).
Visual Aids: Possibly include a short video/gif of the conversion process or a screenshot of an example card deck generated, to make it tangible. Ensure any text on slides is readable (not too code-heavy for a general audience).
Rehearsal: Both members practice the presentation delivery, coordinating who says what. Time it to stay within 10 minutes. Verify that any live demo parts run quickly enough (we might pre-convert a PDF to avoid waiting on stage, or have the AI output ready to speed up the demonstration).
Dec 2, 2025: Final Presentation
Present the completed demo project to the audience. Show how a PDF is turned into flashcards seamlessly. Highlight the learning and development experience (including the use of Cursor for vibe coding, see below).
If the add-on is implemented: demonstrate using the Anki GUI (this will impress the automation aspect). If not, demonstrate the manual import process (still a win compared to creating cards by hand from scratch).
Engage with any questions on methodology or future improvements.
Team Roles and Collaboration
Our team consists of two graduate students working collaboratively. We plan to divide responsibilities but also work together closely on integration:
Member 1 (e.g., Alice) – Focus on the PDF conversion pipeline and system integration. This includes using marker-pdf library, handling the conversion output, and ensuring the data flows into the card generation step. Alice will also oversee how the output is formatted for Anki import (writing the parser/formatter for Q&A pairs). She will take lead on any Windows-specific setup issues.
Member 2 (e.g., Bob) – Focus on the AI prompt engineering and flashcard generation logic. Bob will design and refine the prompts used for the GPT API, handle calling the API, and parse its responses into a usable form. He will test different approaches to improve the quality of the flashcards. Bob may also research the Anki add-on development since it involves Python coding that ties into the output of step 2.
Collaboration and Version Control: We’ll use the GitHub repository for all code. Both members will create feature branches for major features (e.g., pdf-conversion, anki-output, addon-experiment etc.) and use pull requests to review each other’s code. Regular commits and clear commit messages are expected. Issues or a project board will track tasks and progress, ensuring we stay on schedule.
Cursor & Vibe Coding: A unique requirement is to use Cursor for “vibe coding” sessions. This means the team will engage in pair-programming style development using the Cursor editor (which likely provides AI assistance for coding as well). We plan to schedule regular joint coding sessions (possibly using Cursor’s live share or by sitting together) where we work on challenging parts of the code, leveraging AI suggestions to speed up mundane coding tasks or get hints. This not only helps in writing code but also fulfills the experiential requirement. We will document these sessions (perhaps by keeping a log of what was done with AI help) to mention in our reports/presentation if needed (since “experience vibe coding” is important to demonstrate).
Tools and Technology Stack
marker-pdf (PDF to Markdown) – The core conversion tool. We will use it as a Python library in our development environment. It's open-source and supports advanced PDF parsing features that are crucial for our PDF content, including deep learning-based layout detection and OCR. Installation is simple via pip (`pip install marker-pdf`), and it handles dependencies automatically.
Programming Language – Python will be used for scripting the pipeline (calling marker-pdf, invoking the AI API, processing outputs). Python is also needed if we develop an Anki add-on or use libraries for creating Anki decks.
AI API – Likely OpenAI GPT-4 (or GPT-3.5 if cost or speed is a concern) via their REST API. We will use it for natural language generation. We need internet access during development and possibly during demo (if live). If internet is an issue for the final demo, we might explore an offline model for demonstration (less likely given complexity; instead, we’ll ensure internet or use a pre-generated example).
Anki Desktop – Version 2.1+ on Windows. This is the target application for the flashcards. We will familiarize ourselves with its import format and, if doing an add-on, its internal APIs.
AnkiConnect (optional) – If we use the AnkiConnect route for automation, this is an existing Anki add-on that we will install. It provides a localhost JSON API. Using it would require the Anki app to be running during the card creation process.
genanki (optional) – As an alternative method, we could use the genanki Python library to programmatically assemble an .apkg Anki deck package. This way, our script could directly output a deck file that can be opened in Anki. We haven’t committed to this approach because manual import via text is straightforward, but we keep it in mind if time permits or if it simplifies the demonstration (e.g., generating an .apkg in one go).
Development Tools:
Cursor Editor: for coding with AI assistance.
VSCode/PyCharm as needed (particularly if debugging or for editing Anki add-on, which might need an IDE).
Python on Windows (for running marker-pdf as a local service; simple server mode is sufficient).
Git for version control (with GitHub).
Documentation & Communication:
We will maintain documentation in the repo (README, maybe a Wiki or docs folder) for how to run the project.
For communication, aside from in-person/Zoom meetings, we might use GitHub Issues to discuss and record decisions.
If required by our course, we’ll also prepare any written reports describing the project development.
Risks and Challenges
PDF Conversion Accuracy: While marker-pdf is powerful, there’s a risk that some PDFs might not convert cleanly (e.g., unusual formatting, OCR issues if PDFs are scanned images). We mitigate this by testing early and, if a PDF is problematic, possibly pre-processing it (e.g., ensure it’s a text-based PDF, or limit to a range of pages). We’ll also keep marker-pdf updated to latest version in case of bug fixes.
Large Content & AI Limitations: A full lecture note or paper can be long. GPT-4 has input token limits, and summarizing or selecting important points is non-trivial. The AI might also sometimes generate incorrect answers or nonsensical questions if the prompt or context isn’t clear enough. Our strategy is to iterate on prompt design, and possibly break the content into smaller chunks. If needed, for the demo, we might restrict to processing a portion of the document (e.g., a chapter or a section) to ensure quality over quantity. We will also manually review outputs as needed to avoid showing any blatantly wrong flashcard in presentations (noting that in a real scenario, user review is wise).
Time Constraint for Add-on: Implementing a full Anki add-on in a few weeks (while also perfecting the core pipeline) is ambitious for two students. We recognize this and have labeled it a stretch goal. The risk is we spend too much time on it and neglect core functionality. To manage this, we will only start serious add-on development after the interim if the core pipeline is solid. If time is short, we will limit ourselves to demonstrating the concept (maybe a partial automation or just describing how it would work) rather than a fully polished add-on.
Windows/WSL Environment Issues: Some tools (especially PDF parsing libraries) can be tricky on native Windows. We will run marker-pdf inside WSL (Linux userspace) and ensure required Python dependencies are installed there. Confirm localhost access across WSL↔Windows and handle Windows firewall or loopback as needed. We will test on the target machine thoroughly.
Collaboration & Version Control: There’s a risk in any team project of merge conflicts or duplication of work. To mitigate, we’ll communicate frequently, use branches, and perform code reviews. The use of Cursor for pair programming also helps keep both members on the same page and can reduce integration issues (since we’ll often be coding together for core parts).
Demo Risks: Live demos can fail (network outage, API rate-limit, etc.). We will have backup plans: for instance, have a set of pre-generated cards or a cached API response to use if the live call doesn’t work. We’ll also inform our instructors of any requirement like internet for the demo in advance, or run a local instance of a smaller LLM if absolutely needed (as a backup, though quality may differ).
Conclusion
By following this plan, we aim to deliver a successful demo that showcases the end-to-end process of generating Anki flashcards from PDF materials. The project not only solves a practical problem (saving students time and enhancing studying) but also gives our team experience in integrating multiple tools and AI services, and in collaborative “vibe coding” development. We have a clear timeline leading up to the interim check-in on Oct 14 and final presentation on Dec 2. By focusing on core functionality first and then exploring stretch goals, we increase our chances of having a working product to show. With ongoing testing and prompt refinement, we’re confident the demo will illustrate the concept effectively. Lastly, any feedback at interim will be incorporated to improve the final outcome. We look forward to demonstrating the PDF-to-Anki Card Generator and possibly surprising the audience with how quickly one can turn a dense PDF into a handy deck of flashcards!

Sources


No file chosenNo file chosen
ChatGPT can make mistakes. Check important info.

Project Plan: PDF-to-Anki Card Generator Demo
Objective and Overview
The goal is to develop a demo application that automatically generates Anki flashcards from PDF documents (e.g., lecture slides or scientific papers). This will streamline the creation of study flashcards by extracting key information from PDFs and converting it into question-answer card format. The project focuses on implementing a pipeline with the following steps:
PDF to Markdown Conversion – Use an open-source tool (marker-pdf) to convert PDF content into Markdown text for easier processing.
Flashcard Content Generation – Feed the Markdown content into an AI (via API) to generate flashcard questions and answers in a Basic Anki card format.
Card Import into Anki – Import the generated cards into the Anki desktop application (manually for the demo).
(Stretch Goal) Anki Add-on Integration – Optionally, create an Anki add-on to automate the import process (planned after the interim demo).
This demo will handle textbook-style lecture notes and journal articles, including content with figures and equations. The interim focus is on Steps 1–3, while Step 4 is a future enhancement (not required for the interim presentation).
Project Scope and Requirements
Input PDF Types: Lecture slides and academic papers, which may contain formatted text, images, tables, and mathematical equations. The conversion tool (marker-pdf) supports advanced formatting – it can extract images and tables, and even convert math equations to LaTeX
github.com
, ensuring that complex content is preserved in Markdown form.
Output Flashcards: Basic Anki cards with a front (question) and back (answer). The flashcards will target key facts or concepts from the PDF. For example, a slide about a definition could become a “What is X?” card. We will let the user specify the number of cards to generate and possibly the focus (e.g. definitions, concepts, or questions covering each section).
No Pre-trained Model: We are not training a custom model. Instead, we will use an API (likely a GPT-4 based service) to generate flashcard text from the Markdown. Prompt engineering will be crucial to guide the AI to produce useful Q&A pairs.
Platform: Development and demo will be on Windows (the team’s working OS), so all tools must run on Windows. marker-pdf can be run via a local server or Docker container (it supports both CPU and GPU, with easy Docker setup
github.com
), which we will configure on Windows. Anki Desktop (Windows version) will be used to import and display the cards.
Methodology and Approach
Step 1: PDF to Markdown Conversion
Tool: We will use marker-pdf (GitHub: adithya-s-k/marker-api) to convert PDFs to Markdown. marker-pdf provides a REST endpoint to convert PDFs “quickly and accurately” into Markdown format
github.com
. It’s an open-source, easily deployable service which we can run locally. Key advantages: it preserves formatting, extracts images/tables, and even handles math equations by converting them to LaTeX syntax
github.com
. This suits our needs for lecture notes with formulas or papers with equations.
Setup: The team will install marker-pdf on the development machine. We have two options:
Local Python Server: Install via pip/Poetry and run server.py (as per marker-pdf docs)
github.com
. This may require setting up a Python environment and ensuring dependencies (like PyMuPDF, etc.) are installed.
Docker Container: Use the provided Docker image or Dockerfile (marker-pdf has CPU/GPU Docker support
github.com
) to avoid dependency issues on Windows. We will likely use the CPU Docker image (since GPU isn’t necessary for PDF parsing) and expose the API on a localhost port (e.g., 8080).
Execution: Once set up, using marker-pdf is straightforward: we send an HTTP request with the PDF, and it returns Markdown. We’ll write a small wrapper script in Python to call this API (e.g., using requests). This script will feed a PDF file and retrieve the Markdown text.
Output Handling: The returned Markdown will contain the textual content of the PDF, including any images (usually referenced as image files) and LaTeX for equations. For the demo’s scope, text content will be the primary source for flashcards. Non-text elements:
Images: We will note that images are extracted by marker-pdf (placed in a folder, referenced in Markdown). However, generating flashcard Q&A from images automatically is complex and out-of-scope. We might simply ignore direct image-based questions for now. (If needed, we could include a few manually or as future work).
Equations: Since equations are converted to LaTeX, the AI could generate questions about them (e.g., “What does the following equation represent: …?”). Anki supports LaTeX in cards, so we will ensure the LaTeX text is wrapped properly so Anki can render it (Anki uses MathJax for LaTeX). We will test a sample equation card.
Verification: We’ll test marker-pdf on a couple of sample PDFs (one lecture slide deck, one paper) early on. This ensures the conversion quality is acceptable (e.g., headings, bold text, etc., come through in Markdown) and to see how large the Markdown gets for a typical document. This informs how we prompt the AI in Step 2 (since very large Markdown might need splitting or summarizing).
Step 2: Generating Anki Cards from Markdown
Approach: We will use an AI text-generation API (likely OpenAI GPT-4 or similar) to transform the Markdown content into a set of flashcard Q&A pairs. The procedure will be:
Prompt Design: Create a prompt template that instructs the model to produce flashcards. For example: “You are an assistant that creates flashcards. Given the following content extracted from a lecture or article, generate X flashcards in Q&A format suitable for Anki (basic card). Focus on key concepts, definitions, or important details. Provide output as a list of 'Question: ... Answer: ...' pairs.” We will fine-tune the wording of this prompt to get the desired output style.
Feeding Content: Insert the Markdown text (or a relevant portion of it) into the prompt. If the PDF content is very large (e.g., a long article), we might not send the entire text at once to avoid token limits. In that case, possible strategies include:
Splitting the content by sections and generating a few cards per section, then combining results.
Or summarizing the text first (though that risks missing details for specific flashcards).
We will experiment with a manageable size first (perhaps 5-10 pages) and scale up if possible.
Choosing Number of Cards: Allow the user (for demo purposes, ourselves) to specify the number of cards (e.g., 5, 10, 15) to generate. This will be a parameter in the prompt. The model will then try to output that many Q&A pairs. We’ll have to ensure the prompt clearly asks for a specific number of distinct Q&As and maybe enumerate them to be sure none are missed.
Ensuring Format: We need the output in a format that can be easily imported or parsed. Likely, we will use a simple delimiter format (each Q&A separated by a line break, with question and answer separated by a known token or just labeled). For example:
Q: What is ...?  
A: It is ...  
Or Question: ... Answer: ... on separate lines. We will parse this to create a tab-separated text for Anki import. We must instruct the AI not to produce extraneous text beyond the QA pairs.
Development: Implement a Python script that calls the AI API. This includes managing API keys securely (not hardcoding in the repo) and handling the response parsing. We will test this with small dummy content first (e.g., a paragraph of text) to verify the format.
Prompt Tuning & Testing: Generating good flashcards might require iterative prompt tuning. We’ll check:
Are the questions relevant and clear?
Are the answers correct and complete enough (not too verbose, just enough to answer the question)?
Do they cover important points from the text?
If the initial results are unsatisfactory, we may adjust instructions (e.g., “make questions concise,” “avoid trivial details,” or specify the style of questions). We might also post-process the answers (for example, if the answer text includes Markdown artifacts or references from the PDF, clean those out).
Handling Figures/Equations: As noted, fully automating question generation for images is out-of-scope. However, for equations in LaTeX, the AI might include them in questions or answers. We will verify that the LaTeX is intact. When importing to Anki, we’ll ensure the card type is set to render LaTeX (Anki by default can render if the content is enclosed in [latex]...[/latex] or between $ $). We will document how to handle this for the demo (perhaps instruct the AI to put $...$ around LaTeX so it displays as math in Anki).
Step 3: Importing Cards into Anki (Demo Procedure)
Output Format for Import: We plan to take the AI-generated Q&A pairs and format them into a file that Anki can import. The simplest is a tab-separated or comma-separated CSV file with two columns: front and back. For example:
What is Newton's first law of motion?\tEvery object will remain at rest or in uniform motion in a straight line unless compelled to change its state by the action of an external force.
Each line represents one card. We will generate such a file (e.g., cards.txt or cards.csv). If using tabs, it can be a .txt which Anki will parse with tab as the delimiter. We’ll avoid characters that might interfere with CSV format in the content (commas, newlines inside an answer – if an answer is multi-line, we might need to handle that or keep it one line).
Manual Import Process: For the demo, the import will be done manually through Anki’s GUI:
Open Anki on the demo machine (Windows laptop).
Create or select a target deck for the cards.
Use File > Import and select the generated cards.txt file.
In the import dialog, ensure it’s set to “Notes separated by tab” (if we use tab) and map the first field as Front, second as Back of a Basic note type.
Complete the import and verify that the cards appear in the deck.
Verification: We will test this import process beforehand with a sample file to ensure formatting is correct (for instance, check that question marks or special characters aren’t causing issues, and LaTeX formulas appear correctly in Anki’s review mode). If LaTeX is used, we’ll verify Anki’s LaTeX support is working (typically requires having LaTeX installed or using the built-in MathJax; in modern Anki, MathJax is included). We should document any setup needed (maybe none if using MathJax which is default).
Demo Presentation Usage: In the interim presentation, we might show the content of the generated file and a quick import (or have a few cards pre-imported to demonstrate). For final presentation, if time permits, a live demo of selecting a PDF and going through the pipeline to Anki would be ideal. If a live demo is risky, we will prepare a short video or screenshots showing each step.
Step 4: Anki Add-on Automation (Stretch Goal)
This step is planned after the interim presentation, as a stretch goal towards the final. The idea is to eliminate the manual import (Step 3) by integrating the functionality as an Anki add-on or using an automation API. Possible approaches:
Anki Add-on (Plugin): Develop a custom add-on in Python that runs inside Anki. This could add a menu option or button in Anki (e.g., “Import from PDF via marker-pdfAI”) which when clicked, prompts the user to select a PDF, then behind the scenes calls our conversion and generation pipeline, and finally creates new cards in the deck automatically.
Feasibility: Anki’s add-ons are written in Python and can call external scripts or Python code. We’d package our logic into the add-on, ensuring it can call the marker-pdf (maybe by running the conversion as a subprocess or requiring the user to have the marker-pdf running locally) and use Anki’s API to add cards to the collection. This might be complex to do fully by Dec 2, but we will research it.
AnkiConnect: Alternatively, use the AnkiConnect plugin (a popular add-on that exposes a localhost API to Anki). Our code (running outside Anki) could send a request to AnkiConnect with the new cards. This approach means we don’t have to write a full add-on UI, just ensure AnkiConnect is installed. It might be simpler, but it requires the user to run our script separately.
Planned Decision: After the interim demo, we will evaluate which approach is more doable in the remaining time. If the add-on path is chosen, we’ll allocate time to learn Anki’s add-on structure. If it seems too time-consuming, we might implement a basic solution with AnkiConnect as a proof-of-concept by final presentation. In either case, this feature is beyond the core demo; if we cannot fully implement it by final, we will document it as future work.
Timeline and Milestones
Today is Sept 30, 2025. The project has two key deadlines:
Interim Presentation: Oct 14, 2025 (with preparation finalized by Oct 8).
Final Presentation: Dec 2, 2025.
Below is the timeline with milestones and deliverables:
Week of Sept 30 – Oct 6, 2025: Project Setup & Initial Prototype
Setup Repository: Create a GitHub repository for the project. Initialize it with a README outlining the project goals. Both team members will have access and follow a consistent commit practice.
Environment Configuration: Set up development environment on Windows machines. Install Anki Desktop. Install marker-pdf (try Docker setup first for ease on Windows). Ensure we can run the marker-pdf server locally and it’s accessible (test with a sample PDF).
Initial Conversion Test: Run marker-pdf on a small PDF to verify output. Examine the Markdown for structure and content fidelity (e.g., are headings correctly identified, are images referenced, etc.).
API Access: Ensure we have access to a GPT-based API (e.g., OpenAI API key or similar). Write a simple test script that calls the API with a trivial prompt to verify connectivity.
Prototype Prompt: Draft a basic prompt for flashcard generation. For example, take a short text and see if the API can output one Q&A pair. This is to gauge the format and any issues in parsing the response.
👍 Milestone (End of week): Achieve an end-to-end mini prototype – e.g., convert one page of a PDF to Markdown, feed it to the AI with our prompt, and get at least one Q&A pair. This prototype will help identify issues early (like formatting or API limitations).
Oct 7 – Oct 13, 2025: Interim Demo Preparation
Integrate Steps: Connect the pieces into a cohesive pipeline. Develop a script or notebook that takes a PDF file input and goes through Step 1 and 2 automatically, producing a set of flashcards. Minimal error handling is fine for now (assuming well-formed input).
Generate Sample Output: Choose 1-2 example documents (one lecture slide deck, one research paper excerpt) and generate a small set of flashcards from each. Refine the prompt based on the output quality. Possibly adjust how we chunk the input if needed.
Review Card Quality: Both team members review the generated cards. Check if the questions make sense and answers are correct. If the AI introduced errors (possible with technical content), make note. We might not have time to fix all content issues, but we should be aware of limitations to mention.
Interim Presentation Prep: Create slides for the interim presentation (5-10 minutes). Content to include:
Project motivation and objective.
System architecture/pipeline (diagram showing PDF -> Markdown -> AI -> Anki).
Demo of the prototype (e.g., show the Markdown output snippet and a couple of generated Q&A cards).
Early findings (what works, challenges like “long text summarization” or “math formula handling”).
Next steps (what we plan before final).
Possibly include a short live demo if feasible (e.g., show running the script on a small PDF and then showing the output cards). If live demo is risky, prepare screenshots of each step for the slides.
👍 Milestone (Oct 8): Interim demo ready – All components working in a basic way, and slides drafted. Do a practice run of the presentation to ensure timing and that the demo elements (if any) work on the presentation computer.
Oct 14, 2025: Interim Presentation
Deliver the presentation to the class/instructors, demonstrating the progress.
Gather feedback, especially on approach (maybe suggestions on improving card quality or additional features).
Discuss any scope adjustments if recommended by mentors (for example, if the project is too ambitious or not ambitious enough, adjust accordingly after this point).
Mid October – Early November 2025: Development and Refinement
Improve Flashcard Generation: Using feedback, improve the prompt or logic. For instance, if certain important details were missed by the AI, consider splitting input differently or explicitly instructing the AI to cover specific sections. We might introduce some preprocessing, e.g., extracting section titles from Markdown and ensuring at least one card per section.
Error Handling: Make the pipeline more robust. Handle cases like: marker-pdf fails on a PDF (have a fallback or meaningful error message), AI returns fewer cards than requested (maybe ask for more or adjust prompt), or outputs that contain markdown or references (clean them).
Testing on Various PDFs: Each team member will try at least one new PDF (not used before) – e.g., a different style lecture notes or a different field paper – to see how the pipeline handles it. Document results and any needed tweaks.
Begin Add-on Research: Start looking into Anki add-on development. By end of October, decide whether to proceed with building a simple add-on. If yes, create a plan:
Review Anki’s add-on documentation and existing simple add-ons for reference.
Outline how our add-on would work (likely a menu action that calls an external script or Python code to handle the PDF-to-cards pipeline).
Set up a development environment for the add-on (Anki add-ons are typically written in Python and can be tested by placing them in Anki’s add-on folder).
If this looks feasible, allocate time to implement in November. If it seems too complex, plan to demonstrate an automation concept via script + AnkiConnect instead.
November 2025: Implementation of Stretch Goal & Final Touches
Anki Add-on Development (early-to-mid Nov): If proceeding, develop a basic Anki add-on. For the demo, it could be simple: e.g., a button “Convert PDF to Cards” that when pressed, opens a file picker for PDF, then calls our Python conversion/generation logic (which might run as a separate process or within the add-on if possible), and finally adds the cards to the current deck. Ensure this is tested with a sample PDF.
If using AnkiConnect instead: write a script that does the same but uses AnkiConnect’s API to add cards. This script could be run outside Anki (so the workflow would be: user runs our script, it calls marker-pdf and AI, then calls AnkiConnect to create notes directly in Anki). Test that this works with Anki open.
Performance Considerations: If some PDFs are large, test how long conversion and generation take. We may need to note that very large documents might be slow. Optimize where possible (e.g., convert only needed pages for demo, or limit number of cards).
Finalize Documentation: Update the project README and prepare a short user guide (for demo purposes) explaining how to run the tool and import cards. This is useful if we distribute the code or if instructors want to test it.
Buffer for Issues: Leave some buffer time in case any component is troublesome (e.g., marker-pdf on Windows issues – we have time to adapt, maybe run on a server or use an alternate PDF-to-text method as backup, though marker is preferred).
👍 Milestone (Mid/Late Nov): Feature complete – The core pipeline is solid and (if targeted) the add-on or automation is functioning in a basic form. Begin focusing on final presentation.
End of November 2025: Testing & Final Presentation Prep
Comprehensive Testing: Run through the entire demo workflow multiple times with the final setup: from picking a PDF, generating cards, to importing them (or using the add-on). Make sure it works on the presentation machine offline (in case no internet, we might need to run the AI part with a cached result or ensure internet access for the API). Prepare contingencies like saving a set of generated cards in case the live generation fails due to network or API issues during the presentation.
Prepare Final Presentation (5–10 min): Emphasize the end-to-end demo. The presentation will likely include:
Problem & motivation (why automating flashcard creation is useful).
Solution approach recap (maybe a refined diagram of the pipeline including any add-on integration).
Live Demo or Recorded Demo: Show the tool in action – e.g., select a PDF, run conversion, show the generated flashcards, and show them in Anki. This will be the highlight if everything works smoothly. (We will practice this to fit in the time window).
Results: Discuss how well it worked on our test documents (perhaps how many cards generated, any interesting observations).
Challenges faced and how we solved them (e.g., dealing with large content, ensuring quality of questions, technical integration on Windows, etc.).
Future work: mention remaining tasks (for example, fully refining the add-on, improving question quality with more advanced NLP, or handling image-based cards, etc.).
Visual Aids: Possibly include a short video/gif of the conversion process or a screenshot of an example card deck generated, to make it tangible. Ensure any text on slides is readable (not too code-heavy for a general audience).
Rehearsal: Both members practice the presentation delivery, coordinating who says what. Time it to stay within 10 minutes. Verify that any live demo parts run quickly enough (we might pre-convert a PDF to avoid waiting on stage, or have the AI output ready to speed up the demonstration).
Dec 2, 2025: Final Presentation
Present the completed demo project to the audience. Show how a PDF is turned into flashcards seamlessly. Highlight the learning and development experience (including the use of Cursor for vibe coding, see below).
If the add-on is implemented: demonstrate using the Anki GUI (this will impress the automation aspect). If not, demonstrate the manual import process (still a win compared to creating cards by hand from scratch).
Engage with any questions on methodology or future improvements.
Team Roles and Collaboration
Our team consists of two graduate students working collaboratively. We plan to divide responsibilities but also work together closely on integration:
Member 1 (e.g., Alice) – Focus on the PDF conversion pipeline and system integration. This includes setting up marker-pdf, handling the conversion output, and ensuring the data flows into the card generation step. Alice will also oversee how the output is formatted for Anki import (writing the parser/formatter for Q&A pairs). She will likely take lead on any Windows-specific setup issues or Docker configuration needed for marker-pdf.
Member 2 (e.g., Bob) – Focus on the AI prompt engineering and flashcard generation logic. Bob will design and refine the prompts used for the GPT API, handle calling the API, and parse its responses into a usable form. He will test different approaches to improve the quality of the flashcards. Bob may also research the Anki add-on development since it involves Python coding that ties into the output of step 2.
Collaboration and Version Control: We’ll use the GitHub repository for all code. Both members will create feature branches for major features (e.g., pdf-conversion, anki-output, addon-experiment etc.) and use pull requests to review each other’s code. Regular commits and clear commit messages are expected. Issues or a project board will track tasks and progress, ensuring we stay on schedule.
Cursor & Vibe Coding: A unique requirement is to use Cursor for “vibe coding” sessions. This means the team will engage in pair-programming style development using the Cursor editor (which likely provides AI assistance for coding as well). We plan to schedule regular joint coding sessions (possibly using Cursor’s live share or by sitting together) where we work on challenging parts of the code, leveraging AI suggestions to speed up mundane coding tasks or get hints. This not only helps in writing code but also fulfills the experiential requirement. We will document these sessions (perhaps by keeping a log of what was done with AI help) to mention in our reports/presentation if needed (since “experience vibe coding” is important to demonstrate).
Tools and Technology Stack
marker-pdf (PDF to Markdown) – The core conversion tool. We will run it as a local service on our development machine. It’s open-source (GPL-3.0) and supports advanced PDF parsing features that are crucial for our PDF content
github.com
. Running it may involve Docker or a Python environment with dependencies like PyMuPDF, Camelot (for tables), etc. We will adhere to its guidelines for installation (possibly using the simple server mode for our scale).
Programming Language – Python will be used for scripting the pipeline (calling marker-pdf, invoking the AI API, processing outputs). Python is also needed if we develop an Anki add-on or use libraries for creating Anki decks.
AI API – Likely OpenAI GPT-4 (or GPT-3.5 if cost or speed is a concern) via their REST API. We will use it for natural language generation. We need internet access during development and possibly during demo (if live). If internet is an issue for the final demo, we might explore an offline model for demonstration (less likely given complexity; instead, we’ll ensure internet or use a pre-generated example).
Anki Desktop – Version 2.1+ on Windows. This is the target application for the flashcards. We will familiarize ourselves with its import format and, if doing an add-on, its internal APIs.
AnkiConnect (optional) – If we use the AnkiConnect route for automation, this is an existing Anki add-on that we will install. It provides a localhost JSON API. Using it would require the Anki app to be running during the card creation process.
genanki (optional) – As an alternative method, we could use the genanki Python library to programmatically assemble an .apkg Anki deck package. This way, our script could directly output a deck file that can be opened in Anki. We haven’t committed to this approach because manual import via text is straightforward, but we keep it in mind if time permits or if it simplifies the demonstration (e.g., generating an .apkg in one go).
Development Tools:
Cursor Editor: for coding with AI assistance.
VSCode/PyCharm as needed (particularly if debugging or for editing Anki add-on, which might need an IDE).
WSL (Ubuntu) on Windows (for running marker-pdf as a local Python service; simple server mode is sufficient).
Git for version control (with GitHub).
Documentation & Communication:
We will maintain documentation in the repo (README, maybe a Wiki or docs folder) for how to run the project.
For communication, aside from in-person/Zoom meetings, we might use GitHub Issues to discuss and record decisions.
If required by our course, we’ll also prepare any written reports describing the project development.
Risks and Challenges
PDF Conversion Accuracy: While marker-pdf is powerful, there’s a risk that some PDFs might not convert cleanly (e.g., unusual formatting, OCR issues if PDFs are scanned images). We mitigate this by testing early and, if a PDF is problematic, possibly pre-processing it (e.g., ensure it’s a text-based PDF, or limit to a range of pages). We’ll also keep marker-pdf updated to latest version in case of bug fixes.
Large Content & AI Limitations: A full lecture note or paper can be long. GPT-4 has input token limits, and summarizing or selecting important points is non-trivial. The AI might also sometimes generate incorrect answers or nonsensical questions if the prompt or context isn’t clear enough. Our strategy is to iterate on prompt design, and possibly break the content into smaller chunks. If needed, for the demo, we might restrict to processing a portion of the document (e.g., a chapter or a section) to ensure quality over quantity. We will also manually review outputs as needed to avoid showing any blatantly wrong flashcard in presentations (noting that in a real scenario, user review is wise).
Time Constraint for Add-on: Implementing a full Anki add-on in a few weeks (while also perfecting the core pipeline) is ambitious for two students. We recognize this and have labeled it a stretch goal. The risk is we spend too much time on it and neglect core functionality. To manage this, we will only start serious add-on development after the interim if the core pipeline is solid. If time is short, we will limit ourselves to demonstrating the concept (maybe a partial automation or just describing how it would work) rather than a fully polished add-on.
Windows Environment Issues: Some tools (especially those involving machine learning or PDF parsing libraries) can be tricky on Windows (library compatibility, path issues, etc.). Using Docker for marker-pdf should alleviate many issues by containerizing the environment. For Anki add-on, we will need to ensure any external calls (to marker-pdf or to an internet API) are allowed – this might need handling of Windows firewall or loopback for AnkiConnect. We will test on our target machine thoroughly.
Collaboration & Version Control: There’s a risk in any team project of merge conflicts or duplication of work. To mitigate, we’ll communicate frequently, use branches, and perform code reviews. The use of Cursor for pair programming also helps keep both members on the same page and can reduce integration issues (since we’ll often be coding together for core parts).
Demo Risks: Live demos can fail (network outage, API rate-limit, etc.). We will have backup plans: for instance, have a set of pre-generated cards or a cached API response to use if the live call doesn’t work. We’ll also inform our instructors of any requirement like internet for the demo in advance, or run a local instance of a smaller LLM if absolutely needed (as a backup, though quality may differ).
Conclusion
By following this plan, we aim to deliver a successful demo that showcases the end-to-end process of generating Anki flashcards from PDF materials. The project not only solves a practical problem (saving students time and enhancing studying) but also gives our team experience in integrating multiple tools and AI services, and in collaborative “vibe coding” development. We have a clear timeline leading up to the interim check-in on Oct 14 and final presentation on Dec 2. By focusing on core functionality first and then exploring stretch goals, we increase our chances of having a working product to show. With ongoing testing and prompt refinement, we’re confident the demo will illustrate the concept effectively. Lastly, any feedback at interim will be incorporated to improve the final outcome. We look forward to demonstrating the PDF-to-Anki Card Generator and possibly surprising the audience with how quickly one can turn a dense PDF into a handy deck of flashcards!
Citations

GitHub - adithya-s-k/marker-api: Easily deployable API to convert PDF to markdown quickly with high accuracy.

https://github.com/adithya-s-k/marker-api

GitHub - adithya-s-k/marker-api: Easily deployable API to convert PDF to markdown quickly with high accuracy.

https://github.com/adithya-s-k/marker-api

GitHub - adithya-s-k/marker-api: Easily deployable API to convert PDF to markdown quickly with high accuracy.

https://github.com/adithya-s-k/marker-api

GitHub - adithya-s-k/marker-api: Easily deployable API to convert PDF to markdown quickly with high accuracy.

https://github.com/adithya-s-k/marker-api
All Sources

github