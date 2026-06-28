# Application Layer

Application use cases and orchestration live here.

This package coordinates domain objects and ports for workflows such as selecting the next
photo, syncing libraries, and preparing display-ready outputs.

Application code may depend on the domain layer but should avoid direct dependencies on
specific storage systems, web frameworks, or display clients.
