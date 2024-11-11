CREATE TABLE IF NOT EXISTS ${db}.${table} (
  id STRING,
  name STRING,
  created_at STRING,
  picture_url STRING,
  owners ARRAY < STRUCT < id: STRING > >,
  users ARRAY < STRUCT < email: STRING,
  id: STRING,
  name: STRING > >,
  dp_create_timestamp TIMESTAMP,
  dp_update_timestamp TIMESTAMP
) USING ${format} LOCATION '${path}'
TBLPROPERTIES (
  delta.autoOptimize.optimizeWrite = true,
  delta.autoOptimize.autoCompact = true
)