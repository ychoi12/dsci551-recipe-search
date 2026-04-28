-- Create the dsci551 user by the Python benchmark / CLI.
-- Run once as root:
--   mysql -u root -p < sql/00_create_user.sql
-- (root password: Dsci551Pass!123)

DROP USER IF EXISTS 'dsci551'@'localhost';
CREATE USER 'dsci551'@'localhost' IDENTIFIED BY 'Dsci551Pass!123';
GRANT ALL PRIVILEGES ON recipe_project.* TO 'dsci551'@'localhost';
FLUSH PRIVILEGES;

SELECT User, Host FROM mysql.user WHERE User = 'dsci551';
SELECT COUNT(*) AS recipe_rows FROM recipe_project.recipes;
