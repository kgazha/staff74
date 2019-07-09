select count(*), 'количество поставивших галочки' as name from
(select count(*) from public.mdl_user_info_data as d
inner join mdl_user_info_field as f on fieldid = f.id
where shortname in ('ecoandnature', 'thingandearth', 'selhoz', 'dorogi',
                    'cultandtourism', 'zkh', 'zdrav', 'studyandyoung',
                    'social', 'buildings', 'infotech', 'economyandfin')
                    and   d.data != '0'
group by userid) s
union all
select count(*), 'количество зарегистрировавшихся' as name from mdl_user
union all
select count(*), 'количество участников, прошедних тест успешно'
from (
SELECT test_completed, s.userid, percents FROM
(
    SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_completed, email, userid
    FROM public.mdl_quiz_attempts
    INNER JOIN mdl_user ON mdl_user.id = userid
    GROUP BY username, email, userid, firstname, lastname
) s
WHERE test_completed = 5
AND percents >= 70) s
union all
select count(*), 'количество участников, прошедних тест'
from (
SELECT test_completed, s.userid, percents FROM
(
    SELECT username, firstname, lastname, ROUND(sum(sumgrades)*100/50) AS percents, count(quiz) AS test_completed, email, userid
    FROM public.mdl_quiz_attempts
    INNER JOIN mdl_user ON mdl_user.id = userid
    GROUP BY username, email, userid, firstname, lastname
) s
WHERE test_completed = 5) s