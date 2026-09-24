# Recipe Box - CRUD Recipe Management Application

#### Video Demo: [https://youtube.com/shorts/RONAF2ta_NY]

#### Description:
**Recipe Box** is a dynamic, responsive web application built with Python, Flask, SQLite, Jinja2, Bootstrap 5, and vanilla JavaScript. It was developed as a final project for Harvard's CS50x. 

The primary goal of the application is to provide a seamless user interface for managing recipes, ingredients, and instructions. Unlike standard web applications that rely on separate pages for editing, Recipe Box features an intuitive **inline card editing** system alongside dynamic form fields, allowing users to modify existing recipes directly from their dashboard without full page navigations.

---

## Technical Stack & Architecture

- **Backend:** Python / Flask
- **Database:** SQLite3 (with foreign keys and cascading deletes enforced)
- **Frontend:** HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3
- **Templating:** Jinja2 partials (`form.html`) for reusable creation and editing UI

---

## Features & Functionality

1. **Full CRUD Lifecycle:**
   - **Create (`/add`):** Add new recipes with custom metadata, optional photo uploads (`multipart/form-data`), and dynamic multi-row ingredient inputs.
   - **Read (`/` & `/index`):** View all recipes on a clean card dashboard sorted by newest entries first.
   - **Update (`/edit/<id>`):** Toggle cards into inline edit mode to modify titles, replace photos, add or remove ingredients, and update instructions.
   - **Delete (`/delete/<id>`):** Remove recipes with a single click. Deleting a recipe automatically removes associated junction data from SQLite via `ON DELETE CASCADE` and deletes any uploaded photo from the local storage folder.

2. **Relational Database Schema:**
   - Features a normalized many-to-many relationship using three tables: `recipes`, `ingredients`, and `recipes_ingredients`.
   - Utilizes `UNIQUE` indices and `INSERT OR IGNORE` strategies to maintain a master catalog of ingredients without duplicate entries.

3. **Dynamic Frontend Interactions:**
   - Vanilla JavaScript handles dynamic input creation for adding and removing individual ingredient rows on the fly.
   - Utilizes global event delegation to ensure dynamic rows inside inline card forms function properly without duplicate DOM ID collisions.

---

## Project Structure & File Overview

```text
.
├── app.py                  # Main Flask application, routes, and DB context managers
├── schema.sql              # Database creation script with constraints and tables
├── requirements.txt        # Python package dependencies
├── style.css               # Custom CSS styles overriding Bootstrap utilities
├── static/
│   ├── favicon.ico         # Application icon
│   ├── script.js           # DOM manipulations, card toggling, dynamic inputs
│   ├── style.css            # Base stylesheet
│   └── uploads/            # Local image storage directory for recipe photos
└── templates/
    ├── layout.html         # Main application wrapper and navigation bar
    ├── index.html          # Main dashboard displaying recipe cards & edit views
    ├── add.html            # Dedicated page for adding a new recipe
    └── form.html           # Reusable Jinja partial shared between /add and inline edits