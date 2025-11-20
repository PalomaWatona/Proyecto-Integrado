const botonEliminar = (id) => {
    if (window.confirm("¿Está Seguro De Querer Eliminar El Registro?")) {
        window.location.href = "/eliminarficha/" + id;
    }
}

const botonVerFicha = (id) => {
    window.location.href = "/verficha/" + id;  
}

const botonEditarFicha = (id) => {
    window.location.href = "/editarficha/" + id;  
}

