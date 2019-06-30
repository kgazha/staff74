SELECT username, firstname, lastname, email, icq, skype,
       institution, department, address, city, mdl_user.description,
       middlename, alternatename, mdl_user_info_field.shortname,
       mdl_user_info_field.name as field_name, mdl_user_info_data.data
FROM public.mdl_user
LEFT JOIN public.mdl_user_info_data ON userid = mdl_user.id
LEFT JOIN public.mdl_user_info_field ON mdl_user_info_field.id = mdl_user_info_data.fieldid
WHERE mdl_user.id = '{0}'