Diseño de la Base de Datos

![alt text](image-2.png)


*   Metadata Sitios
    -   Recordar que mucha data parece ser que se esta actualizando, es por ello que si existe haremos un update, identificar los campos, si no hacer un insert, Identificar que campos se deben de actualizar
    La metadata contiene información del comercio, incluyendo localización, atributos y categorías.

*   Review Estados
    Los archivos donde se disponibiliza las reviews de los usuarios

*   Business
    Contiene información del comercio, incluyendo localización, atributos y categorías.

*   Review
    Contiene las reseñas completas, incluyendo el user_id que escribió el review y el business_id por el cual se escribe la reseña

*   user.parquet
    Data del usuario incluyendo referencias a otros usuarios amigos y a toda la metadata asociada al usuario.

*   checkin.json 
    Registros en el negocio.

*   tip
    Tips (consejos) escritos por el usuario. Los tips son más cortas que las reseñas y tienden a dar sugerencias rápidas.

 

 User_id y latitud y longitud serían las llaves que esta relacionando los dataset de google y yelp

 Se Agrega el script de creación de la base de datos