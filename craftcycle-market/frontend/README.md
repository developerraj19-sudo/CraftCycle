# CraftCycle Frontend

The frontend of CraftCycle is a web application built using HTML, CSS, and JS. It interacts with the backend APIs to display the platform's features.

## Structure

### Key Directories

- **/assets**: Holds static assets like CSS files, JavaScript scripts, images, icons, and fonts used across the application.
- **/intro**: Contains the introductory animations and video logic for new users visiting the application.
- **/pages**: Contains the main HTML views/pages for the various features of the application.

### Pages & Components

Here is a breakdown of the main pages available in the frontend:

1. **`index.html`** & **`home.html`**  
   The landing and home pages. `index.html` often serves as the entry point (potentially handling the intro redirection) and `home.html` contains the main dashboard/feed for the user.

2. **`pages/auth.html`**  
   The authentication page handling user login, registration, and password recovery. 

3. **`pages/dashboard.html`**  
   The main user dashboard, displaying an overview of user activities, statistics, recent transactions, and quick links to other modules.

4. **`pages/profile.html`**  
   User profile management page. Allows users to view and update their personal information, avatar, and preferences.

5. **`pages/marketplace.html`**  
   The core marketplace feature where users can browse, buy, and sell upcycled products and scrap materials.

6. **`pages/my-products.html`** & **`pages/orders.html`**  
   Management pages for a user's listed products in the marketplace and the history of their placed or received orders.

7. **`pages/scanner.html`**  
   An interface for the AI scanner feature that likely allows users to scan scrap materials and identify their types or get DIY suggestions.

8. **`pages/diy-hub.html`**  
   A dedicated hub for Do-It-Yourself (DIY) projects. Provides tutorials, ideas, and guides to upcycle scrap materials into useful products.

9. **`pages/community.html`**  
   The social component of CraftCycle. A place for users to share ideas, post their completed projects, interact with others, and discuss environmental and crafting topics.

10. **`pages/challenges.html`**  
    A gamified feature offering recycling or crafting challenges that users can complete to earn rewards or coins.

11. **`pages/coins.html`**  
    The wallet or virtual currency interface displaying the user's earned CraftCycle coins, transaction history, and options to redeem them.

12. **`pages/nearby.html`**  
    A geolocation-based feature to find nearby scrap donors, crafters, or local drop-off points.

13. **`pages/admin.html`**  
    The administrative dashboard for managing users, products, challenges, content, and monitoring system activities.

## Development

- Start a local server (e.g., Live Server) in the `craftcycle_frontend` repository to run and debug the pages.
- Ensure the backend service is running locally for full functional testing.
