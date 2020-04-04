WITH users_with_team_id AS (
	SELECT
		id,
		MIN(name) AS name,
		MIN(sessions_active_total) AS sessions_active_total,
		MIN(sessions_skip_total) AS sessions_skip_total,
		MIN(sessions_skip_streak) AS sessions_skip_streak,
		MIN(days_active_total) AS days_active_total,
		MIN(days_since_join) AS days_since_join,
		MIN(user_team.team_id) AS team_id
	FROM
		users
		JOIN user_team ON users.id = user_team.user_id
	WHERE community = %s
	GROUP BY
		id
)
SELECT
	a.*,
	b.timezone,
	b.label
FROM
	users_with_team_id a
	JOIN teams b ON a.team_id = b.id;
