![alt text](doc/logo.png)

# Project Origin Example IdentityService

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
