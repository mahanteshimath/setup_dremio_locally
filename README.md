
# What is Dremio?

Dremio is a data lakehouse platform that allows users to access, analyze, and visualize data from various sources in real time. It's an open source Data-as-a-Service (DaaS) platform that's powered by Apache Iceberg. 
Features: 

• Query engine descripton: Dremio's query engine allows users to directly query petabyte-scale cloud data lake storage
• Self-service analytics: Dremio allows data teams to deliver self-service analytics  
• Interactive analytics: Dremio supports ad-hoc and interactive analytics  
• Security: Dremio provides robust security, including data level security 
• Customizable interface: Dremio offers a customizable interface  

•Benefits: Eliminates massive data transfers,    Mitigates security risks, Accelerates AI and analytics initiatives, and Dramatically reduces costs.Use cases: Business intelligence and Creating and consuming data products.   
-------
# What Dremio recommend ?
![alt text](image-4.png)



-----



# Setting Up a Data Analytics Environment with Docker and Docker Compose

## Step 1: Understanding Docker and Docker Compose

**Docker** is a platform for developing, shipping, and running containerized applications. Containers bundle software with its dependencies, ensuring consistent behavior across environments.

**Docker Compose** is a tool that allows you to define and run multi-container Docker applications using a single `docker-compose.yml` file. In this file, you define all services, their configurations, and how they interact.

---

## Step 2: Creating the Docker Compose File

### Instructions:
1. Open a text editor (e.g., VS Code, Notepad).
2. Create a new file named `docker-compose.yml`.
3. Copy and paste the following configuration (adjust services as needed):

```yaml
version: "3"

services:
  # Nessie Catalog Server Using In-Memory Store
  nessie:
    image: projectnessie/nessie:latest
    container_name: nessie
    networks:
      - iceberg
    ports:
      - 19120:19120

  # MinIO Storage Server
  ## Creates two buckets named lakehouse and lake
  minio:
    image: minio/minio:latest
    container_name: minio
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=password
    networks:
      - iceberg
    ports:
      - 9001:9001
      - 9000:9000
    command: ["server", "/data", "--console-address", ":9001"]
    entrypoint: >
      /bin/sh -c "
      minio server /data --console-address ':9001' &
      sleep 5 &&
      mc alias set myminio http://localhost:9000 admin password &&
      mc mb myminio/lakehouse &&
      mc mb myminio/lake &&
      tail -f /dev/null
      "

  # Dremio
  dremio:
    platform: linux/x86_64
    image: dremio/dremio-oss:latest
    container_name: dremio
    environment:
      - DREMIO_JAVA_SERVER_EXTRA_OPTS=-Dpaths.dist=file:///opt/dremio/data/dist
    networks:
      - iceberg
    ports:
      - 9047:9047
      - 31010:31010
      - 32010:32010

  # Superset
  superset:
    image: alexmerced/dremio-superset
    container_name: superset
    networks:
      - iceberg
    ports:
      - 8088:8088

  # Data Science Notebook (Jupyter Notebook)
  datanotebook:
    image: alexmerced/datanotebook
    container_name: datanotebook
    environment:
      - JUPYTER_TOKEN= # Set a token if desired, or leave blank to disable token authentication
    networks:
      - iceberg
    ports:
      - 8888:8888
    volumes:
      - ./notebooks:/home/pydata/work # Mounts a local folder for persistent notebook storage

networks:
  iceberg:
```



### Explanation of Services:
- **Nessie**: Provides version control for data, useful for tracking data lineage and historical states.
- **MinIO**: Acts as an S3-compatible object storage, holding data buckets that Dremio will use as data sources.
- **Dremio**: A query engine enabling SQL-based interactions with data stored in MinIO and Nessie.
- **Superset**: A BI tool for creating and visualizing dashboards based on data queried through Dremio.
- **DataNotebook**: Jupyter Notebook server for exploratory data analysis.

---

## Step 3: Running the Environment

1. Open a terminal and navigate to the folder where you saved `docker-compose.yml`.
2. Start all services in detached mode:
   ```bash
   docker-compose up -d
   ```
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)
![alt text](image-3.png)


3. Verify that the services are running:
   ```bash
   docker ps
   ```
4. Initialize Superset before using it:
   ```bash
   docker exec -it superset superset init
   ```

---

## Step 4: Verifying the Services

- **Dremio**: [http://localhost:9047](http://localhost:9047) (log in or create an admin account).
- **MinIO**: [http://localhost:9001](http://localhost:9001) (username: `admin`, password: `password`).
- **Superset**: [http://localhost:8088](http://localhost:8088) (username: `admin`, password: `admin`).
- **DataNotebook**: [http://localhost:8888/lab?](http://localhost:8888/lab?).

---

## Step 5: Adding Nessie and MinIO as Data Sources in Dremio

### Connecting Nessie as a Catalog in Dremio
1. In Dremio, go to **Add Source**.
2. Choose **Nessie** from the source types and configure:

#### General Settings:
- **Name**: `lakehouse`
- **Endpoint URL**: `http://nessie:19120/api/v2`
- **Authentication**: None

#### Storage Settings:
- **Access Key**: `admin`
- **Secret Key**: `password`
- **Root Path**: `lakehouse`

#### Connection Properties:
- `fs.s3a.path.style.access`: `true`
- `fs.s3a.endpoint`: `minio:9000`
- `dremio.s3.compat`: `true`

3. Save the source. The `lakehouse` should now appear in the Datasets section.

### Connecting MinIO as an S3-Compatible Source in Dremio
1. In Dremio, click **Add Source** and select **S3**.
2. Configure MinIO:

#### General Settings:
- **Name**: `lake`
- **Credentials**: AWS Access Key
- **Access Key**: `admin`
- **Secret Key**: `password`
- **Encrypt Connection**: unchecked

#### Advanced Options:
- **Enable Compatibility Mode**: `true`
- **Root Path**: `/lake`

#### Connection Properties:
- `fs.s3a.path.style.access`: `true`
- `fs.s3a.endpoint`: `minio:9000`

3. Save the source. The `lake` source will appear in Dremio.

---

## Step 6: Setting Up Superset for BI Visualizations

1. Initialize Superset:
   ```bash
   docker exec -it superset superset init
   ```
2. Open Superset at [http://localhost:8088](http://localhost:8888), log in using user admin :pass :admin, and go to **Settings > Database Connections**.
3. Add a new database:
   - Select **Other** as the type.
   - Enter the connection string (replace `USERNAME` and `PASSWORD` with Dremio credentials):
     ```
     dremio+flight://USERNAME:PASSWORD@dremio:32010/?UseEncryption=false
     ```
4. Test the connection and save it.
5. Add datasets:
   - Click the `+` icon, choose a table (e.g., `sales_data`), and add it to your workspace.
6. Create charts and add them to dashboards.

---

## Step 7: Shutting Down the Environment

To stop and clean up the environment, run:
```bash
docker-compose down -v
```
This will remove all containers and volumes, giving you a clean slate for the next session. 

For more information, please refer to this tutorial: https://www.youtube.com/watch?v=2_hYwyF1A2A&list=LL
