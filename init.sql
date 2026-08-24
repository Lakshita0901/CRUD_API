CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO task (title, done)
SELECT * FROM (VALUES
    ('Buy milk', FALSE),
    ('Walk the dog', FALSE),
    ('Finish assignment', TRUE)
) AS seed(title, done)
WHERE NOT EXISTS (SELECT 1 FROM task);