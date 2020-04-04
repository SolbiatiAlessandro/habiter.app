WITH teams_activity AS (
	SELECT
		team_id,
		COUNT(DISTINCT (user_id)) AS number_of_users,
		SUM(total_activity) AS total_messages,
		MAX(last_activity) AS last_activity
	FROM
		user_team
	WHERE
		user_id != '898309178' /* oana */
		AND user_id != '884492906' /* alex */
	GROUP BY
		team_id
)
SELECT
	team_id,
	active,
	team_name,
	number_of_users,
	total_messages,
	last_activity,
	label,
	content_index
FROM
	teams teams_info
	JOIN teams_activity ON teams_info.id = teams_activity.team_id
WHERE
	community = %s;
