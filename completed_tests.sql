SELECT * FROM
(
    SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_complited, email, userid
    FROM public.mdl_quiz_attempts
    INNER JOIN mdl_user ON mdl_user.id = userid
    GROUP BY username, email, userid, firstname, lastname
) s
WHERE test_complited = 5