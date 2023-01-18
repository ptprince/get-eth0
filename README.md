# readme

## DB info
add DB_URL to `.env`
reference to `.env.example`
currently support
- MySQL
- PostgresSQL

## create table `server `

```sql
# MySQL
CREATE TABLE IF NOT EXISTS server (
    id SERIAL NOT NULL,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip_address  VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    updated_time    DATETIME 
)
# PostgresSQL
CREATE TABLE IF NOT EXISTS server (
    id SERIAL NOT NULL,
    hostname VARCHAR(255) NOT NULL UNIQUE,
    ip_address  VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    updated_time    timestamp 
)
```

## update ip

```json
{
	"hostname": "test1",
    "eth0_ip": "1.1.1.1"
}
```