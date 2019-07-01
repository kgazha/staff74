SELECT username, lastname, firstname, patronymic, percents, test_complited, email, s.userid FROM
(
    SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_complited, email, userid
    FROM public.mdl_quiz_attempts
    INNER JOIN mdl_user ON mdl_user.id = userid
    GROUP BY username, email, userid, firstname, lastname
) s
INNER JOIN
(
    SELECT mdl_user.id as userid, mdl_user_info_data.data as patronymic
    FROM public.mdl_user
    LEFT JOIN public.mdl_user_info_data ON userid = mdl_user.id
    LEFT JOIN public.mdl_user_info_field ON mdl_user_info_field.id = mdl_user_info_data.fieldid
    WHERE shortname = 'otchestvo'
) s2
ON s.userid = s2.userid
WHERE test_complited = 5
AND percents >= 70