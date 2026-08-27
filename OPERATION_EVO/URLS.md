# Operation EVO - Liste des URLs

## Frontend (Angular)

- http://localhost:4200/
- http://localhost:4200/submit (redirige vers /)
- http://localhost:4200/new-jira
- http://localhost:4200/items/:id (exemple: http://localhost:4200/items/12)

## Backend pages (Flask)

- http://127.0.0.1:5000/
- http://127.0.0.1:5000/login
- http://127.0.0.1:5000/admin
- http://127.0.0.1:5000/dashboard
- http://127.0.0.1:5000/images.png
- POST http://127.0.0.1:5000/logout

## Backend API - General

- GET http://127.0.0.1:5000/api/health
- GET http://127.0.0.1:5000/api/auth/me
- POST http://127.0.0.1:5000/api/system-email/weekly

## Backend API - Users

- GET http://127.0.0.1:5000/api/users
- POST http://127.0.0.1:5000/api/users
- GET http://127.0.0.1:5000/api/users/:user_id
- PUT http://127.0.0.1:5000/api/users/:user_id
- DELETE http://127.0.0.1:5000/api/users/:user_id
- POST http://127.0.0.1:5000/api/users/analyze

## Backend API - Tickets

- GET http://127.0.0.1:5000/api/tickets
- POST http://127.0.0.1:5000/api/tickets
- GET http://127.0.0.1:5000/api/tickets/:ticket_id
- PUT http://127.0.0.1:5000/api/tickets/:ticket_id
- DELETE http://127.0.0.1:5000/api/tickets/:ticket_id
- POST http://127.0.0.1:5000/api/tickets/:ticket_id/assign
- GET http://127.0.0.1:5000/api/tickets/:ticket_id/comments
- POST http://127.0.0.1:5000/api/tickets/:ticket_id/comments
- GET http://127.0.0.1:5000/api/tickets/:ticket_id/activity
- GET http://127.0.0.1:5000/api/tickets/:ticket_id/history

## Backend API - Tickets (metrics/analysis/export)

- GET http://127.0.0.1:5000/api/tickets/metrics
- GET http://127.0.0.1:5000/api/tickets/metrics-summary
- POST http://127.0.0.1:5000/api/tickets/ai-analysis
- GET http://127.0.0.1:5000/api/tickets/history
- GET http://127.0.0.1:5000/api/tickets/export
- GET http://127.0.0.1:5000/api/tickets/problem-updates

## Backend API - Problem groups

- GET http://127.0.0.1:5000/api/tickets/problem-groups
- POST http://127.0.0.1:5000/api/tickets/problem-groups
- GET http://127.0.0.1:5000/api/tickets/problem-groups/:group_id
- PUT http://127.0.0.1:5000/api/tickets/problem-groups/:group_id
- DELETE http://127.0.0.1:5000/api/tickets/problem-groups/:group_id
- GET http://127.0.0.1:5000/api/tickets/problem-groups/:group_id/suggest-assignee
- POST http://127.0.0.1:5000/api/tickets/problem-groups/:group_id/suggest-assignee

## Backend API - Stats

- GET http://127.0.0.1:5000/api/stats
- GET http://127.0.0.1:5000/api/stats/periodic
