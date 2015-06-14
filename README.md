# SF Movies
This is an implementation of the "SF Movies" [Uber coding challenge](https://github.com/uber/coding-challenge-tools/blob/master/coding_challenge.md), which purpose is 
> Create a service that shows on a map where movies have been filmed in San Francisco. The user should be able to filter the view using autocompletion search.

The data with the movies is available at [DataSF](https://data.sfgov.org/Arts-Culture-and-Recreation-/Film-Locations-in-San-Francisco/yitu-d5am)

## Solution
This project presents a very simple solution that shows the user a text input. Whenever someone starts typing in it, a list of movies matching the input appear in a dropdown. Once the user clicks in one of the movies, a brief description is shown along with markers in the map with all the locations where it was filmed in San Francisco. The interactions between the front-end and the back-end are performed through a REST API.

I have opted to do the back-end part of the application. However, I have added a small UI so please forgive my awful JavaScript :)

This is the stack that I have used for the project:
* Python
* Tornado framework: I have chosen to use this framework as its asynchronous paradigm provides very high performance
* MongoDB: not only MongoDB is a good choice to store denormalized data with high performance but it also provides a powerful text search mechanism, ideal to implement the autocompletion search functionality required by this project.
* Motor

### Architecture
I have divided the service in 3 tiers, namely services, business and database. Each one of them is in charge of performing one task only, and can only access tiers in a lower level, but never higher level tiers.

#### Services
The services tier is the one that will receive all the requests and will be in charge of all the tasks related to the HTTP protocol (i.e. set headers, response status, transform data to and from JSON, read query parameters, etc.) and communicates with the business tier. In this case there are only 2 different endpoints: 
* `/api/search/movies`: it receives a query with a text and returns movies which title matches that query
* `/api/movies/<id>`: it returns the content of a movie given its id

#### Business
The business tier contains all the logic of the application, which in this case is sanitizing the input and caching the results. The latter is very important for this problem as it will alleviate the load of the database. For this I have implemented a LRU (Least Recently Used) cache that stores the results of a given query. In practice, this is far from ideal as this cache will be per node, so in a distributed system the chances of hitting this first level cache are smaller. Ideally, a cache system such as Redis or Memcached should be used, but I haven't been able to implement it due to lack of time.

#### Database
Finally, the database tier is in charge of accessing our MongoDB. It implements several abstractions in order to make this simpler. First, a Query common object that abstracts the access to the database, in this case performed with Motor. Also, I have applied a DAO pattern, that provides an interface to access to each collection (though in this case is only the `movies` collection).

In order to populate the database, I downloaded the movies information in JSON format and created a script to load it. This script is also in charge of retrieving the coordinates of the locations using Google's Geolocation API. I have done it this way because this information will never change, so we'll be saving having to retrieve that information later. The database is denormalized. This means that there are no relations between the data, though some data (locations, actors, etc.) might be duplicated. However, performance increases by doing this.

Also, the static content is served with a Nginx server.

### Tests
I have added 3 different types of tests:
* unit: they test the logic of each component separately and are free of dependencies
* database: they access the database in order to test the components of the database layer, as its behavior cannot be replicated with mocks.
* api: these are integration tests that make direct calls to the REST API.

### Deployment
The application can be accessed at [http://52.8.150.46](http://52.8.150.46). In this case, it is a single machine in Amazon EC2 that is running all of the components. Of course, this would not be a valid solution for a production environment. However, the the services are stateless so the only thing left to deploy more services instances would be to change the Nginx configuration, adding the IPs of the desired services and adding a DNS, as everything is accessed through IPs in this solution.
