# Dhairya Kumar — Projects Knowledge Base

## LaunchFolio
LaunchFolio is a live AI resume and portfolio builder, deployed at
launchfolio.tech. Users fill out a simple form and LaunchFolio generates a
professional resume and a personal portfolio site from it. It supports
AI-powered template personalization, multiple template options, and
one-click PDF export. It is built with Node.js, deployed on Cloudflare
Pages, and uses Cloudflare D1 (a SQLite-based database) for storage.
Payments are handled through Razorpay. The project is open-sourced under
the MIT license. LaunchFolio is Dhairya's flagship product — it has real
users on a live custom domain, not just a demo.

## AXiS
AXiS is an agentic AI desktop platform that Dhairya is currently building.
It lives in a floating "Dynamic Island" style UI on the desktop. It can see
the user's screen, listen through voice input, and take actions through
tool-based interactions, similar to how an AI agent reasons and acts rather
than just chatting. It is built with Electron for the desktop app,
FastAPI for the backend, and LangGraph for agent orchestration and
tool-calling logic. AXiS is designed to be modular — Dhairya plans to ship
one useful module at a time (memory, vision, voice, IoT hooks) rather than
building the whole system before releasing anything.

## VisionTrack
VisionTrack is a real-time object detection and tracking system. It uses
YOLOv8 for object detection and Deep SORT for multi-object tracking across
video frames. The backend is built with Python and Flask. It includes a 3D
visualization dashboard built with Three.js, and supports exporting
tracking data to CSV. VisionTrack was built during Dhairya's AI internship
at CodeAlpha.

## Community Hero
Community Hero is a live AI-powered civic issue reporting platform. Users
can report local problems — like a broken streetlight or an overflowing
bin — and the platform uses AI to automatically route each report to the
correct municipal department. It includes real-time maps showing reported
issues. It is built with TypeScript and deployed on Google Cloud Run.

## LexiFlux
LexiFlux is an AI translation suite. It automatically detects the input
language, translates it using the Gemini API, and can read the translation
aloud using native-accent text-to-speech. It also keeps a per-user history
of past translations. It is built with React, TypeScript, and Express, and
was built during Dhairya's AI internship at CodeAlpha.

## Hostel Meal Manager
Hostel Meal Manager is a full-stack web application for tracking hostel
meal registration and food inventory. It automated what used to be manual
admin work, reducing manual effort by roughly 40%. It includes real-time
dashboards showing consumption data so administrators can reduce food
waste. It is built with Next.js, Node.js, and Python.

## Fire Detection System
The Fire Detection System is an embedded hardware project built with an
Arduino Uno and C++. It uses infrared flame sensors to detect fire in real
time, with an optimized polling loop for fast response. When a flame is
detected, it triggers a buzzer and LED alert chain. Through sensor
calibration, it achieves roughly 95% detection accuracy with minimal false
positives.

## Open Source Contribution — KanaDojo
Dhairya is a merged open-source contributor to KanaDojo, an open-source
Japanese learning platform built with Next.js. His contribution, PR #23796,
added a trivia question feature. During the process, he independently
diagnosed and fixed a failing CI pipeline (caused by a malformed JSON file
with an extra trailing bracket) before maintainer review — he found and
fixed the bug himself rather than waiting for help.

## Internship — CodeAlpha
Dhairya completed a one-month remote AI internship at CodeAlpha in June
2026. During the internship he built VisionTrack and LexiFlux, applying
computer vision (YOLOv8, Deep SORT, OpenCV) and generative AI APIs to ship
working applications within project deadlines.
