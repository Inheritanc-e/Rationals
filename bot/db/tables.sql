SET TIMEZONE = 'UTC'; 

CREATE TABLE IF NOT EXISTS infractions(
    id BIGSERIAL PRIMARY KEY NOT NUll,
    user_id BIGINT NOT NULL,
    type VARCHAR(10) NOT NULL,
    reason VARCHAR(1000), 
    permanent BOOL NOT NULL,
    issued_time TIMESTAMP NOT NULL, 
    active BOOL NOT NULL,
    expires TIMESTAMP CHECK (permanent = 'f'),
    actor BIGINT NOT NULL
) ;

