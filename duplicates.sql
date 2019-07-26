select CONCAT(lastname, ' ', firstname, ' ', patronymic) as FIO, json_agg(email), count(*) from
(
    SELECT test_completed, s1.userid, username, firstname, lastname, percents, email FROM
    (
        SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_completed, email, userid
        FROM public.mdl_quiz_attempts
        INNER JOIN mdl_user ON mdl_user.id = userid
        GROUP BY username, email, userid, firstname, lastname
    ) s1
    WHERE test_completed = 5
    AND percents >= 70
) s
INNER JOIN
(select userid, data as patronymic from public.mdl_user_info_data
 inner join public.mdl_user_info_field on mdl_user_info_field.id = mdl_user_info_data.fieldid
 where shortname = 'otchestvo') s2
ON s.userid = s2.userid
group by fio
order by count desc