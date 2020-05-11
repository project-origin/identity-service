![alt text](doc/logo.png)

# Project Origin IdentityService

TODO Describe the project here


# Environment variables

Name | Description | Example
:--- | :--- | :--- |
`DEBUG` | Whether or not to enable debugging mode (off by default) | `0` or `1`
`SECRET` | Application secret for salting | `foobar`
`DATABASE_URI` | Database connection string for SQLAlchemy | `postgresql://scott:tiger@localhost/mydatabase`
`DATABASE_CONN_POLL_SIZE` | Connection pool size per container | `10`
`TOKEN_EXPIRE_MINUTES` | Number of minutes to keep the token valid | `4320`
**URLs:** | |
`HYDRA_URL` | URL to Hydra without trailing slash | `https://auth.projectorigin.dk`
`FAILURE_REDIRECT_URL` | An arbitrary URL to redirect to if something unexpected fails | `https://app.projectorigin.dk`
**Logging:** | |
`AZURE_APP_INSIGHTS_CONN_STRING` | Azure Application Insight connection string (optional) | `InstrumentationKey=19440978-19a8-4d07-9a99-b7a31d99f313`
