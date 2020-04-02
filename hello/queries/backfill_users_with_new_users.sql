WITH users_with_unique_ids AS (
	SELECT
		user_id,
		MIN(username) AS username,
		'Leetcode' AS community,
		'Telegram' AS app
	FROM
		user_actions
	WHERE
		community = 'Leetcode'
		AND NOT EXISTS (
			SELECT
				*
			FROM
				users
			WHERE
				users.name = user_actions.username
				OR users.id = user_actions.user_id)
		GROUP BY
			user_id
) INSERT INTO users (id, name, community, app)
SELECT
	MIN(user_id),
	username,
	MIN(community),
	MIN(app)
FROM
	users_with_unique_ids
GROUP BY
	username;
