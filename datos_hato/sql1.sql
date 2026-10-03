WITH parametro AS (
    SELECT '1015' AS animal_id
),

animal AS (
    SELECT dg.*
    FROM stg_datos_generales AS dg
    INNER JOIN parametro AS p
        ON TRIM(CAST(dg.idem AS TEXT)) = p.animal_id
),

consulta AS (

    /* =====================================================
       1. IDENTIDAD
       ===================================================== */

    SELECT
        'IDENTIDAD' AS seccion,
        NULL AS fecha,
        'Identificador' AS concepto,
        CAST(a.idem AS TEXT) AS valor,
        'datos_generales' AS fuente
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Nombre',
        COALESCE(a.nombre, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Sexo',
        COALESCE(a.sexo, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Raza',
        COALESCE(a.raza, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Raza compuesta',
        COALESCE(a.raza_compuesta, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Fecha nacimiento',
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
        END,
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Madre',
        COALESCE(CAST(a.madre AS TEXT), ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Padre',
        COALESCE(CAST(a.padre AS TEXT), ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Arete registrado',
        COALESCE(a.aretes, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Lote',
        COALESCE(a.lote, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'IDENTIDAD',
        NULL,
        'Ubicación registrada',
        COALESCE(a.ubicacion, ''),
        'datos_generales'
    FROM animal AS a


    /* =====================================================
       2. ESTADO
       ===================================================== */

    UNION ALL

    SELECT
        'ESTADO',
        NULL,
        'Estado evidencial',
        CASE
            WHEN CAST(a.mortalidad_fecha AS REAL) > 0
                THEN 'MUERTO'
            WHEN CAST(a.f_descarte AS REAL) > 0
                THEN 'DESCARTADO'
            ELSE 'CON ACTIVIDAD REGISTRADA'
        END,
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'ESTADO',
        NULL,
        'Última ubicación registrada',
        COALESCE(a.ubicacion, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'ESTADO',
        NULL,
        'Fecha mortalidad',
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
        END,
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'ESTADO',
        NULL,
        'Causa mortalidad',
        COALESCE(a.mortalidad_causa, ''),
        'datos_generales'
    FROM animal AS a


    /* =====================================================
       3. RESUMEN DE HISTORIA
       ===================================================== */

    UNION ALL

    SELECT
        'RESUMEN',
        NULL,
        'Cantidad de partos',
        CAST(COUNT(*) AS TEXT),
        'partos'
    FROM stg_partos AS p
    INNER JOIN parametro AS x
        ON TRIM(CAST(p.nro_animal AS TEXT)) = x.animal_id

    UNION ALL

    SELECT
        'RESUMEN',
        NULL,
        'Cantidad de tratamientos',
        CAST(COUNT(*) AS TEXT),
        'TTO'
    FROM stg_tto AS t
    INNER JOIN parametro AS x
        ON TRIM(CAST(t.nro_de_animal AS TEXT)) = x.animal_id

    UNION ALL

    SELECT
        'RESUMEN',
        NULL,
        'Cantidad de ubicaciones',
        CAST(COUNT(*) AS TEXT),
        'ubicacion_potrero'
    FROM stg_ubicacion_potrero AS u
    INNER JOIN parametro AS x
        ON TRIM(CAST(u.idem AS TEXT)) = x.animal_id

    UNION ALL

    SELECT
        'RESUMEN',
        NULL,
        'Cantidad de PIA',
        CAST(COUNT(*) AS TEXT),
        'PIA'
    FROM stg_pia AS p
    INNER JOIN parametro AS x
        ON TRIM(CAST(p.nro_de_animal AS TEXT)) = x.animal_id

    UNION ALL

    SELECT
        'RESUMEN',
        NULL,
        'Cantidad de registros de arete',
        CAST(COUNT(*) AS TEXT),
        'aretes'
    FROM stg_aretes AS a
    INNER JOIN parametro AS x
        ON TRIM(CAST(a.idem_vaca AS TEXT)) = x.animal_id


    /* =====================================================
       4. PARTOS Y CRÍAS
       ===================================================== */

    UNION ALL

    SELECT
        'PARTOS',
        CASE
            WHEN CAST(p.fparto AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(p.fparto AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'Parto #' || CAST(p.nro_parto AS INTEGER),
        'Cría=' || COALESCE(CAST(p.cria AS TEXT), '') ||
        ' | Sexo=' || COALESCE(p.sexo, '') ||
        ' | Servicio=' || COALESCE(p.tipo_de_servicio, '') ||
        ' | Ubicación=' || COALESCE(p.ubicacion, ''),
        'partos'
    FROM stg_partos AS p
    INNER JOIN parametro AS x
        ON TRIM(CAST(p.nro_animal AS TEXT)) = x.animal_id


    /* =====================================================
       5. SALUD
       ===================================================== */

    UNION ALL

    SELECT
        'SALUD',
        CASE
            WHEN CAST(a.fecha_dx_reciente AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(a.fecha_dx_reciente AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'Diagnóstico reciente',
        COALESCE(CAST(a.dx_reciente__pn_vc_ AS TEXT), ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'SALUD',
        NULL,
        'Observación diagnóstico',
        COALESCE(a.obs__dx, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'SALUD',
        CASE
            WHEN CAST(a.fecha_tto AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(a.fecha_tto AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'Tratamiento reciente',
        COALESCE(a.tto_reciente, ''),
        'datos_generales'
    FROM animal AS a

    UNION ALL

    SELECT
        'SALUD',
        NULL,
        'Observaciones generales',
        COALESCE(a.obs_gral, ''),
        'datos_generales'
    FROM animal AS a


    /* =====================================================
       6. HISTORIAL DE TRATAMIENTOS
       ===================================================== */

    UNION ALL

    SELECT
        'TRATAMIENTOS',
        CASE
            WHEN CAST(t.fecha AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(t.fecha AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'Tratamiento',
        COALESCE(t.tto, ''),
        'TTO'
    FROM stg_tto AS t
    INNER JOIN parametro AS x
        ON TRIM(CAST(t.nro_de_animal AS TEXT)) = x.animal_id


    /* =====================================================
       7. UBICACIONES
       ===================================================== */

    UNION ALL

    SELECT
        'UBICACIONES',
        CASE
            WHEN CAST(u.fecha AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(u.fecha AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'Módulo',
        COALESCE(CAST(u.modulo AS TEXT), ''),
        'ubicacion_potrero'
    FROM stg_ubicacion_potrero AS u
    INNER JOIN parametro AS x
        ON TRIM(CAST(u.idem AS TEXT)) = x.animal_id


    /* =====================================================
       8. REPRODUCCIÓN / PIA
       ===================================================== */

    UNION ALL

    SELECT
        'REPRODUCCIÓN',
        CASE
            WHEN CAST(p.fecha_de_servicio AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(p.fecha_de_servicio AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'PIA',
        'Toro/Semen=' || COALESCE(p.toro__semen_, '') ||
        ' | Practicante=' || COALESCE(p.practicante, '') ||
        ' | Servicio=' || COALESCE(p.servicio, '') ||
        ' | Obs=' || COALESCE(p.obs, ''),
        'PIA'
    FROM stg_pia AS p
    INNER JOIN parametro AS x
        ON TRIM(CAST(p.nro_de_animal AS TEXT)) = x.animal_id


    /* =====================================================
       9. ARETES
       ===================================================== */

    UNION ALL

    SELECT
        'IDENTIFICADORES',
        CASE
            WHEN CAST(a.fecha AS REAL) > 0
            THEN strftime(
                '%d/%m/%Y',
                date(
                    '1899-12-30',
                    '+' || CAST(a.fecha AS INTEGER) || ' days'
                )
            )
            ELSE ''
        END,
        'Arete',
        COALESCE(a.arete, ''),
        'aretes'
    FROM stg_aretes AS a
    INNER JOIN parametro AS x
        ON TRIM(CAST(a.idem_vaca AS TEXT)) = x.animal_id
)

SELECT
    seccion,
    fecha,
    concepto,
    valor,
    fuente
FROM consulta
ORDER BY
    CASE seccion
        WHEN 'IDENTIDAD' THEN 1
        WHEN 'ESTADO' THEN 2
        WHEN 'RESUMEN' THEN 3
        WHEN 'PARTOS' THEN 4
        WHEN 'SALUD' THEN 5
        WHEN 'TRATAMIENTOS' THEN 6
        WHEN 'UBICACIONES' THEN 7
        WHEN 'REPRODUCCIÓN' THEN 8
        WHEN 'IDENTIFICADORES' THEN 9
        ELSE 99
    END,
    fecha;