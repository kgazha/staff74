select userid, username, firstname, lastname, patronymic, email, city, confirmed,
       TO_CHAR(TO_TIMESTAMP(firstaccess), 'YYYY-MM-DD') as firstaccess from mdl_user
inner join
(   SELECT mdl_user.id as userid, mdl_user_info_data.data as patronymic
    FROM public.mdl_user
    LEFT JOIN public.mdl_user_info_data ON userid = mdl_user.id
    LEFT JOIN public.mdl_user_info_field ON mdl_user_info_field.id = mdl_user_info_data.fieldid
    WHERE shortname = 'otchestvo'
) s
ON id = s.userid
where id = '{0}'