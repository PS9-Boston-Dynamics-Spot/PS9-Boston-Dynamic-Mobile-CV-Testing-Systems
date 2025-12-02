CREATE TABLE IF NOT EXISTS cvision_images_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    format TEXT NOT NULL, -- e.g. png ,jpg
    content_type TEXT NOT NULL, -- e.g. image/jpeg
    bucket TEXT NOT NULL,
    size INTEGER NOT NULL, -- bytes
    compressed BOOLEAN NOT NULL DEFAULT 0,
    compression_method TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cvision_images_analyzed (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_image_id INTEGER NOT NULL,
    name TEXT NOT NULL UNIQUE ,
    format TEXT NOT NULL, -- e.g. png, jpg
    content_type TEXT NOT NULL,
    bucket TEXT NOT NULL,
    size INTEGER NOT NULL,
    compressed BOOLEAN NOT NULL DEFAULT 0,
    compression_method TEXT,
    sensor_type TEXT NOT NULL, -- e.g. digital / analog / both (NOT NULL)
    opcua_node_id TEXT, -- if analog sensor, node_id is empty
    aruco_id INTEGER NOT NULL, 
    category TEXT NOT NULL, -- category: e.g. temperature, pressure (NOT NULL)
    quality REAL, -- means the image quality, any value between 0 and 1, --> 1 is the best
    value REAL NOT NULL, -- e.g. 20.0 °C (NOT NULL)
    unit TEXT NOT NULL, -- e.g. °C (NOT NULL)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_image_id) REFERENCES cvision_images_raw(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS anomalies(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analyzed_image_id INTEGER NOT NULL,
    detected_value REAL NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    anomaly_score REAL NOT NULL,
    node_id TEXT,
    parameters TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (analyzed_image_id) REFERENCES cvision_images_analyzed(id) ON DELETE CASCADE
);