CREATE TABLE IF NOT EXISTS cvision_images_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    format TEXT NOT NULL,
    compressed BOOLEAN,
    compression_method TEXT
);

CREATE TABLE IF NOT EXISTS cvision_images_analyzed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_image_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    format TEXT NOT NULL,
    compressed BOOLEAN,
    compression_method TEXT,
    category TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    FOREIGN KEY (raw_image_id) REFERENCES cvision_images_raw(id) ON DELETE CASCADE
);
