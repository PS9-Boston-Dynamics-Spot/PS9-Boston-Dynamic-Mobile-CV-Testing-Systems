CREATE TABLE IF NOT EXISTS cvision_images_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE ,
    format TEXT NOT NULL, -- e.g. png ,jpg
    bucket TEXT NOT NULL,
    size INTEGER NOT NULL,
    compressed BOOLEAN NOT NULL DEFAULT 0,
    compression_method TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cvision_images_analyzed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_image_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE ,
    format TEXT NOT NULL, -- e.g. png, jpg
    bucket TEXT NOT NULL,
    size INTEGER NOT NULL,
    compressed BOOLEAN NOT NULL DEFAULT 0,
    compression_method TEXT,
    sensor_type TEXT, -- e.g. digital / analog / both (NOT NULL)
    category TEXT, -- category: e.g. temperature, pressure (NOT NULL)
    quality REAL, -- means the image quality, any value between 0 and 1, --> 1 is the best
    value REAL, -- e.g. 20.0 °C (NOT NULL)
    unit TEXT, -- e.g. °C (NOT NULL)
    information TEXT, -- e.g. JSON-String with all extracted information (NOT NULL)
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_image_id) REFERENCES cvision_images_raw(id) ON DELETE CASCADE
);