CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    image_filename TEXT NOT NULL,
    reference_object TEXT NOT NULL,  -- e.g., "Standard Credit Card"
    reference_size TEXT NOT NULL,    -- e.g., "85.6 mm"
    measured_value TEXT NOT NULL,    -- e.g., "45.0"
    unit TEXT NOT NULL,             -- e.g., "cm"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);