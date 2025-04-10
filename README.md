# YUMSINMYTUMS

YumsInMyTums, a digital food ordering system that lets users pre-order meals from any campus stall and pick them up conveniently between classes—saving time and reducing queues.

### Prerequisites

- [Docker](https://www.docker.com/) installed on your system
- Python 3.8+ (if running Flask locally without Docker)
- Optional: [Postman](https://www.postman.com/) for testing APIs
  

## Project Structure

```
.
├── backend/                          
│   ├── microservice/                
│         ├── service.py              # Flask
│         ├── DockerFile              
│         └── requirements.txt        
├── frontend/                         # FrontEnd vue codes
│   ├── src/                          
│         ├── router.js               # routes for frontend
│         ├── services/               
│         ├── views/                  # frontend codes
│   ├── package.json                  
│   └── DockerFile                    
├──  Swagger/                         # API route definitions
├── docker-compose.yaml               
├── docker-compose.kong.yaml          
├── kong.yaml                         # Kong services & routes
└── README.md                         
```

## Deployment

1. Open Docker Desktop to enable file sharing for kong.yaml

   Settings(top right corner) -> resources -> file sharing -> add the route where the github folder is located
   
   ![telegram-cloud-photo-size-5-6323362071252684632-y](https://github.com/user-attachments/assets/eabbc9c3-937d-469e-94a6-303812156cfa)
   (for example, the photo above, the project folder is located in /Applications/MAMP/htdocs)

3. Run both docker-compose.yaml and docker-compose.kong.yaml
   
   docker-compose -f docker-compose.yaml -f docker-compose.kong.yaml up -d --build

## Access Swagger Documentations
http://localhost:6008/api-docs/generalAPI/#/
