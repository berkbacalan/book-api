# BuyTheBook

## To run the project

The project uses MongoDB as a database and FastApi as a backend framework.
You may easily run the project with Docker. Run the command below

````
docker-compose up --build -d
````

You may access the server on localhost:8000

## Swagger
FastApi provides swagger for apps using OpenAPI. You may access the swagger document on
````
localhost:8000/docs
````

## Postman Collection

Also you may find the Postman collection to access the requests.
````
buythebook.postman_collection.json
````
In Postman, import the file above. You may find the requests. 

Please mind that, except the User services you need to bearer token to make requests.

BuyTheBook app uses JWT Token Based Authentication.