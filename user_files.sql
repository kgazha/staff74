select max(id) as id, contenthash, max(CONCAT(contextid, '/', component, '/', filearea, '/', itemid, '/', filename)) as media_path,
json_agg(filearea) as filearea, json_agg(filename) as filename, json_agg(mimetype) as mimetype
FROM mdl_files
WHERE userid = '{0}' and filesize > 0
and contenthash not in
(select contenthash
FROM mdl_files
WHERE userid = '{0}' and filesize > 0
and filearea like '%submission_files%'
group by contenthash)
group by contenthash
union all
select  max(id) as id, contenthash, max(CONCAT(contextid, '/', component, '/', filearea, '/', itemid, '/', filename)) as media_path,
json_agg(filearea) as filearea, json_agg(filename) as filename, json_agg(mimetype) as mimetype
FROM mdl_files
WHERE userid = '{0}' and filesize > 0
and filearea like '%submission_files%'
group by contenthash