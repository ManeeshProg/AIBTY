# Am I Better Than Yesterday?

An AI-driven personal growth application designed to help users objectively reflect on their daily actions, habits, and mindset.

## Project Structure

- **`backend/`**: FastAPI application handling API requests, AI orchestration (LangChain/Claude), and database interactions (PostgreSQL/pgvector).
- **`mobile/`**: React Native (Expo) application for Android and iOS.

## Getting Started

### Backend
1. Navigate to `backend/`.
2. Install dependencies (Poetry recommended).
3. Run `uvicorn app.main:app --reload`.

### Mobile
1. Navigate to `mobile/`.
2. Run `npm install`.
3. Run `npx expo start`.
