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

1. Run both docker-compose.yaml and docker-compose.kong.yaml
   
   docker-compose -f docker-compose.yaml -f docker-compose.kong.yaml up -d --build

## Access Swagger Documentations
http://localhost:6008/api-docs/generalAPI/#/
