WITH parametro AS (
    SELECT '1015' AS animal_id
),

animal AS (
    SELECT dg.*
    FROM stg_datos_generales AS dg
    INNER JOIN parametro AS p
        ON TRIM(CAST(dg.idem AS TEXT)) = p.animal_id
),

partos AS (
    SELECT
        COUNT(*) AS cantidad_partos,

        group_concat(
            'Parto ' || CAST(nro_parto AS INTEGER) ||
            ': ' ||
            strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(fparto AS INTEGER) || ' days'
                )
            ) ||
            ' | Cría=' || COALESCE(CAST(cria AS TEXT),'') ||
            ' | Sexo=' || COALESCE(sexo,'') ||
            ' | Servicio=' || COALESCE(tipo_de_servicio,''),
            '  ||  '
        ) AS historial_partos,

        group_concat(
            CAST(cria AS TEXT),
            '; '
        ) AS crias

    FROM (
        SELECT *
        FROM stg_partos
        WHERE TRIM(CAST(nro_animal AS TEXT)) = '1015'
        ORDER BY CAST(nro_parto AS INTEGER)
    )
),

tratamientos AS (
    SELECT
        COUNT(*) AS cantidad_tratamientos,

        group_concat(
            strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(fecha AS INTEGER) || ' days'
                )
            ) ||
            ': ' ||
            COALESCE(tto,''),
            '  ||  '
        ) AS historial_tratamientos

    FROM (
        SELECT *
        FROM stg_tto
        WHERE TRIM(CAST(nro_de_animal AS TEXT)) = '1015'
        ORDER BY CAST(fecha AS REAL)
    )
),

ubicaciones AS (
    SELECT
        COUNT(*) AS cantidad_ubicaciones,

        group_concat(
            strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(fecha AS INTEGER) || ' days'
                )
            ) ||
            ': ' ||
            COALESCE(CAST(modulo AS TEXT),''),
            '  ||  '
        ) AS historial_ubicaciones

    FROM (
        SELECT *
        FROM stg_ubicacion_potrero
        WHERE TRIM(CAST(idem AS TEXT)) = '1015'
        ORDER BY CAST(fecha AS REAL)
    )
),

pia AS (
    SELECT
        COUNT(*) AS cantidad_pia,

        group_concat(
            strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(fecha_de_servicio AS INTEGER) || ' days'
                )
            ) ||
            ': Toro/Semen=' || COALESCE(toro__semen_,'') ||
            ' | Servicio=' || COALESCE(servicio,''),
            '  ||  '
        ) AS historial_pia

    FROM (
        SELECT *
        FROM stg_pia
        WHERE TRIM(CAST(nro_de_animal AS TEXT)) = '1015'
        ORDER BY CAST(fecha_de_servicio AS REAL)
    )
),

aretes AS (
    SELECT
        COUNT(*) AS cantidad_aretes,

        group_concat(
            COALESCE(arete,''),
            '; '
        ) AS historial_aretes

    FROM (
        SELECT *
        FROM stg_aretes
        WHERE TRIM(CAST(idem_vaca AS TEXT)) = '1015'
        ORDER BY CAST(fecha AS REAL)
    )
)

SELECT

    /* ================= IDENTIDAD ================= */

    a.idem AS IDEM,
    a.nombre AS NOMBRE,

    CASE
        WHEN CAST(a.f_nac_ AS REAL) > 0
        THEN strftime(
            '%d/%m/%Y',
            date(
                '1899-12-30',
                '+' || CAST(a.f_nac_ AS INTEGER) || ' days'
            )
        )
        ELSE ''
    END AS FECHA_NACIMIENTO,

    a.sexo AS SEXO,
    a.raza AS RAZA,
    a.raza_compuesta AS RAZA_COMPUESTA,

    a.madre AS MADRE,
    a.padre AS PADRE,

    a.aretes AS ARETE_DG,

    /* ================= SITUACIÓN ================= */

    a.ubicacion AS UBICACION_ACTUAL,
    a.lote AS LOTE,

    CASE
        WHEN CAST(a.mortalidad_fecha AS REAL) > 0
        THEN 'MUERTO'
        WHEN CAST(a.f_descarte AS REAL) > 0
        THEN 'DESCARTADO'
        ELSE 'ACTIVO / CON ACTIVIDAD REGISTRADA'
    END AS ESTADO,

    CASE
        WHEN CAST(a.mortalidad_fecha AS REAL) > 0
        THEN strftime(
            '%d/%m/%Y',
            date(
                '1899-12-30',
                '+' || CAST(a.mortalidad_fecha AS INTEGER) || ' days'
            )
        )
        ELSE ''
    END AS FECHA_MUERTE,

    a.mortalidad_causa AS CAUSA_MUERTE,

    /* ================= PRODUCCIÓN / RESUMEN ================= */

    a.peso_reci__romana_kg AS PESO_RECIENTE,
    a.clasificacion_potencial AS POTENCIAL,
    a.lact_1 AS LACTACION_1,
    a.lact_2 AS LACTACION_2,
    a.lact_3 AS LACTACION_3,

    /* ================= PARTOS ================= */

    p.cantidad_partos AS CANTIDAD_PARTOS,
    p.crias AS CRIAS,
    p.historial_partos AS HISTORIAL_PARTOS,

    /* ================= SALUD ================= */

    CASE
        WHEN TRIM(COALESCE(a.dx_reciente__pn_vc_,''))
            <> ''
        THEN a.dx_reciente__pn_vc_
        ELSE ''
    END AS DIAGNOSTICO_RECIENTE,

    a.obs__dx AS OBS_DIAGNOSTICO,

    /* ================= TRATAMIENTOS ================= */

    t.cantidad_tratamientos AS CANTIDAD_TRATAMIENTOS,
    t.historial_tratamientos AS HISTORIAL_TRATAMIENTOS,

    /* ================= UBICACIONES ================= */

    u.cantidad_ubicaciones AS CANTIDAD_UBICACIONES,
    u.historial_ubicaciones AS HISTORIAL_UBICACIONES,

    /* ================= REPRODUCCIÓN ================= */

    pi.cantidad_pia AS CANTIDAD_PIA,
    pi.historial_pia AS HISTORIAL_PIA,

    /* ================= IDENTIFICADORES ================= */

    ar.cantidad_aretes AS CANTIDAD_REGISTROS_ARETE,
    ar.historial_aretes AS HISTORIAL_ARETES

FROM animal AS a
CROSS JOIN partos AS p
CROSS JOIN tratamientos AS t
CROSS JOIN ubicaciones AS u
CROSS JOIN pia AS pi
CROSS JOIN aretes AS ar;