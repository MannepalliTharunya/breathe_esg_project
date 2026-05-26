-- ESG Platform database initialization
-- Runs once when the MySQL container is first created

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Ensure the database uses utf8mb4 for full Unicode support (including emoji)
ALTER DATABASE esg_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create a read-only reporting user for analytics tools
CREATE USER IF NOT EXISTS 'esg_readonly'@'%' IDENTIFIED BY 'readonly_password_change_me';
GRANT SELECT ON esg_platform.* TO 'esg_readonly'@'%';
FLUSH PRIVILEGES;
