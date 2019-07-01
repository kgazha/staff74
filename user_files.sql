SELECT contenthash, media_path, filearea, filename, itemid FROM
(select max(id) as id, contenthash, max(CONCAT(contextid, '/', component, '/', filearea, '/', itemid, '/', filename)) as media_path,
json_agg(filearea) as filearea, max(filename) as filename
FROM mdl_files
WHERE userid = '{0}' and filesize > 0
group by contenthash) s
LEFT JOIN
(SELECT id, itemid FROM mdl_files
where mdl_files.filearea = 'submission_files') s2
ON s.id = s2.id