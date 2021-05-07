Este servicio permite, mediante sus endpoints, almacenar listas de proxies para su posterior uso.

* `GET /proxies/all` devuelve un listado de todos los proxies almacenados en su base de datos.
* `GET /proxies/download` busca nuevos proxies y los retorna luego de almacenarlos en su base de datos.
* `GET /proxies/get` busca y retorna un proxy de la base de datos. También lo marca como usado. Cuando ya no restan proxies marcados como usados, se resetea dicho campo para que puedan volver a usarse.
* `GET /proxies/checked/{days}/days` retorna los proxies que fueron verificados hace más de `days` días.
* `GET /proxies/delete/{_id}` retorna y elimina de la base de datos el documento con el id `_id`.
