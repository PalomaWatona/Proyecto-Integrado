const botonEliminar = (id) => {
    if (window.confirm("¿Está Seguro De Querer Eliminar El Registro?")) {
        window.location.href = "/eliminarficha/" + id;
    }
}

const botonVerFicha = (id) => {
    window.location.href = "/ficha/?id=" + id;  
}

const botonEditarFicha = (id) => {
    window.location.href = "/editarficha/?id=" + id;  
}

function aplicarFiltros() {
    let link = "";
    const filter = document.getElementById('cbofilter').value;
    const search = document.getElementById('txtsearch').value;
    const hidereviewed = document.getElementById('hidereviewed').checked;
    if (filter != "" && search != "") {
        link += `?fs=${filter}&s=${search}`;
    }
    const orderBy = document.getElementById('cboorderfilter').value;
    const order = document.getElementById('cboorder').value;
    if (orderBy != "") {
        link += (link ? '&' : '?') + `fo=${orderBy}&o=${order}`;
    }
    if (hidereviewed) {link += (link ? '&' : '?') + "rv=y";}
    else {link += (link ? '&' : '?') + "rv=n";}
    window.location.href = link;
}

function borrarFiltros() {
    window.location.href = window.location.pathname;
}

document.getElementById('txtsearch').addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { aplicarFiltros(); }
});

