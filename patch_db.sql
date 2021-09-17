CREATE TABLE IF NOT EXISTS driver_route (
    id SERIAL PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude REAL NOT NULL,
    speed REAL NOT NULL,
    date_created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_driver_route_driver_id ON driver_route(driver_id);

CREATE TABLE IF NOT EXISTS route_description (
    id SERIAL PRIMARY KEY,
    driver_route_id INTEGER NOT NULL,
    description CHAR(256) NOT NULL,
    is_driver_over_speed BOOLEAN NOT NULL,
    is_correct_driver_altitude BOOLEAN NOT NULL,
    date_created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
