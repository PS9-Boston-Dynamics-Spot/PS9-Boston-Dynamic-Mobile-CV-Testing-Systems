CREATE TABLE IF NOT EXISTS cvision_images_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE ,
    format TEXT NOT NULL, -- e.g. png ,jpg
    compressed BOOLEAN,
    compression_method TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cvision_images_analyzed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_image_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE ,
    format TEXT NOT NULL, -- e.g. png ,jpg
    compressed BOOLEAN,
    compression_method TEXT,
    category TEXT NOT NULL, -- category: e.g. temperature, pressure
    quality REAL, -- any value between 0 and 1, --> 1 is the best
    value REAL NOT NULL, -- e.g. 20.0 °C
    unit TEXT NOT NULL, -- e.g. °C
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_image_id) REFERENCES cvision_images_raw(id) ON DELETE CASCADE
);