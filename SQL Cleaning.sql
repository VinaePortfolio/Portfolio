select *
from FPLCleaning

--Change numeric value to the players position
ALTER TABLE FPLCleaning
ALTER COLUMN Value#element_type VARCHAR(50);

UPDATE FPLCleaning
SET Value#element_type = CASE
    WHEN Value#element_type = 1 THEN 'Goalkeeper'
    WHEN Value#element_type = 2 THEN 'Defender'
    WHEN Value#element_type = 3 THEN 'Midfielder'
    WHEN Value#element_type = 4 THEN 'Striker'
    ELSE Value#element_type  -- Keeps existing value if it doesn't match any of the conditions
END;

--Combine the players first and second name and delete the two original separate columns leaving the newly created combined one
-- Step 1: Add the new FullName column
ALTER TABLE FPLCleaning
ADD FullName VARCHAR(255); -- Adjust the size if necessary

-- Step 2: Update the FullName column with concatenated values
UPDATE FPLCleaning
SET FullName = CONCAT(Value#first_name, ' ', Value#second_name, ' (ID: ', Value#code, ')');

-- Step 3: Drop the old Value#first_name and Value#second_name columns
ALTER TABLE FPLCleaning
DROP COLUMN Value#first_name

ALTER TABLE FPLCleaning
DROP COLUMN Value#second_name

ALTER TABLE FPLCleaning
ALTER COLUMN Value#penalties_order VARCHAR(255);

UPDATE FPLCleaning
SET Value#penalties_order = CASE
    WHEN Value#penalties_order = 1 THEN '1st choice taker'
    WHEN Value#penalties_order = 2 THEN '2nd choice taker'
    WHEN Value#penalties_order = 3 THEN '3rd choice taker'
    WHEN Value#penalties_order = 4 THEN '4th choice taker'
    WHEN Value#penalties_order IS NULL THEN 'doesnt take penalties'
    ELSE Value#penalties_order -- Keeps existing value if it doesn't match any of the conditions
END;

--Change the names of all the tables so they no longer have 'value#' at the start of every column
DECLARE @sql NVARCHAR(MAX) = '';

SELECT @sql = @sql + 'EXEC sp_rename ''' + TABLE_SCHEMA + '.' + TABLE_NAME + '.' + COLUMN_NAME + ''', ''' 
       + SUBSTRING(COLUMN_NAME, 7, LEN(COLUMN_NAME)) + ''', ''COLUMN'';' + CHAR(13)
FROM INFORMATION_SCHEMA.COLUMNS
WHERE COLUMN_NAME LIKE 'value#%'
AND TABLE_SCHEMA = 'dbo'  -- Replace with your schema name if needed
AND TABLE_NAME = 'FPLCLeaning';    -- Replace with your table name if needed

EXEC sp_executesql @sql;

-- 1. Change the column to FLOAT
ALTER TABLE FPLCleaning
ALTER COLUMN now_cost FLOAT;

-- 2. Update the column to divide by 10
UPDATE FPLCleaning
SET now_cost = now_cost / 10;

--Change numeric value to the players team
ALTER TABLE FPLCleaning
ALTER COLUMN team VARCHAR(50);

UPDATE FPLCleaning
SET team = CASE
    WHEN team = 1 THEN 'Arsenal'
    WHEN team = 2 THEN 'Aston Villa'
    WHEN team = 3 THEN 'Bournemouth'
    WHEN team = 4 THEN 'Brentford'
	WHEN team = 5 THEN 'Brighton'
	WHEN team = 6 THEN 'Chelsea'
	WHEN team = 7 THEN 'Crystal Palace'
	WHEN team = 8 THEN 'Everton'
	WHEN team = 9 THEN 'Fulham'
	WHEN team = 10 THEN 'Ipswich'
	WHEN team = 11 THEN 'Leicester'
	WHEN team = 12 THEN 'Liverpool'
	WHEN team = 13 THEN 'Man City'
	WHEN team = 14 THEN 'Man Utd'
	WHEN team = 15 THEN 'Newcastle'
	WHEN team = 16 THEN 'Nottingham Forest'
	WHEN team = 17 THEN 'Southampton'
	WHEN team = 18 THEN 'Spurs'
	WHEN team = 19 THEN 'West Ham'
	WHEN team = 20 THEN 'Wolves'
	ELSE team  -- Keeps existing value if it doesn't match any of the conditions
END;
