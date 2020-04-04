INSERT INTO user_team(user_id, team_id, last_activity, total_activity)
WITH joined_on_user_id AS (
	SELECT a.* FROM user_actions a INNER JOIN users b ON a.user_id = b.id
),
joined_on_chat_id AS (
	SELECT
		a.user_id,
		b.id AS team_id,
		MIN(a.chat_name) AS chat_name,
		MAX(a.time) AS last_activity,
		COUNT(*) AS total_activity
	FROM
		joined_on_user_id a
	LEFT JOIN teams b ON a.chat_id = b.chat_id
GROUP BY
	(b.id,
		a.user_id)
),
joined_on_chat_id_chat_name AS (
	SELECT
		a.user_id,
		a.team_id AS team_id_from_chat_id,
		b.id AS team_id_from_chat_name,
		a.chat_name,
		a.last_activity,
		a.total_activity
	FROM
		joined_on_chat_id a
	LEFT JOIN teams b ON a.chat_name = b.team_name
)
SELECT
	user_id,
	team_id_from_chat_id AS team_id,
	last_activity,
	total_activity
FROM
	joined_on_chat_id_chat_name
WHERE
	team_id_from_chat_id IS NOT NULL
UNION
SELECT
	user_id,
	team_id_from_chat_name AS team_id,
	last_activity,
	total_activity
FROM
	joined_on_chat_id_chat_name
WHERE
	team_id_from_chat_id IS NULL
	AND team_id_from_chat_name IS NOT NULL;
