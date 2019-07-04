select count(f.name), f.name from public.mdl_user_info_data as d
inner join mdl_user_info_field as f on fieldid = f.id
where shortname in ('ecoandnature', 'thingandearth', 'selhoz', 'dorogi',
                    'cultandtourism', 'zkh', 'zdrav', 'studyandyoung',
                    'social', 'buildings', 'infotech', 'economyandfin')
and d.data != '0'
group by f.name
order by count(f.name) desc