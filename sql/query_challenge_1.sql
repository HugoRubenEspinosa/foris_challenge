SELECT COUNT(DISTINCT e.student_id) AS student_count
FROM enrollment e
JOIN subject s ON e.group_id IN (
    SELECT id
    FROM `group`
    WHERE subject_id = s.id
)
WHERE e.enrollment_hour >= '2024-02-05 00:00:00'
AND e.enrollment_hour < '2024-02-07 23:59:59'
AND s.code LIKE '%1'
AND e.student_id IN (
    SELECT student_id
    FROM enrollment
    WHERE enrollment_hour >= '2024-02-05 00:00:00'
    AND enrollment_hour <= '2024-02-07 23:59:59'
    GROUP BY student_id
    HAVING COUNT(DISTINCT group_id) >= 5
);