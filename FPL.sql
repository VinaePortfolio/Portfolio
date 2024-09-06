-- Calculates the team that scored the most points, by summing the total points of the players and then grouping them by their team--

SELECT Team, SUM(TotalPoints) as TotalTeamPoints
FROM RealStats
GROUP BY Team
ORDER BY TotalTeamPoints DESC

-- Calculates the average points each team scored by position by using the AVG function to find the average points and then group it by the team and position--
SELECT Team, Position, AVG(TotalPoints) as AveragePoints
FROM RealStats
GROUP BY Team, Position
ORDER BY Team, Position


-- Calculates the best value players by dividing their price by the total amount of points they scored and displays the players in descending order showing the best value players at the top--
SELECT FirstName, Surname, TotalPoints, (NULLIF(TotalPoints, 0)/Price) as PointsPerMillion
FROM RealStats
ORDER BY PointsPerMillion DESC;


-- This calcualtes the overperforming players in terms of goalscoring. It calculates the difference between the expected goals and the goals the player has actually scored. The more clinical players will have the higher values.--
SELECT e.FirstName, e.Surname, SUM(CAST(e.ExpectedGoals AS FLOAT)) AS TotalExpectedGoals, SUM(CAST(r.Goals AS FLOAT)) AS TotalRealGoals, (SUM(CAST(r.Goals AS FLOAT)) - SUM(CAST(e.ExpectedGoals AS FLOAT))) AS goal_difference
FROM ExpectedStats e
JOIN RealStats r 
ON e.FirstName = r.FirstName 
AND e.Surname = r.Surname 
AND e.ExpectedGoals = r.ExpectedGoals
GROUP BY e.FirstName, e.Surname
HAVING (SUM(CAST(r.Goals AS FLOAT)) - SUM(CAST(e.ExpectedGoals AS FLOAT))) > 0
ORDER BY goal_difference DESC;

-- Step 1: Create a Temporary Table
CREATE TABLE #TopPerformers (
   FirstName varchar(50),
   Surname varchar(50),
   TotalGoals INT
);

-- Step 2: Insert Top Performers into the Temporary Table
INSERT INTO #TopPerformers (FirstName, Surname, TotalGoals)
SELECT r.FirstName, r.Surname, SUM(r.goals) AS total_goals
FROM RealStats r
GROUP BY r.FirstName, r.Surname
HAVING SUM(r.goals) > 5;

-- Step 3: Query the Temporary Table and Analyze Per 90 Stats
SELECT 
   p90.FirstName, p90.Surname, tp.TotalGoals, AVG(p90.ExpectedGoalsPer90) AS ExpectedGoalsPer90, AVG(p90.ExpectedAssistsPer90) AS avg_assists_per_90
FROM #TopPerformers tp
JOIN Per90 p90 ON tp.FirstName = p90.FirstName
and tp.Surname = p90.Surname
GROUP BY p90.FirstName, p90.Surname, tp.TotalGoals
ORDER BY ExpectedGoalsPer90 DESC;

-- Step 4: Drop the Temporary Table
DROP TABLE #TopPerformers;


-- This calculates the difference between the expected assists and the real assists by position using a CTE and creates a view for it--
CREATE VIEW PositionAssistSummary AS
WITH PositionAssists AS (
   SELECT 
       r.position, 
       SUM(CAST(e.ExpectedAssists AS FLOAT)) AS total_expected_assists, 
       SUM(CAST(r.Assists AS FLOAT)) AS total_real_assists
   FROM ExpectedStats e
   JOIN RealStats r 
       ON e.FirstName = r.FirstName 
       AND e.Surname = r.Surname
   GROUP BY r.position
)
SELECT 
   pa.position, 
   pa.total_expected_assists, 
   pa.total_real_assists, 
   (pa.total_real_assists - pa.total_expected_assists) AS assist_diff
FROM PositionAssists pa