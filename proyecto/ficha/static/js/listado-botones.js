// Función para eliminar un registro
const botonEliminar = (id) => {
    // Muestra un cuadro de diálogo de confirmación al usuario
    if (window.confirm("¿Está Seguro De Querer Eliminar El Registro?")) {
        // Si el usuario confirma, navega a la URL de eliminación, pasando el ID como parámetro de ruta
        window.location.href = "/eliminarficha/" + id;
    }
}

// Función para ir a la vista detallada de una ficha
const botonVerFicha = (id) => {
    // Redirige a la URL de la ficha, usando el ID como parámetro de consulta
    window.location.href = "/ficha/?id=" + id;  
}

// Función para ir a la vista de edición de una ficha
const botonEditarFicha = (id) => {
    // Redirige a la URL de edición, usando el ID como parámetro de consulta
    window.location.href = "/editarficha/?id=" + id;  
}

// Función que crea los parámetros del filtro
function aplicarFiltros() {
    // Inicializa la cadena de parámetros de enlace
    let link = "";

    // Obtiene los valores de los elementos de filtro de búsqueda
    const filter = document.getElementById('cbofilter').value;
    const search = document.getElementById('txtsearch').value; // Valor a buscar
    const hidereviewed = document.getElementById('hidereviewed').checked;

    // Si tanto el filtro como el termino de búsqueda están llenos, añade los parámetros 'fs' y 's'.
    if (filter != "" && search != "") {
        link += `?fs=${filter}&s=${search}`;
    }

    // Obtiene los valores para ordenamiento
    const orderBy = document.getElementById('cboorderfilter').value; // Campo por el cual ordenar
    const order = document.getElementById('cboorder').value; // Dirección del orden Ascendente o Descendente

    // Si hay un criterio de ordenamiento, lo añade al enlace
    if (orderBy != "") {
        link += (link ? '&' : '?') + `fo=${orderBy}&o=${order}`;
    }

    // Añade el parámetro para ocultar o mostrar las fichas revisadas
    if (hidereviewed) {link += (link ? '&' : '?') + "rv=y";}
    else {link += (link ? '&' : '?') + "rv=n";}

    // Redirige a la URL recién construida con todos los filtros.
    window.location.href = link;
}

// Función para eliminar todos los filtros aplicados
function borrarFiltros() {
    window.location.href = window.location.pathname;
}

document.getElementById('txtsearch').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { aplicarFiltros(); }
});

