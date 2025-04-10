### Stack Tecnologico

Se utilizó la nube de google cloud, los componentes usados son:

Cloud Composer, el cual tiene embebido Airflow y se encarga de la orquestación por medio de DAGs. Para comunicarse entre sus componentes, enlistados a continuación:

Cloud Storage, estaría haciendo la función del data lake, donde se estan almacenando los archivo
A traves de python es como lee el cloud Storage, hace la limpieza y los registros los sube a Big Query.

![alt text](Images/image.png)

#### Base De Datos

A continuación el diagrama entidad relación
![alt text](Images/image-1.png)

##### Diccionario de datos

###### Google Maps

* Sitios

![alt text](Images/image-2.png)

* Business

![alt text](Images/image-3.png)

* Review

![alt text](Images/image-4.png)

* Usuario

![alt text](Images/image-5.png)

* Tip

![alt text](Images/image-6.png)

* Check in

![alt text](Images/image-7.png)