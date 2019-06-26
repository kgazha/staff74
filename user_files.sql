--SELECT max(username) as username, max(firstname) as firstname, max(lastname) as lastname,
--       max(percents) as percents, max(email) as email, contenthash, json_agg(filearea) as filearea, max(filename) as filename,
--       max(CONCAT(contextid, '/', component, '/', filearea, '/', itemid, '/', filename)) as media_path
--FROM
--(
--    SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_complited, email, userid
--	FROM public.mdl_quiz_attempts
--    INNER JOIN mdl_user ON mdl_user.id = userid
--    GROUP BY username, email, userid, firstname, lastname
--) s
--inner JOIN public.mdl_files ON mdl_files.userid = s.userid
--WHERE filesize != 0 and test_complited = 5
--group by contenthash
---- AND filearea = 'submission_files' and filesize != 0
--
--SELECT json_agg(filearea), contenthash
--FROM mdl_files
--WHERE userid in
--(
--	select userid from
--	(
--		SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_complited, email, userid
--		FROM public.mdl_quiz_attempts
--		INNER JOIN mdl_user ON mdl_user.id = userid
--		GROUP BY username, email, userid, firstname, lastname
--	) s
--	WHERE test_complited = 5
--)
--and filesize > 0
--group by contenthash

select contenthash, max(CONCAT(contextid, '/', component, '/', filearea, '/', itemid, '/', filename)) as media_path,
json_agg(filearea) as filearea, max(filename) as filename
FROM mdl_files
WHERE userid = '{0}' and filesize > 0
group by contenthash