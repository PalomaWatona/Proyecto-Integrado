

function createButton(label, page, disabled = false) {
    // Crea el elemento <button>
    const button = document.createElement('button');
    // Asigna el texto al botón
    button.textContent = label;
    // Si 'disabled' es true, deshabilita el botón
    if (disabled) button.disabled = true;

    button.addEventListener('click', () => {
        // Obtiene los paráaetros de la URL actual
        urlParams = new URLSearchParams(window.location.search)
        // Establece o actualiza el parametro 'page' al número de página deseado
        urlParams.set('page', page);
        // Actualiza la URL de la ventana para navegar a la nueva página
        window.location.search = urlParams.toString();
    });
    return button;
}


function createPagination(idcontainer, t, c, r=1){

    // Convierte el total de páginas a entero
    const totalpages = parseInt(t);
    // Si solo hay 1 página o menos, no renderiza la paginación y sale de la función
    if (totalpages <= 1) return;

    // Convierte la página actual a entero
    const currentpage = parseInt(c);
    // Obtiene el elemento contenedor
    const paginationContainer = document.getElementById(idcontainer);

    // Boton Ir a la primera página (<<)
    if (currentpage != 1) {
        paginationContainer.appendChild(createButton("≪", 1));
    }

    // Boton Página anterior (<)
    if (currentpage > 1) {
        paginationContainer.appendChild(createButton("<", currentpage - 1));
    }

    // Variables para determinar el rango de botones numéricos a mostrar
    const range = r;
    // Calcula el inicio del rango (nunca menor que 1)
    const start = Math.max(1, currentpage - range);
    // Calcula el final del rango (nunca mayor que el total de páginas)
    const end = Math.min(totalpages, currentpage + range);

    // Bucle para crear los botones numéricos dentro del rango calculado
    for (let i = start; i <= end; i++) {
        // Si el indice 'i' es la página actual, crea un campo de entrada (input) en su lugar
        if (i === currentpage) {
            const input = document.createElement('input');
            input.type = "text";
            input.value = currentpage;
            input.style.width = "40px";

            // Limpia caracteres no numéricos mientras se escribe
            input.addEventListener('input', () => {
                input.value = input.value.replace(/\D/g, '');
            });
            
            // Maneja la navegación al presionar la tecla "Enter"
            input.addEventListener('keydown', (e) => {
                if (e.key === "Enter") {
                    const val = parseInt(input.value);
                    // Valida que el valor sea un número válido y esté dentro del rango de páginas

                    if (!isNaN(val) && val >= 1 && val <= totalpages) {
                        // Si es válido, navega a la página ingresada, similar a createButton
                        urlParams = new URLSearchParams(window.location.search)
                        urlParams.set('page', val);
                        window.location.search = urlParams.toString();
                    }
                }
            });
            // Añade el campo de entrada al contenedor
            paginationContainer.appendChild(input);
        } else {
            // Si no es la página actual, crea un botón normal y lo añade al contenedor
            const button = createButton(i, i);
            paginationContainer.appendChild(button);
        }
    }
    // Boton Página siguiente (>)
    if (currentpage < totalpages) {
        paginationContainer.appendChild(createButton(">", currentpage + 1));
    }

    // Boton Ir a la última página (>>)
    if (currentpage != totalpages) {
        paginationContainer.appendChild(createButton("≫", totalpages));
    }

}