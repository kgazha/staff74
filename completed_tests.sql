SELECT test_completed, s.userid, percents FROM
(
    SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_completed, email, userid
    FROM public.mdl_quiz_attempts
    INNER JOIN mdl_user ON mdl_user.id = userid
    GROUP BY username, email, userid, firstname, lastname
) s
WHERE test_completed = 5
AND percents >= 70