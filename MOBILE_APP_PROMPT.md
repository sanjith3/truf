# AI Prompt for Mobile App Development

**Copy and paste the following prompt into your AI coding assistant (e.g., Cursor, Windsurf, Bolt.new):**

---

## Project: TurfSpot Mobile App

I need you to build a modern mobile application using **React Native (Expo)** and **NativeWind (TailwindCSS)** for a sports turf booking platform called "TurfSpot".

The backend is an existing Django REST API running at `http://YOUR_LOCAL_IP:8000/api/v1/`.

### 1. Design & UI/UX (Must match Website)
- **Primary Color:** Emerald Green (`#10b981` aka `brand-500` used in web).
- **Backgrounds:** Clean white (`#ffffff`) with Gray-50 (`#f9fafb`) sections.
- **Typography:** Use the **Outfit** font family (Google Fonts) for a modern, sleek look.
- **Style:** "Glassmorphism" touches, rounded corners combined with "Bento grid" layouts.

### 2. Tech Stack
- **Framework:** React Native (Expo Router v3).
- **Styling:** NativeWind v4 (TailwindCSS for Mobile).
- **Icons:** Lucide React Native or FontAwesome.
- **State Management:** Zustand or React Context.
- **Networking:** Axios or TanStack Query.

### 3. API Integration Structure
Base URL: `/api/v1/`

**Authentication (Phone Number + OTP):**
- **POST** `/auth/login/`: Accepts `{ phone_number }`. Returns success/OTP sent.
- **POST** `/auth/verify/`: Accepts `{ phone_number, otp }`. Returns `{ access, refresh, user }`.
- Store the standard JWT token in SecureStore.

**Core Features:**
- **GET** `/turfs/`: Fetches list of venues.
  - JSON keys: `id`, `name`, `image`, `location`, `price_per_hour`, `rating`, `sports` (list with icons).
- **GET** `/turfs/{id}/`: Fetches specific turf details including images, amenities, and slots.

### 4. Required Screens & Flow

**A. Onboarding / Auth**
- **Splash Screen:** Green gradient background with TurfSpot logo.
- **Login Screen:** Clean input for Phone Number. "Send OTP" button (Gradient Green).
- **OTP Screen:** 4-digit input. Auto-submit on fill.

**B. Home Tab**
- **Header:** "Hello, {User}" with Profile Avatar.
- **Hero Section:** "Ready to play?" heading with a fresh, clean design.
- **Search Bar:** "Find turfs near you..."
- **Categories:** Horizontal scroll (Football, Cricket, Badminton).
- **Near You:** Vertical list of Turf Cards (Image, Name, Location badge, Price/hr).

**C. Turf Detail Screen (The "Wow" Factor)**
- **Hero Image:** Full width top image with back button overlay.
- **Info Card:** Rounded white card overlapping the image bottom.
- **Details:** Name (H1), Location (Icon + Text), Rating (Star).
- **Amenities:** Grid of icons (e.g., Parking, Water).
- **Booking Action:** Sticky bottom button "Book Now" -> Opens Date/Slot picker.

### 5. Implementation Steps
1. Initialize a new Expo project with TypeScript and NativeWind.
2. Set up the `api/client.ts` with Axios interceptors for JWT.
3. Build the `LoginScreen` and `VerifyScreen`.
4. Create the `TurfCard` component matching the web design (White card, shadow-sm, rounded-xl).
5. Build the `HomeScreen` fetching from `/turfs/`.

### strict Rules
- Use `SafeAreaView` correctly.
- Handle "Loading" states with skeleton loaders (`moti` or simple animated views).
- Handle "Error" states (e.g., API down).
- Do NOT mock data if possible; try to hit the localhost API (use your machine's IP, e.g., 192.168.x.x, since 'localhost' doesn't work on real devices).

---
