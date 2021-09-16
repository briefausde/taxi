CREATE TABLE IF NOT EXISTS driver_route (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude REAL NOT NULL,
    speed REAL NOT NULL,
    date_created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS route_description (
    id SERIAL PRIMARY KEY,
    driver_route_id INTEGER NOT NULL,
    is_driver_over_speed BOOLEAN NOT NULL,
    is_correct_driver_altitude BOOLEAN NOT NULL,
    date_created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
