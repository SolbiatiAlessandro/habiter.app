-- queries activity data from user_actions
-- and backfills users table
WITH sessions_data AS (
	SELECT
		- 1 AS days_active_total,
		COUNT(DISTINCT (DATE(time))) AS sessions_active_total,
		-- MIN(DISTINCT (DATE(time))) AS first_day_active,
		-- MAX(DISTINCT (DATE(time))) AS last_day_active,
		DATE(now()) - MAX(DISTINCT (DATE(time))) AS sessions_skip_streak,
		DATE(now()) - MIN(DISTINCT (DATE(time))) AS days_since_join,
		(DATE(now()) - MIN(DISTINCT (DATE(time)))) - COUNT(DISTINCT (DATE(time))) AS sessions_skip_total,
		user_id
	FROM
		user_actions
	WHERE
		text = 'SCREENSHOT'
	GROUP BY
		user_id
	ORDER BY
		sessions_active_total DESC
),
activity_data AS (
	SELECT
		*
	FROM
		sessions_data
	UNION
	SELECT
		COUNT(DISTINCT (DATE(time))) AS days_active_total,
		0 AS sessions_active_total,
		-- MIN(DISTINCT (DATE(time))) AS first_day_active,
		-- MAX(DISTINCT (DATE(time))) AS last_day_active,
		DATE(now()) - MIN(DISTINCT (DATE(time))) AS sessions_skip_streak,
		DATE(now()) - MIN(DISTINCT (DATE(time))) AS days_since_join,
		DATE(now()) - MIN(DISTINCT (DATE(time))) AS sessions_skip_total,
		user_id
	FROM
		user_actions
	WHERE
		NOT EXISTS (
			SELECT
				*
			FROM
				sessions_data
			WHERE
				user_actions.user_id = sessions_data.user_id)
		GROUP BY
			user_id
		ORDER BY
			sessions_active_total DESC
)
UPDATE
	users
SET
	days_active_total = activity_data.days_active_total,
	sessions_active_total = activity_data.sessions_active_total,
	sessions_skip_streak = activity_data.sessions_skip_streak,
	days_since_join = activity_data.days_since_join,
	sessions_skip_total = activity_data.sessions_skip_total
FROM
	activity_data
WHERE
	users.id = activity_data.user_id;
