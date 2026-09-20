# URL Shortener

**Author:** Kavish Kumar  
**Roll Number:** 2026UEC2812  
**Year:** 1st Year Student

## About The Project

This is a fully-featured URL Shortener web application. While the initial expectation for this assignment was a command-line interface (CLI) tool, I chose to implement it as a web application using Flask. I have prior experience with web development, and I felt that building a visual, interactive application would be a more comprehensive demonstration of my programming capabilities and system design understanding.

### Core Features
- **URL Shortening**: Transform long URLs into concise, shareable short codes.
- **Custom Aliases**: Define your own custom short codes (e.g., `my-portfolio`).
- **QR Code Generation**: Automatically generates a downloadable QR code for every shortened link.
- **Link Expiration (TTL)**: Set a Time-To-Live for links (e.g., 1 Hour, 1 Day, 30 Days). Once expired, the link automatically returns a standard HTTP `410 Gone` status.
- **Smart Deduplication**: Automatically detects if a URL has already been shortened to prevent database clutter, returning the existing code instead.
- **Saved Links Dashboard**: Favorite, manage, and delete your personal links directly from the homepage.
- **Global Analytics**: A dedicated dashboard tracking total clicks, top referrers, device/browser usage, and clicks over time via an interactive graph.
- **Database Management**: A search-enabled administrative table view to easily parse through all generated URLs and their metadata.
- **Retro "Neo-Brutalism" UI**: A fully custom, highly responsive, and trendy UI built entirely from scratch using Tailwind CSS.

## Screenshots

- **Home / URL Creation Page:** `![img.png](img.png)`
- **QR Code & Success View:** `![img_1.png](img_1.png)`
- **Global Analytics Dashboard:** `![img_3.png](img_3.png)`
- **Database Management Table:** `![img_2.png](img_2.png)`

## Installation & Setup

1. **Navigate to the project folder:**
   Open your terminal and ensure you are inside the project directory.

2. **Install Dependencies:**
   Install the required Python packages using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application:**
   Start the local Flask development server:
   ```bash
   python app.py
   ```

4. **Access the Web App:**
   Open your web browser and navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000).

## How to Use

1. **Shorten a Link:** On the home page, paste your long URL into the "Original URL" field. 
2. **Add an Alias:** Optionally, type a name for the link to make it easily identifiable.
3. **Advanced Settings:** Click `+ Advanced Settings` if you want to set an expiration time for the link.
4. **Generate:** Click **Shorten & Save**. Your new short link and its QR code will instantly appear.
5. **View Analytics:** Click the **Analytics** button at the top of the page to view click statistics, referrers, and traffic charts.
6. **Manage Database:** Click **DB Management** to view the complete list of shortened URLs, search for specific entries, and view direct click counts.

## Libraries & Technologies Used

- **[Flask](https://flask.palletsprojects.com/)**: The core web framework used to handle routing, HTTP requests, and backend logic.
- **[SQLite3](https://docs.python.org/3/library/sqlite3.html)**: Python's built-in database engine used to persistently store URLs, aliases, expiration times, and analytics data.
- **[Segno](https://segno.readthedocs.io/)**: A lightweight, pure-Python library used for generating SVG QR codes without requiring heavy external image processing dependencies.
- **[Tailwind CSS](https://tailwindcss.com/)**: Used via CDN for rapid, utility-first UI styling, which powered the custom Neo-Brutalism design framework (inspired by elements from the JetBrains Website).
- **[Chart.js](https://www.chartjs.org/)**: A JavaScript charting library used to render the interactive "Clicks Over Time" line graph on the analytics page.
