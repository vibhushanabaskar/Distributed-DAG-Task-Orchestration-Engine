1. if NODEjs not installed install it
2. open new terminal run : docker-compose up --build (this starts the container) i) to delete container : docker-compose down -v
3. open another terminal run : npm install reactflow axios (if not installed)
4. to open Local: http://localhost:5173/ run :npm run dev
5. open new terminal and run : docker exec -it dag_db psql -U dag_user -d dag_db (to visualize the db) run below code i)\dt ii) select id, command, file_path from tasks;
6. to stop worker_node: docker stop dag_worker to start worker node: docker start dag_worker
