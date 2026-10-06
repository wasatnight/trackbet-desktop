# TrackBet Desktop

> 🚧 **Status: In active development**

TrackBet is a desktop-oriented sports betting tracker built to record bets, analyze performance, and monitor bankroll evolution locally.

The project is currently under active development. The core application already includes a React interface, a FastAPI backend, and local SQLite persistence.

## Overview

TrackBet is designed to provide a private and structured way to track sports betting activity without depending on spreadsheets or external betting platforms.

The current development version supports the main workflow for recording and reviewing betting activity while additional desktop features are being completed.

## Tech Stack

- React
- JavaScript
- FastAPI
- Python
- SQLite
- Vite

A future desktop release is planned to use Tauri while keeping the existing React + FastAPI + SQLite architecture.

## Current Features

### Dashboard

- Bankroll tracking
- Net profit
- ROI
- Resolved and pending bets
- Pending exposure
- Bankroll evolution

### Bet Registration

- Straight bets
- Parlay bets
- Multiple selections per parlay
- American and decimal odds
- Pre-game and live betting modes
- Stake tracking
- Automatic estimated return
- Automatic potential profit calculation

### Betting History

- Complete betting history
- Straight and parlay visualization
- Search
- Sport filters
- Result filters
- Sorting
- Pagination
- Expandable bet details
- Responsive desktop/mobile interface

### Backend

- REST API built with FastAPI
- Pydantic validation
- SQLite persistence
- Betting calculations
- Bankroll calculations
- ROI calculations
- Parlay settlement logic
- Push handling
- Backup utilities
- CSV reporting utilities

## Architecture

```text
React UI
   │
   │ HTTP / JSON
   ▼
FastAPI
   │
   │ Application logic
   ▼
SQLite
```

The final Windows desktop version is planned to use:
TrackBet Desktop
│
├── Tauri
│ └── React UI
│
└── Local FastAPI service
└── SQLite database
The goal is for TrackBet Desktop to operate locally without requiring a permanent internet connection.
Development Progress
Currently working:

- React frontend
- FastAPI backend
- SQLite local storage
- Dashboard
- Betting history
- Straight bet registration
- Parlay builder
- Financial calculations
- Search and filters
- Responsive interface
- React → FastAPI → SQLite integration
  Currently being developed:
- Full parlay end-to-end validation
- Editing bets from the React interface
- Bet settlement
- Bet deletion
- CSV export from the desktop interface
- Backup and restore interface
- Additional automated API tests
- Windows desktop packaging
  Desktop v1 Goals
  The first desktop release is planned to include:
- Straight and parlay registration
- Bet history and filters
- Edit, settle and delete bets
- Profit and loss statistics
- ROI and win rate
- Bankroll tracking
- CSV export
- Backup and restore
- Local SQLite storage
- Clear error and empty states
- Optional demonstration data
- Windows installer
  Not Planned for v1
  To keep the first release focused, the following features are intentionally outside the current scope:
- iOS or Android applications
- User accounts
- Cloud synchronization
- Payments or subscriptions
- Live sportsbook odds
- Sportsbook integrations
  Project Status
  TrackBet is not currently considered a production release.
  The repository represents an actively developed software project and is being published to document its architecture, implementation progress, testing, and evolution toward a Windows desktop release.
  Screenshots
  Screenshots and a demonstration GIF/video will be added as the desktop version approaches its first release.
  Running the Project
  Development currently requires Python and Node.js.
  Backend

python -m uvicorn api_trackbet:app --reload --host 127.0.0.1 --port 8000

Frontend
cd frontend
npm install
npm run dev

The React frontend communicates with the local FastAPI service.
Testing
The project contains automated tests for core betting logic and API behavior.
Frontend linting:
cd frontend
npm run lint

Development is maintained with the goal of keeping the frontend at:
0 warnings
0 errors

Roadmap
The current priority is completing and stabilizing TrackBet Desktop v1 before expanding to other platforms.
After the desktop MVP is complete, the existing API and betting logic may be reused for future mobile versions.
Author
Developed by Wasatnight
TrackBet Desktop — Work in Progress
