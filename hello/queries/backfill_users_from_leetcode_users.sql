UPDATE users 
SET screenshot_submitted = leetcode_users.screenshot_submitted
FROM leetcode_users
WHERE users.id = leetcode_users.id::varchar(255) 