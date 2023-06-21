USE epidata;

-- Create new `fluview_clinical` table with proper unique constraint.
CREATE TABLE `fluview_clinical_v2` (
    `id` int(11) NOT NULL AUTO_INCREMENT,
    `release_date` date NOT NULL,
    `issue` int(11) NOT NULL,
    `epiweek` int(11) NOT NULL,
    `region` varchar(12) NOT NULL,
    `lag` int(11) NOT NULL,
    `total_specimens` int(11) NOT NULL,
    `total_a` int(11) DEFAULT NULL,
    `total_b` int(11) DEFAULT NULL,
    `percent_positive` double DEFAULT NULL,
    `percent_a` double DEFAULT NULL,
    `percent_b` double DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `issue` (`issue`, `epiweek`, `region`),
    KEY `release_date` (`release_date`),
    KEY `epiweek` (`epiweek`),
    KEY `region` (`region`),
    KEY `lag` (`lag`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8;


-- Insert unique rows from `fluview_clinical` into `fluview_clinical_v2`.
-- This is done in order to reset ID counter and fill gaps betwen row's ids.
INSERT INTO
    fluview_clinical_v2(
        `release_date`,
        `issue`,
        `epiweek`,
        `region`,
        `lag`,
        `total_specimens`,
        `total_a`,
        `total_b`,
        `percent_positive`,
        `percent_a`,
        `percent_b`
    )
SELECT
    min_release_date release_date,
    tmp.issue,
    tmp.epiweek,
    tmp.region,
    tmp.lag,
    tmp.total_specimens,
    tmp.total_a,
    tmp.total_b,
    tmp.percent_positive,
    tmp.percent_a,
    tmp.percent_b
FROM
    (
        SELECT
            s.release_date,
            s.issue,
            s.epiweek,
            s.region,
            s.lag,
            s.total_specimens,
            s.total_a,
            s.total_b,
            s.percent_positive,
            s.percent_a,
            s.percent_b
        FROM
            (
                SELECT
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
                    ROW_NUMBER() OVER(
                        PARTITION BY fc.epiweek,
                        fc.issue,
                        fc.region
                        ORDER BY
                            fc.release_date DESC
                    ) as row_num
                FROM
                    fluview_clinical fc
            ) s
        WHERE
            s.row_num = 1
    ) tmp
    JOIN (
        SELECT
            MIN(fc.release_date) as min_release_date,
            fc.issue,
            fc.epiweek,
            fc.region
        FROM
            fluview_clinical fc
        GROUP BY
            fc.issue,
            fc.epiweek,
            fc.region
    ) rel_date ON tmp.issue = rel_date.issue
    AND tmp.epiweek = rel_date.epiweek
    AND tmp.region = rel_date.region
ORDER BY
    tmp.issue,
    tmp.epiweek,
    tmp.region DROP INDEX issue ON fluview_clinical;

-- Before creating new unique constraint we need to remove rows that do not satisfy it.
DELETE FROM
    fluview_clinical
WHERE
    id IN (
        SELECT
            tmp.id
        FROM
            (
                SELECT
                    s.id,
                    s.release_date,
                    s.issue,
                    s.epiweek,
                    s.region,
                    s.lag,
                    s.total_specimens,
                    s.total_a,
                    s.total_b,
                    s.percent_positive,
                    s.percent_a,
                    s.percent_b
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
                            ROW_NUMBER() OVER(
                                PARTITION BY fc.epiweek,
                                fc.issue,
                                fc.region
                                ORDER BY
                                    fc.release_date DESC
                            ) as row_num
                        FROM
                            epidata.fluview_clinical fc
                    ) s
                WHERE
                    s.row_num = 1
            ) tmp
            JOIN (
                SELECT
                    MIN(fc.release_date) as min_release_date,
                    fc.issue,
                    fc.epiweek,
                    fc.region
                FROM
                    epidata.fluview_clinical fc
                GROUP BY
                    fc.issue,
                    fc.epiweek,
                    fc.region
            ) rel_date ON tmp.issue = rel_date.issue
            AND tmp.epiweek = rel_date.epiweek
            AND tmp.region = rel_date.region
        ORDER BY
            tmp.issue,
            tmp.epiweek,
            tmp.region
    );

-- Remove index to avoid "duplicate index" issue.
DROP INDEX issue ON epidata.fluview_clinical;

-- Create new unique constraint based in issue, epiweek and region.
ALTER TABLE
    fluview_clinical
ADD
    CONSTRAINT `issue` UNIQUE(`issue`, `epiweek`, `region`);