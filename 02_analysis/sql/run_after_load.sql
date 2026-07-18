\set ON_ERROR_STOP on

\echo Building the analytics star schema
\ir 01_build_analytics.sql

\echo Creating analytical views
\ir 02_views.sql

\echo Running SQL validation queries
\ir 03_validation.sql
