USE epidata;

DELETE FROM
    fluview_clinical
WHERE
    id IN (
        SELECT
            dup.id
        FROM
            (
                SELECT
                    *
                FROM
                    (
                        SELECT
                            fc.id,
                            fc.release_date,
                            fc.issue,
                            fc.epiweek,
                            fc.region,
                            fc.lag,
                            fc.total_specimens,
                            fc.total_a,
                            fc.total_b,
                            fc.percent_positive,
                            fc.percent_a,
                            fc.percent_b,
                            ROW_NUMBER() OVER (
                                PARTITION BY fc.release_date,
                                fc.issue,
                                fc.epiweek,
                                fc.region,
                                fc.lag,
                                fc.total_specimens,
                                fc.total_a,
                                fc.total_b,
                                fc.percent_positive,
                                fc.percent_a,
                                fc.percent_b
                                ORDER BY
                                    fc.release_date
                            ) as row_num
                        FROM
                            epidata.fluview_clinical fc
                        ORDER BY
                            fc.release_date DESC
                    ) s
                WHERE
                    s.row_num > 1
            ) dup
    );

DROP INDEX issue ON epidata.fluview_clinical;

ALTER TABLE
    fluview_clinical
ADD
    CONSTRAINT `issue` UNIQUE(`issue`, `epiweek`, `region`);