<div align="center">
  <img src="https://via.placeholder.com/150x150/2d6a4f/ffffff?text=CraftCycle" alt="CraftCycle Logo" width="150" height="150" />
  <h1><a href="https://craftcycle.pages.dev">♻️ CraftCycle</a></h1>
  <p><strong>Online Eco-Commerce Platform for the Circular Economy</strong></p>
  <p>🌍 <strong>Live Website: <a href="https://craftcycle.pages.dev">craftcycle.pages.dev</a></strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
  [![Flask](https://img.shields.io/badge/Flask-Framework-black.svg)](https://flask.palletsprojects.com/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791.svg)](https://www.postgresql.org/)
  [![Vanilla JS](https://img.shields.io/badge/JavaScript-Vanilla-F7DF1E.svg)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
</div>

---

## 📖 Overview

**CraftCycle** is a comprehensive and user-friendly web-based application developed to streamline the process of purchasing and managing upcycled goods and raw scrap materials in a digital environment. It bridges the gap between material donors, eco-artisans, and customers by providing an interactive and convenient platform. 

The system enables users to effortlessly browse through a wide range of upcycled products, perform advanced searches based on material type, identify recyclable items via an AI scanner, and securely complete their purchases while earning gamified **'Eco Coins'**. 

---

## ✨ Key Features

- 🛍️ **Eco-Marketplace:** Browse, search, and purchase sustainable, upcycled products online. Detailed listings include material type, prices, images, and creator details.
- 🤖 **AI Smart Scanner:** Users can upload or capture photos of waste materials to instantly identify their recyclability and receive DIY upcycling suggestions.
- 🛒 **Real-Time Cart & Secure Checkout:** Add items to a smart cart and seamlessly check out. The system ensures robust real-time stock management.
- 🪙 **Gamification & Eco Coins:** Earn rewards and 'Eco Coins' for completing sustainability challenges and actively participating in upcycling.
- 👥 **Multi-Role Dashboards:** Distinct portal experiences tailored for **Buyers**, **Sellers (Artisans)**, and **Admins**, featuring specialized tools for inventory management, stock control, and order tracking.

---

## 🛠️ Technology Stack

The CraftCycle platform utilizes a decoupled client-server architecture:

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Vanilla JS | Single Page Application (SPA) using Fetch API for a highly responsive UI. |
| **Backend** | Python, Flask | RESTful API handling business logic, JWT authentication, and AI scanner integration. |
| **Database** | PostgreSQL | Robust Relational Database Management System (RDBMS) via SQLAlchemy ORM. |
| **AI Integration** | Google Vision API / Gemini | Advanced image recognition technology to identify materials from user camera uploads. |

---

## 📐 System Architecture & Workflows

### 1. High-Level Architecture
CraftCycle utilizes a robust decoupled architecture connecting the SPA frontend to the Flask REST API.

```mermaid
graph TD
    subgraph Client Layer
        UI[Web UI Interface]
        API_Client[api.js Fetch API]
        State[Local Storage]
        UI <--> API_Client
        API_Client <--> State
    end

    subgraph Application Layer
        Router[Python API Router]
        Auth_MW[JWT Middleware]
        Logic[Business Logic & ORM]
        Router --> Auth_MW
        Auth_MW --> Logic
    end

    subgraph Data & External Layer
        DB[(PostgreSQL)]
        AI[Vision AI API]
    end

    API_Client <-->|HTTPS / REST| Router
    Logic <-->|SQLAlchemy| DB
    Logic <-->|REST| AI
```

### 2. Entity-Relationship (ER) Diagram
A structured overview of the core database entities that map out products, orders, and users:

```mermaid
erDiagram
    USER ||--o{ ORDERS : places
    USER ||--o{ PRODUCTS : sells
    USER {
        int id PK
        string name
        string email
        string role
    }
    PRODUCTS ||--o{ CART : added_to
    PRODUCTS {
        int id PK
        string product_name
        float price
        int stock
    }
    ORDERS ||--o{ CART : contains
    ORDERS {
        int id PK
        float total_price
        string address
        timestamp created_at
    }
    CART {
        int id PK
        int user_id FK
        int product_id FK
        int quantity
    }
```

### 3. AI Smart Scanner Workflow
The logic flow when an eco-conscious user utilizes the AI Scanner feature:

```mermaid
stateDiagram-v2
    [*] --> Upload_Image
    Upload_Image --> Send_To_API: User clicks 'Analyze'
    
    state Send_To_API {
        [*] --> Fetch_Vision_API
        Fetch_Vision_API --> Process_Result: AI identifies material (e.g. "Glass")
        Process_Result --> Fetch_DB_Tutorials: Query local DB for matching material
    }
    
    Send_To_API --> Display_Results
    Display_Results --> Show_Material_Type
    Display_Results --> Show_DIY_Tutorials
    
    Show_DIY_Tutorials --> User_Earns_Coins: If User saves tutorial
    User_Earns_Coins --> [*]
```

### 4. E-Commerce Checkout Sequence
The transactional flow during the checkout process designed to prevent race conditions on stock inventory:

```mermaid
sequenceDiagram
    participant Client as Frontend (User)
    participant API as Python API (Flask)
    participant DB as PostgreSQL Database

    Client->>API: POST /api/v1/orders/checkout (Cart Payload, Auth Token)
    activate API
    API->>API: Validate JWT Token
    API->>DB: BEGIN TRANSACTION
    
    loop For each item in cart
        API->>DB: SELECT * FROM products WHERE id=X FOR UPDATE
        DB-->>API: Return Product Details & Stock Level
        
        alt Stock is Sufficient
            API->>DB: UPDATE products SET stock = stock - quantity
            API->>DB: INSERT INTO order_items
        else Stock is Insufficient
            API->>DB: ROLLBACK TRANSACTION
            API-->>Client: 400 Bad Request (Out of Stock Error)
        end
    end
    
    API->>DB: INSERT INTO orders (total_price, address)
    API->>DB: COMMIT TRANSACTION
    API-->>Client: 201 Created (Order ID & Success Message)
    deactivate API
```

---

## 🎨 Visual Design System

CraftCycle employs an **"Eco-Chic"** visual design language tailored to communicate sustainability and elegance:
- **Color Palette:** Deep Forest Green (`#2d6a4f`) for primary actions, Earthy Terracotta (`#e07a5f`) for accents, and Off-white Cream (`#f4f1de`) for backgrounds.
- **Typography:** Modern sans-serif fonts (e.g., *Inter* or *Outfit*) for high legibility and a contemporary feel.
- **Dynamic Interface:** Features like skeleton loading screens, smooth CSS transitions, and glassmorphism effects provide a highly responsive user experience.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL
- Web Browser (Chrome, Edge, Safari, Firefox)

### Installation Guide
*(Further instructions to setup and run the whole project will go here depending on the deployment strategy.)*

---

<div align="center">
  <p>Built with ❤️ for a Greener Planet.</p>
</div>
